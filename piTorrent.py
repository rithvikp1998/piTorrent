import os.path
import argparse
import hashlib
import requests
import time
import socket
import threading

from collections import OrderedDict

import parser
import peer

MY_IP = '192.168.0.101'
MY_PORT = 6881
MY_PUBLIC_IP = '14.139.38.173'

def check_input_file_name(value):
	if not value.endswith('.torrent'):
		raise argparse.ArgumentTypeError('The metafile name should be a .torrent file')
	if not os.access(value, os.R_OK):
		raise argparse.ArgumentError("You don't have access to read the metafile")
	return value

def check_output_location(value):
	if not os.path.isdir(value):
		raise argparse.ArgumentTypeError('The destination should be a valid directory')
	if not os.access(value, os.W_OK):
		raise argparse.ArgumentError("You don't have access to write to the destination")
	return value

class torrent:

	def __init__(self, file_name):
		self.file_name = file_name
		self.metafile_dict = {}
		self.info_dict = OrderedDict() # OrderedDict is mandatory to get correct value of info_dict_hash
		self.request_parameters = {}
		self.tracker_response_dict = {}
		self.peer_ips = []
		self.peers = {} # Dictionary with key being 'client_address' and value being 'peer' object
		self.peer_table = {} # Dictionary with key being 'client_address' and value being 'connection' socket object
		self.ip = MY_IP # Hard coded for the sake of testing
		self.port = MY_PORT # Hard coded for the sake of testing

		self.metafile = open(file_name, 'r', encoding = "ISO-8859-1")
		if self.metafile.read(1)=='d':
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
			while len(self.peer_id)!=20:
				self.peer_id += '0'
		
		self.send_tracker_request()
		if 'peers' in self.tracker_response_dict:
			self.get_peers()
		else:
			print("Tracker returned no peers")
			return

		if self.peer_ips:
			for i in self.peer_ips:
				self.peers[(i[0], i[1])] = peer.peer(i[0], i[1], self.info_dict_hash, self.peer_id)
				print('Peers dict key value is', (i[0], i[1]))
		else:
			print("No peers found to start handshake")
			return

		listen_thread = threading.Thread(target=self.listen_for_peers)
		listen_thread.daemon = False #[TODO] Getting some weird error when made True
		listen_thread.start()

		for address, peer_object in self.peers.items():
			peer_object.handshake()

	def send_tracker_request(self):
		self.request_parameters['info_hash'] = self.info_dict_hash
		self.request_parameters['peer_id'] = self.peer_id
		self.request_parameters['port'] = self.port
		self.request_parameters['uploaded'] = 0
		self.request_parameters['downloaded'] = 0
		self.request_parameters['left'] = 100 # [TODO] Change this to sum of lengths of files
		self.request_parameters['compact'] = 1
		self.request_parameters['supportcrypto'] = 1
		self.request_parameters['event'] = 'started'

		print("Sending a http request to", self.metafile_dict['announce']) # [TODO] Check for UDP and act accordingly
		self.response = requests.get(self.metafile_dict['announce'], params=self.request_parameters)
		self.response.encoding = 'ISO-8859-1'
		self.response_string = self.response.content.decode('ISO-8859-1')
		
		self.tracker_response_dict = parser.bdecode_response_string(self.response_string)
		print("Tracker responded with the following details:")
		print(self.tracker_response_dict)

	def get_peers(self):
		peers_list = []
		for i in self.tracker_response_dict['peers']:
			peers_list.append(str(ord(i)))
		while peers_list:
			ip=''
			port=''
			ip = '.'.join(peers_list[:4])
			port = int(peers_list[4])*256 + int(peers_list[5])
			if ip != MY_PUBLIC_IP or port != self.port:
				self.peer_ips.append((ip, port))
			peers_list=peers_list[6:]

		print("The list of available peers is:", self.peer_ips)

	def listen_for_peers(self):
		i = (MY_IP, MY_PORT)
		self.listener = socket.socket()	
		self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.listener.bind(i)
		self.listener.listen(5)
		print('Listening on', i)

		while True:
			connection, client_address = self.listener.accept()
			print("Client address", client_address)
			self.peer_table[client_address] = connection
			for client_address, connection in self.peer_table.items():
				data, ancdata, msg_flags, address = connection.recvmsg(1024)
				peer_object = self.peers[client_address] # FIx conflicts b/w getting '192.168.x.x' and MY_PUBLIC_IP
				if len(data)==68:
					if self.data[28:48] == peer_object.info_dict_hash:
						peer_object.handshake_recv = 1
					if (peer_object.handshake_sent & peer_object.handshake_recv):
						peer_object.handshake_made = 1
						print("Handshake made with peer", client_address)
					else:
						peer_object.handshake()
				else:
					print("Binary message ", data)
			time.sleep(1)

def main():
	arg_parser = argparse.ArgumentParser()

	arg_parser.add_argument('--metafile', help='Name of the .torrent file', nargs=1, type=lambda value:check_input_file_name(value))
	arg_parser.add_argument('--dest', help='Location where the file needs to be downloaded', nargs=1, type=lambda value:check_output_location(value))

	args = arg_parser.parse_args()
	if not args.metafile:
		print("Please specify a metafile using --metafile option")
		return
	if not args.dest:
		print("Please specify a output destination using --dest option")
		return

	torrent_object = torrent(args.metafile[0])

if __name__=='__main__':
	main()
