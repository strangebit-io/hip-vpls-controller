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

# Timing
from time import time
from time import sleep

# Packets
from packets import packets

hip_config = config.config;

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
from dcrypto import digest

# Open sockets that exist
open_sockets = []
open_addresses = []

# HIP controller lock
hip_config_socket_lock = threading.Lock()

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
        timestamp = time();
        print(hexlify(hit))
        print(hexlify(ip))
        print(timestamp);

def send_loop():
    while True:
        for i in range(0, len(open_sockets)):
            sock = open_sockets[i]
            addr = open_addresses[i]
            # Send messages to each HIP switch
        sleep(1)


hip_th_loop = threading.Thread(target = accept_loop, args = (), daemon = True);
hip_th_loop.start();

while True:
    # Maintainance loop
    sleep(1)
