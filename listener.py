import socket
import time


class Listener:
    def __init__(self, ip, port, info_dict_hash, peer_table, conn_table):
        self.ip = ip
        self.port = port
        self.peer_table = peer_table
        self.conn_table = conn_table
        self.info_dict_hash = info_dict_hash
        self.listener = None

    def listen_for_peers(self):
        i = (self.ip, self.port)
        self.listener = socket.socket()
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(i)
        self.listener.listen(5)
        print('Listening on', i)

        while True:
            connection, client_address = self.listener.accept()
            client_address = (client_address[0], self.peer_table[client_address[0]].port)  # This port doesn't matter, so setting it to peer's listen port to avoid confusion
            print("Client address", client_address)
            self.conn_table[client_address] = connection
            for client_address, connection in self.conn_table.items():
                data, anc_data, msg_flags, address = connection.receivedmsg(1024)
                peer_object = self.peer_table[client_address[0]]
                if len(data) == 68:
                    if data[28:48] == peer_object.info_dict_hash:
                        peer_object.handshake_received = 1
                        print("Handshake packet received from", client_address)
                        if peer_object.handshake_sent == 1:
                            peer_object.handshake_made = 1
                            print("Handshake made with peer", client_address)
                    else:
                        print("Info dict hash not matching")
                else:
                    print("Binary message ", data)
            time.sleep(1)
