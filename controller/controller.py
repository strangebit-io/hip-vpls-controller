#!/usr/bin/python3

# Copyright (C) 2019 strangebit

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Dmitriy Kuptsov"
__copyright__ = "Copyright 2024, stangebit"
__license__ = "GPL"
__version__ = "0.0.1a"
__maintainer__ = "Dmitriy Kuptsov"
__email__ = "dmitriy.kuptsov@gmail.com"
__status__ = "development"

# Import config
from config import config
hip_config = config.config;

from database.models import DevicesModel, HashesModel
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

#engine = db.create_engine('mysql://user:pass@host:port/db')

#engine = sa.create_engine(hip_config["database"]["uri"])

connection_url = sa.engine.URL.create(
    drivername=hip_config["database"]["driver"],
    username=hip_config["database"]["username"],
    password=hip_config["database"]["password"],
    host=hip_config["database"]["host"],
    database=hip_config["database"]["database"],
)

engine = sa.create_engine(connection_url)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()

# Threading
import threading 

# Randome 
from os import urandom

# Timing
from time import time
from time import sleep

# utilities
from utils import misc

# Packets
from packets import packets

# Network stuff
import socket
import ssl

# Add current directory to Python path
import sys
import os
sys.path.append(os.getcwd())

# HEX utils
from binascii import hexlify

# Threading
import threading

# Crypto stuff
from ccrypto import digest

# Open sockets that exist
open_sockets = []
open_addresses = []

# HIP controller lock
hip_config_socket_lock = threading.Lock()
db_lock = threading.Lock()

# Configuration parameters
hostname = hip_config["network"]["hostname"];
port = hip_config["network"]["controller_port"];
buffer_size = hip_config["general"]["buffer_size"];
master_secret = bytearray(hip_config["security"]["master_secret"], encoding="ascii");
private = hip_config["security"]["private_ca_key"]
public = hip_config["security"]["public_ca_key"]
backlog = hip_config["network"]["backlog"]

# Create server socket
ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2);
ctx.load_cert_chain(public, private);
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0);
sock.bind((hostname, port));
sock.listen(backlog);
controller_socket = ctx.wrap_socket(sock, server_side=True);

def accept_loop():
    while True:
        print("Accepting socket")
        try:
           sock, addr = controller_socket.accept()
        except:
           pass
        try:
            hip_config_socket_lock.acquire();
            open_sockets.append(sock);
            open_addresses.append(addr);
            read_th_loop = threading.Thread(target = receive_loop, args = (sock, ), daemon = True);
            read_th_loop.start();
        except:
            pass
        finally:
            hip_config_socket_lock.release();

def receive_loop(socket_):
    global db_lock
    buf = bytearray([])
    while True:
        buf += socket_.recv(8000)
        print(buf)
        print(len(buf))
        if len(buf) == 0:
            # Socket was closed
            try:
                # Remove socket from the list
                hip_config_socket_lock.acquire();
                i = 0
                for s in open_sockets:
                    if s == socket_:
                        open_sockets.pop(i);
                        open_addresses.pop(i);
                        break;
                    i += 1
            finally:
                hip_config_socket_lock.release();
            break;
        if len(buf) < packets.HEART_BEAT_PACKET_LENGTH:
            continue;
        print("Slicing")
        # Slice it....
        pbuf = buf[:packets.HEART_BEAT_PACKET_LENGTH]
        buf = buf[packets.HEART_BEAT_PACKET_LENGTH:];
        packet = packets.HeartbeatPacket(pbuf);
        print(pbuf)
        print(packet.get_packet_type())
        print(packet.get_packet_length())
        if packet.get_packet_type() != packets.HEART_BEAT_TYPE:
            # Socket should be closed
            try:
                # Remove socket from the list
                hip_config_socket_lock.acquire();
                i = 0
                for s in open_sockets:
                    if s == socket_:
                        open_sockets.pop(i);
                        open_addresses.pop(i);
                        break;
                    i += 1
            finally:
                hip_config_socket_lock.release();
                socket_.close()
            break;
        print("---------------------")
        print(hexlify(packet.get_buffer()))
        actual_hmac = packet.get_hmac()
        packet.set_hmac(bytearray([0] * 32))
        buf_ = packet.get_buffer()
        print(hexlify(master_secret))
        print("Nonce: " + str(hexlify(packet.get_nonce())))
        print(packet.get_packet_length())
        print("HIT: " + str(hexlify(packet.get_hit())))
        print("IP: " + str(hexlify(packet.get_ip())))
        print("MAC: " + str(hexlify(actual_hmac)))
        print(hexlify(buf_))
        print("---------------------")
        hmac = digest.SHA256HMAC(master_secret)
        computed_hmac = hmac.digest(buf_)
        if computed_hmac != actual_hmac:
            print("Invalid HMAC")
            continue;
        hit = packet.get_hit();
        ip = packet.get_ip();
        timestamp = int(time());
        
        db_lock.acquire()
        device = session.query(DevicesModel).filter_by(hit = misc.Utils.ipv6_bytes_to_hex_formatted(hit), ip = misc.Utils.ipv4_bytes_to_string(ip)).first()
        if not device:
            device = DevicesModel();
            device.hit = misc.Utils.ipv6_bytes_to_hex_formatted(hit)
            device.ip = misc.Utils.ipv4_bytes_to_string(ip)
            device.timestamp = timestamp
            
            session.add(device)
            session.commit();
        else:
            device.timestamp = timestamp
            session.commit();
        db_lock.release()
        print(hexlify(hit))
        print(hexlify(ip))
        print(timestamp);

def send_loop():
    global db_lock
    while True:
        try:
            for i in range(0, len(open_sockets)):
                sock = open_sockets[i]
                addr = open_addresses[i]
                hosts = session.query(DevicesModel).all();
                hosts_ = []
                buf_ = bytearray([])
                length = 0
                num_hosts = 0
                for h in hosts:
                    hosts_.append({
                        "hit": misc.Utils.ipv6_to_bytes(h.hit),
                        "ip": misc.Utils.ipv4_to_bytes(h.ip)
                    })
                    buf_ += misc.Utils.ipv6_to_bytes(h.hit) + misc.Utils.ipv4_to_bytes(h.ip)
                    length += 20
                    num_hosts += 1
                sha = digest.SHA256Digest()
                packet_hash = hexlify(sha.digest(buf_)).decode("ascii")
                print("-------------------------------------------------------")
                db_lock.acquire()
                print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                device = session.query(DevicesModel).filter_by(ip = addr[0]).first()
                hash = session.query(HashesModel).filter_by(device_id = device.id, type = "HOSTS").first()
                
                if not hash:
                    hash = HashesModel()
                    hash.device_id = device.id
                    hash.type = "HOSTS"
                    hash.hash = packet_hash
                    session.add(hash)
                    session.commit()
                else:
                    if packet_hash == hash.hash:
                        db_lock.release()
                        continue
                    else:
                        hash.hash = packet_hash
                        session.commit()
                db_lock.release()
                packet = packets.HostsConfigurationPacket()
                packet.set_nonce(urandom(4))
                print("111111111111111111111111")
                packet.set_hosts(hosts_, num_hosts)
                print("222222222222222222222222")
                packet.set_packet_type(packets.HOSTS_CONFIGURATION_TYPE)
                print("333333333333333333333333")
                packet.set_packet_length(packets.BASIC_HEADER_OFFSET + length)
                print("444444444444444444444444")
                buf_ = packet.get_buffer()
                hmac = digest.SHA256HMAC(master_secret)
                computed_hmac = hmac.digest(buf_)
                print("555555555555555555555555")
                packet.set_hmac(computed_hmac)
                print("-------------------- Sending configuration packets to the host ------------------");
                send_bytes = sock.send(packet.get_buffer())
                print("SENT %d BYTES TO SWITCH" % send_bytes)
                # Send messages to each HIP switch
        except Exception as e:
            print(e)
            pass
        sleep(1)


hip_th_loop = threading.Thread(target = accept_loop, args = (), daemon = True);
hip_th_loop.start();

send_loop();

