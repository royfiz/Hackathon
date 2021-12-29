import socket
import struct
import time
from threading import Thread
from scapy.arch import get_if_addr
import random


class client:

    def __init__(self, team_name):
        self.port_udp = 13107
        self.mode = False
        self.team_name = team_name
        self.socket_tcpclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def udp_listner(self):
        while True:
            print("Client started, listening for offer requests...")
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.bind(('', self.port_udp))
            msg, server_address = udp_socket.recvfrom(1024)
            print("Received offer from " + str(server_address[0]) + " attempting to connect...")
            msg_unpacked = struct.unpack("Ibh", msg)
            if hex(msg_unpacked[0]) == hex(0xabcddcba) and hex(msg_unpacked[1]) == hex(0x2):
                self.tcp_connect(server_address[0], msg_unpacked[2])
                self.game_start()
                break

    def tcp_connect(self, server_ip, tcp_server_port):

        self.socket_tcpclient.connect((server_ip, tcp_server_port))
        team = self.team_name + "\n"
        self.socket_tcpclient.sendall(team.encode("utf-8"))

    def game_start(self):
        sm = self.socket_tcpclient.recv(1024)
        smd = sm.decode("utf-8")
        print(smd)
        self.mode = True
        res = str(input()) + " " + self.team_name
        self.socket_tcpclient.sendall(res.encode("utf-8"))

    def server_listner(self):
        while True:
            end_message = self.socket_tcpclient.recv(1024)
            if end_message.decode("utf-8") == "Game Over" or len(end_message.decode("utf-8")) == 0:
                self.mode = False
                break
        summary_message = self.socket_tcpclient.recv(1024)
        summary_message_decoded = summary_message.decode("utf-8")
        msg_to_print = ""
        for msg_char in summary_message_decoded:
            if msg_char == " " or msg_char == "\n":
                msg_to_print += msg_char
            else:
                msg_to_print += msg_char
        print(msg_to_print)


team_name = "harsim2"
client = client(team_name)
client.udp_listner()