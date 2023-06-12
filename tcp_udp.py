
"""MapReduce framework Worker node."""
import os
import tempfile
import logging
import json
import time
import threading
import socket
import subprocess
import hashlib
import pathlib
import heapq
import contextlib


def TCP_server(signals, port, host, handle_message):
    """Wait on a message from a socket OR a shutdown signal."""
    # print("TCP_server() starting")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen()

        while not signals["shutdown"]:
            # print("waiting ...")

            try:
                clientsocket, address = sock.accept()
            except socket.timeout:
                continue
            # print("Connection from", address[0])

            clientsocket.settimeout(1)

            with clientsocket:
                message_chunks = []
                while True:
                    try:
                        data = clientsocket.recv(4096)
                    except socket.timeout:
                        continue
                    if not data:
                        break
                    message_chunks.append(data)

            # Decode list-of-byte-strings to UTF8 and parse JSON data
            message_bytes = b''.join(message_chunks)
            message_str = message_bytes.decode("utf-8")

            try:
                message_dict = json.loads(message_str)
                handle_message(message_dict, signals)
            except json.JSONDecodeError:
                continue
            # print("WORKER MESSAGE{")
            print(message_dict)
            # print("}")
            handle_message(message_dict)

    print("TCP_server() shutting down")


def TCP_client(message, port, host):
    """Test TCP Socket Client."""
    # create an INET, STREAMing socket, this is TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

        # connect to the server
        sock.connect((host, port))

        # send a message
        # message = json.dumps({"hello": "world"})
        sock.sendall(message.encode('utf-8'))


def UDP_server():
    """Test UDP Socket Server."""
    # Create an INET, DGRAM socket, this is UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        # Bind the UDP socket to the server
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("localhost", 8001))
        sock.settimeout(1)

        while True:
            try:
                message_bytes = sock.recv(4096)
            except socket.timeout:
                continue
            message_str = message_bytes.decode("utf-8")
            message_dict = json.loads(message_str)
            print(message_dict)


def UDP_client(signals, manager_port, manager_host, port, host):
    """Test UDP Socket Client."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Connect to the UDP socket on server
        sock.connect((manager_host, manager_port))

        # while not signals["acknowledged"]:
        #     time.sleep(.1)
        while not signals["shutdown"]:
            if signals["acknowledged"]:
                message = json.dumps({
                    "message_type": "heartbeat",
                    "worker_host": host,
                    "worker_port": port
                })
                # print(signals["acknowledged"])
                sock.sendall(message.encode('utf-8'))
                time.sleep(2)