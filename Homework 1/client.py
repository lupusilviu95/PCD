#!/usr/bin/python3.5

import click
import socket
import threading
import time

IP = "127.0.0.1"
PROTOCOL_TO_PORT = {
    "TCP": 1080,
    "UDP": 1081
}


class UDPClient(object):
    def __init__(self, host, port, file, size, streaming):
        self.host = host
        self.port = port
        self.file = file
        self.size = size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.communication_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.communication_socket.bind((self.host, self.port + 2))
        self.communication_socket.settimeout(3)
        self.send_file = self._send_file if streaming else self._sw_send_file

    def _sw_send_file(self):
        self.file.seek(0)
        start = time.time()
        bytes_written = 0
        count = 0
        while True:
            data = self.file.read(self.size)
            if not data:
                print("Finished transmitting file")

                self.socket.sendto(data, (self.host, self.port))

                self.socket.close()
                print("Closing connection to client")
                break
            count += 1
            print("Sent  {}".format(len(data)))
            self.socket.sendto(data, (self.host, self.port))
            bytes_written += len(data)
            print("Waiting for confirmation on packet {}".format(count))
            ack = -1
            while ack != count:
                try:
                    data, _ = self.communication_socket.recvfrom(self.size)
                    ack = int.from_bytes(data, byteorder='big')
                except socket.timeout:
                    print("* Socket timed out, sending data again")
                    self.socket.sendto(data, (self.host, self.port))

            print("Confirmation data received: {}".format(int.from_bytes(data, byteorder='big')))
        stop = time.time()
        print("It took {} seconds".format(stop-start))
        print("Sent {} chunks".format(count))
        print("Sent {} bytes".format(bytes_written))

    def _send_file(self):
        self.file.seek(0)
        count = 0
        start = time.time()
        bytes_written = 0
        while True:
            data = self.file.read(self.size)

            print("Sent  {} bytes".format(len(data)))

            if not data:
                print("Finished transmitting file")
                self.socket.sendto(data, (self.host, self.port))
                self.socket.close()
                print("Closing connection to client")
                break
            count += 1
            self.socket.sendto(data, (self.host, self.port))
            bytes_written += len(data)
        stop = time.time()
        print("It took {} seconds".format(stop-start))
        print("Sent {} chunks".format(count))
        print("Sent {} bytes".format(bytes_written))



class TCPClient(object):
    def __init__(self, host, port, file, size, streaming):
        self.host = host
        self.port = port
        self.file = file
        self.size = size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_file = self._send_file if streaming else self._sw_send_file

    def _send_file(self):
        self.socket.connect((self.host, self.port))
        self.file.seek(0)
        start = time.time()
        bytes_written = 0
        count = 0
        while True:
            data = self.file.read(self.size)
            if not data:
                print("Finished transmitting file")
                self.socket.close()
                print("Closing connection to client")
                break
            self.socket.send(data)
            bytes_written += len(data)
            count += 1
            print("Sent  {} bytes".format(len(data)))
        stop = time.time()
        print("It took {} seconds".format(stop-start))
        print("Sent {} chunks".format(count))
        print("Sent {} bytes".format(bytes_written))


    def _sw_send_file(self):
        self.socket.connect((self.host, self.port))
        self.file.seek(0)
        count = 0
        start = time.time()
        bytes_written = 0
        while True:
            data = self.file.read(self.size)
            if not data:
                print("Finished transmitting file")
                self.socket.close()
                print("Closing connection to client")
                break
            count += 1
            self.socket.send(data)
            bytes_written += len(data)
            print("Sent  {} bytes".format(len(data)))
            print("Waiting for confirmation on packet {}".format(count))
            ack = -1
            while ack != count:
                try:
                    data = self.socket.recv(self.size)
                    ack = int.from_bytes(data, byteorder='big')
                except socket.timeout:
                    print("**************Socket timed out, sending data again")
                    self.socket.send(data)

            print("Confirmation data received: {}".format(int.from_bytes(data, byteorder='big')))
        stop = time.time()
        print("It took {} seconds".format(stop-start))
        print("Sent {} chunks".format(count))
        print("Sent {} bytes".format(bytes_written))


@click.command()
@click.option("--protocol", "-p", type=click.Choice(["TCP", "UDP"]), default="TCP")
@click.option("--streaming/--stop-wait", default=True)
@click.option("--message-size", "-s", type=click.IntRange(1, 65535), default=2048)
@click.option("--file", "-f", type=click.File("rb"), required=True)
def cli(protocol, streaming, message_size, file):
    # tcp(protocol, message_size)
    if protocol == "UDP":
        print("Client starting in UDP mode")
        UDPClient(IP, PROTOCOL_TO_PORT.get(protocol), file, message_size, streaming).send_file()
    else:
        print("Client starting in TCP mode")
        TCPClient(IP, PROTOCOL_TO_PORT.get(protocol), file, message_size, streaming).send_file()


if __name__ == "__main__":
    cli()
