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
__copyright__ = "Copyright 2024, strangebit"
__license__ = "GPL"
__version__ = "0.0.1a"
__maintainer__ = "Dmitriy Kuptsov"
__email__ = "dmitriy.kuptsov@gmail.com"
__status__ = "development"

# Import config
from config import config
hip_config = config.config;

import sys
#Logging stuff
import logging

# Configure logging to console and file
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("hipls-controller.log"),
        logging.StreamHandler(sys.stdout)
    ]
);


from database.models import DevicesModel, HashesModel, MeshModel, FirewallModel, ACLModel
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

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
    session = Session()
    while True:
        
        buf += socket_.recv(8000)
        logging.debug(buf)
        logging.debug(len(buf))
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
        logging.debug("Slicing")
        # Slice it....
        packet = packets.HeartbeatPacket(buf);
        hostname_length = packet.get_hostname_length()
        pbuf = buf[:packets.HEART_BEAT_PACKET_LENGTH + hostname_length]
        buf = buf[packets.HEART_BEAT_PACKET_LENGTH + hostname_length:];
        packet = packets.HeartbeatPacket(pbuf);

        logging.debug(pbuf)
        logging.debug(packet.get_packet_type())
        logging.debug(packet.get_packet_length())
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
        logging.debug("---------------------")
        logging.debug(hexlify(packet.get_buffer()))
        actual_hmac = packet.get_hmac()
        packet.set_hmac(bytearray([0] * 32))
        buf_ = packet.get_buffer()
        logging.debug(hexlify(master_secret))
        logging.debug("Nonce: " + str(hexlify(packet.get_nonce())))
        logging.debug(packet.get_packet_length())
        logging.debug("HIT: " + str(hexlify(packet.get_hit())))
        logging.debug("IP: " + str(hexlify(packet.get_ip())))
        logging.debug("MAC: " + str(hexlify(actual_hmac)))
        logging.debug("HOSTNAME : " + str(packet.get_hostname().decode("ascii")))
        
        logging.debug(hexlify(buf_))
        logging.debug("---------------------")
        hmac = digest.SHA256HMAC(master_secret)
        computed_hmac = hmac.digest(buf_)
        if computed_hmac != actual_hmac:
            print("Invalid HMAC")
            continue;
        hit = packet.get_hit();
        ip = packet.get_ip();
        timestamp = int(time());
        switchname = packet.get_hostname().decode("ascii")
        
        #db_lock.acquire()
        
        try:
            device = session.query(DevicesModel).filter_by(hit = misc.Utils.ipv6_bytes_to_hex_formatted(hit), ip = misc.Utils.ipv4_bytes_to_string(ip)).first()
            if not device:
                device = DevicesModel();
                device.hit = misc.Utils.ipv6_bytes_to_hex_formatted(hit)
                device.ip = misc.Utils.ipv4_bytes_to_string(ip)
                device.name = switchname
                device.timestamp = timestamp
                
                session.add(device)
                session.commit();
            else:
                device.timestamp = timestamp
                device.name = switchname
                session.commit();
        except:
            session.rollback()
        finally:
            pass
        #db_lock.release()
        logging.debug(hexlify(hit))
        logging.debug(hexlify(ip))
        logging.debug(timestamp);
    session.close()

def send_loop():

    global db_lock
    
    while True:
        session = Session()
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
                #mesh = session.query(MeshModel).all()
                #mesh_ = []
                
                sha = digest.SHA256Digest()
                packet_hash = hexlify(sha.digest(buf_)).decode("ascii")
                logging.debug("SENDING PACKET FOR THE HOST:")
                logging.debug(addr[0])

                logging.debug("-------------------------------------------------------")
                #db_lock.acquire()
                logging.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                device = session.query(DevicesModel).filter_by(ip = addr[0]).first()
                hash = session.query(HashesModel).filter_by(device_id = device.id, type = "HOSTS").first()
                send_update = True
                if not hash:
                    hash = HashesModel()
                    hash.device_id = device.id
                    hash.type = "HOSTS"
                    hash.hash = packet_hash
                    session.add(hash)
                    session.commit()
                else:
                    if packet_hash == hash.hash:
                        #db_lock.release()
                        send_update = False
                    else:
                        hash.hash = packet_hash
                        session.commit()
                #db_lock.release()
                if send_update:
                    packet = packets.HostsConfigurationPacket()
                    packet.set_nonce(urandom(4))
                    logging.debug(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    logging.debug("Buffer length %d" % (len(packet.get_buffer())))
                    logging.debug("")
                    packet.set_hosts(hosts_, num_hosts)
                    logging.debug("NUM HOSTS %d" % (num_hosts))
                    packet.set_packet_type(packets.HOSTS_CONFIGURATION_TYPE)
                    packet.set_packet_length(packets.BASIC_HEADER_OFFSET + length + packets.HOSTS_CONFIGURATION_NUM_LENGTH)
                    buf_ = packet.get_buffer()
                    logging.debug("-------------------- 000000 ------------------");
                    logging.debug("Buffer length %d" % (len(packet.get_buffer())))
                    hmac = digest.SHA256HMAC(master_secret)
                    computed_hmac = hmac.digest(buf_)
                    packet.set_hmac(computed_hmac)
                    logging.debug("-------------------- Sending configuration packets to the host ------------------");
                    logging.debug("Buffer length %d" % (len(packet.get_buffer())))
                    send_bytes = sock.send(packet.get_buffer())
                    logging.debug("SENT %d BYTES TO SWITCH" % send_bytes)
                    logging.debug(addr[0])

                send_update = True
                mesh = session.query(MeshModel).all()
                logging.debug("++++++++++++++ MESH ++++++++++++++")
                logging.debug(mesh)
                mesh_ = []
                buf_ = bytearray([])
                length = 0
                num_hosts = 0
                device = session.query(DevicesModel).filter_by(ip = addr[0]).first()
                for m in mesh:
                    logging.debug("^^^^^^^^^^^^^^^^^^ FOUND MESH CONFIGURATION ^^^^^^^^^^^^^^^^^^")
                    device1 = session.query(DevicesModel).filter_by(id = m.device_1_id).first()
                    device2 = session.query(DevicesModel).filter_by(id = m.device_2_id).first()
                    if not device1 or not device2:
                        continue
                    if device2.hit == device.hit:
                        # Skip the record for itself
                        continue
                    if device1.hit != device.hit:
                        continue
                    mesh_.append({
                        "hit1": misc.Utils.ipv6_to_bytes(device1.hit),
                        "hit2": misc.Utils.ipv6_to_bytes(device2.hit)
                    })
                    logging.debug("____________ " + addr[0] + "___________________")
                    logging.debug("______________________________")
                    logging.debug(device1.hit)
                    logging.debug(device2.hit)
                    logging.debug("______________________________")

                    buf_ += misc.Utils.ipv6_to_bytes(device1.hit) + misc.Utils.ipv6_to_bytes(device2.hit)
                    length += 32
                    num_hosts += 1
                
                if num_hosts >= 0:
                    sha = digest.SHA256Digest()
                    packet_hash = hexlify(sha.digest(buf_)).decode("ascii")
                    logging.debug("-------------------------------------------------------")
                    #db_lock.acquire()
                    logging.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    device = session.query(DevicesModel).filter_by(ip = addr[0]).first()
                    hash = session.query(HashesModel).filter_by(device_id = device.id, type = "MESH").first()
                    
                    if not hash:
                        hash = HashesModel()
                        hash.device_id = device.id
                        hash.type = "MESH"
                        hash.hash = packet_hash
                        session.add(hash)
                        session.commit()
                    else:
                        if packet_hash == hash.hash:
                            #db_lock.release()
                            send_update = False
                        else:
                            hash.hash = packet_hash
                            session.commit()
                    #db_lock.release()
                    if send_update: 
                        packet = packets.MeshConfigurationPacket()
                        packet.set_nonce(urandom(4))
                        packet.set_mesh(mesh_, num_hosts)
                        packet.set_packet_type(packets.MESH_CONFIGURATION_TYPE)
                        packet.set_packet_length(packets.BASIC_HEADER_OFFSET + length + packets.MESH_CONFIGURATION_NUM_LENGTH)
                        buf_ = packet.get_buffer()
                        logging.debug("-------------- MESH BUFFER --------------")
                        logging.debug(buf_)
                        logging.debug(hexlify(packet.get_nonce()))
                        hmac = digest.SHA256HMAC(master_secret)
                        computed_hmac = hmac.digest(buf_)
                        packet.set_hmac(computed_hmac)
                        logging.debug("-------------------- Sending MESH***** configuration packets to the host ------------------");
                        send_bytes = sock.send(packet.get_buffer())
                        logging.debug("SENT %d BYTES TO SWITCH %s" % (send_bytes, addr[0]))
                firewall = session.query(FirewallModel).all()
                firewall_ = []
                buf_ = bytearray([])
                length = 0
                num_hosts = 0
                send_update = True
                logging.debug("NUMBER OF FIRWALL RULES %d " % len(firewall))
                for m in firewall:
                    
                    device1 = session.query(DevicesModel).filter_by(id = m.device_1_id).first()
                    device2 = session.query(DevicesModel).filter_by(id = m.device_2_id).first()
                    if not device1 or not device2:
                        continue
                    rule = 0
                    if m.rule == "allow":
                        rule = 1
                    firewall_.append({
                        "hit1": misc.Utils.ipv6_to_bytes(device1.hit),
                        "hit2": misc.Utils.ipv6_to_bytes(device2.hit),
                        "rule": rule
                    })
                    buf_ += misc.Utils.ipv6_to_bytes(device1.hit) + misc.Utils.ipv6_to_bytes(device2.hit) + misc.Utils.int_to_bytes(rule)
                    length += 36
                    num_hosts += 1
                
                if num_hosts >= 0:
                    sha = digest.SHA256Digest()
                    packet_hash = hexlify(sha.digest(buf_)).decode("ascii")
                    logging.debug("-------------------------------------------------------")
                    #db_lock.acquire()
                    logging.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    device = session.query(DevicesModel).filter_by(ip = addr[0]).first()
                    hash = session.query(HashesModel).filter_by(device_id = device.id, type = "FIREWALL").first()
                    
                    if not hash:
                        hash = HashesModel()
                        hash.device_id = device.id
                        hash.type = "FIREWALL"
                        hash.hash = packet_hash
                        session.add(hash)
                        session.commit()
                    else:
                        if packet_hash == hash.hash:
                            #db_lock.release()
                            send_update = False
                        else:
                            hash.hash = packet_hash
                            session.commit()
                    #db_lock.release()
                    if send_update:
                        packet = packets.FirewallConfigurationPacket()
                        packet.set_nonce(urandom(4))
                        packet.set_rules(firewall_, num_hosts)
                        packet.set_packet_type(packets.FIREWALL_CONFIGURATION_TYPE)
                        packet.set_packet_length(packets.BASIC_HEADER_OFFSET + length + packets.FIREWALL_CONFIGURATION_NUM_LENGTH)
                        buf_ = packet.get_buffer()
                        hmac = digest.SHA256HMAC(master_secret)
                        computed_hmac = hmac.digest(buf_)
                        packet.set_hmac(computed_hmac)
                        logging.debug("-------------------- Sending [[[[[[ FIREWALL ]]]]]configuration packets to the host %s ------------------ " % (addr[0]));
                        send_bytes = sock.send(packet.get_buffer())
                        logging.debug("SENT %d BYTES TO SWITCH" % send_bytes)
                
                device = session.query(DevicesModel).filter_by(ip = addr[0]).first()
                acl = session.query(ACLModel).filter_by(device_id = device.id).all()
                acl_ = []
                buf_ = bytearray([])
                length = 0
                num_hosts = 0
                send_update = True
                logging.debug("NUMBER OF ACL RULES %d " % len(acl))
                for a in acl:
                    
                    rule = 0
                    if a.rule == "allow":
                        rule = 1
                    acl_.append({
                        "mac1": misc.Utils.mac_to_bytes(a.mac1),
                        "mac2": misc.Utils.mac_to_bytes(a.mac2),
                        "rule": rule
                    })
                    buf_ += misc.Utils.mac_to_bytes(a.mac1) + misc.Utils.mac_to_bytes(a.mac2) + misc.Utils.int_to_bytes(rule)
                    length += 16
                    num_hosts += 1
                
                if num_hosts >= 0:
                    sha = digest.SHA256Digest()
                    packet_hash = hexlify(sha.digest(buf_)).decode("ascii")
                    logging.debug("-------------------------------------------------------")
                    #db_lock.acquire()
                    logging.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                    device = session.query(DevicesModel).filter_by(ip = addr[0]).first()
                    hash = session.query(HashesModel).filter_by(device_id = device.id, type = "ACL").first()
                    
                    if not hash:
                        hash = HashesModel()
                        hash.device_id = device.id
                        hash.type = "ACL"
                        hash.hash = packet_hash
                        session.add(hash)
                        session.commit()
                    else:
                        if packet_hash == hash.hash:
                            #db_lock.release()
                            send_update = False
                        else:
                            hash.hash = packet_hash
                            session.commit()
                    #db_lock.release()
                    if send_update:
                        packet = packets.ACLConfigurationPacket()
                        packet.set_nonce(urandom(4))
                        packet.set_rules(acl_, num_hosts)
                        packet.set_packet_type(packets.ACL_CONFIGURATION_TYPE)
                        packet.set_packet_length(packets.BASIC_HEADER_OFFSET + length + packets.ACL_CONFIGURATION_NUM_LENGTH)
                        buf_ = packet.get_buffer()
                        hmac = digest.SHA256HMAC(master_secret)
                        computed_hmac = hmac.digest(buf_)
                        packet.set_hmac(computed_hmac)
                        logging.debug("-------------------- Sending [[[[[[ ACL ]]]]]configuration packets to the host %s ------------------ " % (addr[0]));
                        send_bytes = sock.send(packet.get_buffer())
                        logging.debug("SENT %d BYTES TO SWITCH" % send_bytes)
        
                # Send messages to each HIP switch
        except Exception as e:
            logging.debug(e)
            session.rollback()
        sleep(1)
        session.close()


hip_th_loop = threading.Thread(target = accept_loop, args = (), daemon = True);
hip_th_loop.start();

send_loop();

