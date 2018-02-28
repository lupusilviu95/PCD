#!/usr/bin/python3.5

import socket
import threading

import click

IP = "127.0.0.1"
PROTOCOL_TO_PORT = {
    "TCP": 1080,
    "UDP": 1081
}


class UDPServer(object):
    def __init__(self, host, port, size, streaming):
        print(streaming)
        self.host = host
        self.port = port
        self.size = size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.recv_file = self._recv_file if streaming else self._sw_recv_file

    def _sw_recv_file(self):
        count = 0
        bytes_read = 0
        with open("udp.pdf", "wb") as out:
            try:
                _data = None
                while True:
                    data, address = self.sock.recvfrom(self.size)
                    bytes_read += len(data)
                    if data != _data:
                        print("Received {} bytes".format(len(data)))
                        _data = data
                        count += 1
                    ip, port = address
                    self.sock.sendto(bytes([count]), (ip, self.port + 2))
                    print("Confirming chunk {}".format(count))
                    out.write(data)
                    if not data:
                        print("Done!")
                        break
            except:
                print("Something went wrong")
                print("Received {} messages".format(count))
        print("Received {} chunks".format(count))
        print("Received {} bytes".format(bytes_read))

    def _recv_file(self):
        count = 0
        bytes_read = 0

        with open("udp.pdf", "wb") as out:
            try:
                while True:
                    data, address = self.sock.recvfrom(self.size)
                    bytes_read += len(data)
                    count += 1
                    print("Received {} bytes".format(len(data)))
                    out.write(data)
                    if not data:
                        print("Done!")
                        break
            except:
                print("Something went wrong")
                print("Received {} messages".format(count))
        print("Received {} chunks".format(count))
        print("Received {} bytes".format(bytes_read))



class TCPServer(object):
    def __init__(self, host, port, size, streaming):
        self.host = host
        self.port = port
        self.size = size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.recv_file = self._recv_file if streaming else self._sw_recv_file

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            print("Client connected!")
            client.settimeout(60)
            threading.Thread(target=self.recv_file, args=(client, address)).start()

    def _recv_file(self, client, address):
        count = 0
        bytes_read = 0
        with open("tcp.pdf", "wb") as out:
            try:
                while True:
                    data = client.recv(self.size)
                    count += 1
                    bytes_read += len(data)
                    print("Received {} bytes".format(len(data)))
                    out.write(data)
                    if not data:
                        print("Done!")
                        break
            except:
                print("SMTH happened")
        print("Received {} chunks".format(count))
        print("Received {} bytes".format(bytes_read))

    def _sw_recv_file(self, client, address):
        count = 0
        _data = None
        bytes_read = 0

        with open("tcp.pdf", "wb") as out:
            try:
                while True:
                    data = client.recv(self.size)
                    bytes_read += len(data)
                    if data != _data:
                        print("Received {} bytes".format(len(data)))
                        _data = data
                        count += 1
                    client.send(bytes([count]))
                    print("Confirming chunk {}".format(count))
                    out.write(data)
                    if not data:
                        print("Done!")
                        break
            except:
                raise
                print("SMTH happened")
        print("Received {} chunks".format(count))
        print("Received {} bytes".format(bytes_read))


@click.command()
@click.option("--protocol", "-p", type=click.Choice(["TCP", "UDP"]), default="TCP")
@click.option("--streaming/--stop-wait", default=True)
@click.option("--message-size", "-s", type=click.IntRange(1, 65535), default=2048)
def cli(protocol, streaming, message_size):
    if protocol == "UDP":
        print("Server starting in UDP mode")
        UDPServer('localhost', PROTOCOL_TO_PORT.get(protocol), message_size, streaming).recv_file()
    else:
        print("Server starting in TCP mode")
        TCPServer('localhost', PROTOCOL_TO_PORT.get(protocol), message_size, streaming).listen()


if __name__ == "__main__":
    cli()
