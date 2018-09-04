import os.path
import argparse
import hashlib
import requests
import socket
import threading

from collections import OrderedDict

import parser
import peer
import listener

MY_PORT = 6881


def check_input_file_name(value):
    if not value.endswith('.torrent'):
        raise argparse.ArgumentTypeError('The metafile name should be a .torrent file')
    if not os.access(value, os.R_OK):
        raise argparse.ArgumentError("You don't have access to read the metafile")
    return value


def check_output_location(value):
    if not os.path.isdir(value):
        print('The destination directory is not present, attempting to create it')
        try:
            os.mkdir(value)
            print("Required destination directory is created")
        except:
            print("Failed to create the destination directory")
    return value


def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # Makes a dummy connection to Google's DNS server
    return s.getsockname()[0]  # Gives IP of the interface that is used to connect to the network


class Torrent:
    def __init__(self, file_name, destination):
        self.file_name = file_name
        self.destination = destination
        self.metafile_dict = {}
        self.info_dict = OrderedDict()  # OrderedDict is mandatory to get correct value of info_dict_hash
        self.request_parameters = {}
        self.tracker_response_dict = {}
        self.peer_ips = []
        self.peer_table = {}  # Dictionary with key being peer's ip address and value being 'peer' object
        self.conn_table = {}  # Dictionary with key being 'client_address' and value being 'connection' socket object
        self.ip = get_my_ip()
        self.port = MY_PORT  # Hard coded for the sake of testing
        self.output_files = []
        self.response = None
        self.response_string = ''

        self.metafile = open(file_name, 'r', encoding="ISO-8859-1")
        if self.metafile.read(1) == 'd':
            print("Parsing metafile")
            self.metafile_dict = parser.get_dict(self.metafile)
            print("Parsing metafile complete")
        self.metafile.close()

        self.info_dict = self.metafile_dict['info']
        self.info_dict_hash = hashlib.sha1(parser.bencode_dict(self.info_dict).encode('utf-8')).digest()
        self.peer_id = "piTorrentTestPeer001"
        if len(self.peer_id) > 20:
            self.peer_id = self.peer_id[:20]
        else:
            while len(self.peer_id) != 20:
                self.peer_id += '0'

        self.send_tracker_request()
        if 'peers' in self.tracker_response_dict:
            self.get_peers()
        else:
            print("Tracker returned no peers")
            return

        if self.peer_ips:
            for i in self.peer_ips:
                self.peer_table[i[0]] = peer.Peer(i[0], i[1], self.info_dict_hash, self.peer_id)
            print('Peers dict is', self.peer_table)
        else:
            print("No peers found to start handshake")
            return

        self.create_empty_files()

        self.listener_object = listener.Listener(self.ip, self.port, self.info_dict_hash, self.peer_table,
                                                self.conn_table)
        listen_thread = threading.Thread(target=self.listener_object.listen_for_peers)
        listen_thread.daemon = False  # [TODO] Getting some weird error when made True
        listen_thread.start()

        for address, peer_object in self.peer_table.items():
            peer_object.handshake()

    def create_empty_files(self):
        if 'files' not in self.info_dict:
            # Only single file present
            try:
                file = open(os.path.join(self.destination, self.info_dict['name']), 'w')
                self.output_files.append(file)  # [TODO] Close the files at the end
                print("File created", self.info_dict['name'])
            except:
                print("Failed to create file", os.path.join(self.destination, self.info_dict['name']))
        else:
            # Multiple files present
            if 'name' in self.info_dict:
                # Parent directory specified
                file_path = os.path.join(self.destination, self.info_dict['name'])
                if not os.path.isdir(file_path):
                    try:
                        os.mkdir(file_path)
                        print("Created parent directory", file_path)
                    except:
                        print("Failed to create the parent directory", file_path)
                else:
                    print("Parent directory already present")

            if 'files' in self.info_dict:
                for file_dict in self.info_dict['files']:
                    directory_path = os.path.join(self.destination, *file_dict['path'][:-1])
                    file_path = os.path.join(self.destination, *file_dict['path'])
                    if not os.path.isdir(directory_path):
                        try:
                            os.mkdir(directory_path)
                        except:
                            print("Failed to create directory", directory_path)
                    else:
                        print("Directory already present", directory_path)
                    if not os.path.isfile(file_path):
                        try:
                            file = open(file_path, 'w')
                            self.output_files.append(file)  # [TODO] Close the files at the end
                            print("File created", file_path)
                        except:
                            print("Failed to create file", file_path)
                    else:
                        print("File already present", file_path)
            else:
                print("Incorrect torrent metafile")

    def send_tracker_request(self):
        self.request_parameters['info_hash'] = self.info_dict_hash
        self.request_parameters['peer_id'] = self.peer_id
        self.request_parameters['port'] = self.port
        self.request_parameters['uploaded'] = 0
        self.request_parameters['downloaded'] = 0
        self.request_parameters['left'] = 100  # [TODO] Change this to sum of lengths of files
        self.request_parameters['compact'] = 1
        self.request_parameters['support_crypto'] = 1
        self.request_parameters['event'] = 'started'

        print("Sending a http request to", self.metafile_dict['announce'])  # [TODO] Check for UDP and act accordingly
        self.response = requests.get(self.metafile_dict['announce'], params=self.request_parameters)
        self.response.encoding = 'ISO-8859-1'
        self.response_string = self.response.content.decode('ISO-8859-1')

        self.tracker_response_dict = parser.bdecode_response_string(self.response_string)
        print("Tracker responded with the following details:")
        print(self.tracker_response_dict)

    def get_peers(self):
        peers_list = []
        if isinstance(self.tracker_response_dict['peers'], str):
            for i in self.tracker_response_dict['peers']:
                peers_list.append(str(ord(i)))
            while peers_list:
                ip = '.'.join(peers_list[:4])
                port = int(peers_list[4])*256 + int(peers_list[5])
                if ip != self.ip:
                    self.peer_ips.append((ip, port))
                peers_list = peers_list[6:]

        elif isinstance(self.tracker_response_dict['peers'], list):
            # qBitTorrent's embedded tracker gives peers list using list of ordered dicts
            for i in self.tracker_response_dict['peers']:
                ip = i['ip'][7:]  # ip format is '::ffff:192.168.0.101'
                port = i['port']
                if ip != self.ip:
                    self.peer_ips.append((ip, port))

        else:
            print("Tracker response case not handled")

        print("The list of available peers is:", self.peer_ips)


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('--metafile', help='Name of the .torrent file', nargs=1,
                            type=lambda value: check_input_file_name(value))
    arg_parser.add_argument('--destination', help='Location where the file needs to be downloaded',
                            nargs=1, type=lambda value: check_output_location(value))

    args = arg_parser.parse_args()
    if not args.metafile:
        print("Please specify a metafile using --metafile option")
        return
    if not args.dest:
        print("Please specify a output destination using --destination option")
        return

    torrent_object = Torrent(args.metafile[0], args.dest[0])


if __name__ == '__main__':
    main()
