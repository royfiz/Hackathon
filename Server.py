import socket
import struct
from threading import Thread
import threading
import time
import random
from scapy.arch import get_if_addr


class server:

    def _init_(self, eth_num):
        self.BROADCAST_IP = '172.1.255.255'
        self.udp_port = 13107
        self.tcp_port = 2133
        self.game_mode = False
        self.CONNECTIONS_DICT = {}
        self.IP_ADDRESS = get_if_addr("eth1")
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.random_group_num = 0  # classify the client team to groups 1/2 randomly.
        self.server_socket_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_socket_tcp.bind((self.IP_ADDRESS, self.tcp_port))

    def run_udp(self):

        end_time = time.time() + 10
        broadcast_message = struct.pack('Ibh', 0xabcddcba, 0x2, self.tcp_port)
        while time.time() < end_time:
            self.server_socket_udp.sendto(broadcast_message, (self.BROADCAST_IP, self.udp_port))
            time.sleep(1)
        self.game_mode = True

    def run_tcp(self):

        self.random_group_num = random.randint(1, 2)
        print("Server started, listening on IP address " + str(self.IP_ADDRESS))
        self.server_socket_tcp.settimeout(0.5)
        self.server_socket_tcp.listen()
        while not self.game_mode:
            try:
                connection_socket, client_address = self.server_socket_tcp.accept()
                team_name = connection_socket.recv(1024)
            except:
                continue

            team_name = team_name.decode("utf-8")
            self.random_casting_to_group(connection_socket, team_name, self.random_group_num)
            if self.random_group_num == 1:
                self.random_group_num = 2
            else:
                self.random_group_num = 1
            if (len(self.CONNECTIONS_DICT) == 2):
                self.game_mode = True
                start_message = "Welcome to Quick Maths.\nPlayer 1: " + self.get_teams_name(
                    1) + "\nPlayer 2: " + self.get_teams_name(
                    2) + "\nPlease answer the following question as fast as you can: "
                num1 = random.randint(0, 5)
                num2 = random.randint(0, 4)
                result = num1 + num2
                start_message += "How much is {0}+{1}?".format(num1, num2)
                for conn in self.CONNECTIONS_DICT.keys():
                    conn.sendall(start_message.encode("utf-8"))
                while True:
                    reply = self.server_socket_tcp.recv(4096)
                    if reply:
                        if (reply[0] == result):
                            msg = reply[2:] + " is the winner"
                            conn.sendall(msg.encode("utf-8"))
                            break
                    time.sleep(0.5)


            else:
                self.game_mode = False

    def send_game_over_message(self):

        for conn in self.CONNECTIONS_DICT.keys():
            conn.sendall("Game Over".encode("utf-8"))

    def random_casting_to_group(self, connection_socket, team_name, group_num):

        score = 0
        self.CONNECTIONS_DICT[connection_socket] = [team_name, group_num, score]

    def get_teams_name(self, group_num):
        names_in_group = ""
        for lst in self.CONNECTIONS_DICT.values():
            if lst[1] == group_num:
                names_in_group += lst[0]
        return names_in_group

    def run_server(self):
        while True:
            udp_thread = Thread(target=self.run_udp)
            tcp_thread = Thread(target=self.run_tcp)
            udp_thread.start()
            tcp_thread.start()
            udp_thread.join()
            tcp_thread.join()
            time.sleep(3)


eth_num = 1
server = server(eth_num)
server.run_server()