import os.path
import argparse
import hashlib
import requests
import time

import parser

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
		self.info_dict = {}
		self.request_parameters = {}
		self.tracker_response_dict = {}
		self.peer_ips = []

		self.metafile = open(file_name, 'r', encoding = "ISO-8859-1")
		
		if self.metafile.read(1)=='d':
			print("Parsing metafile")
			self.metafile_dict = parser.get_dict(self.metafile)
			print("Parsing metafile complete")

		self.metafile.close()

		self.info_dict = self.metafile_dict['info']
		self.info_dict_hash = hashlib.sha1(parser.bencode_dict(self.info_dict).encode('utf-8')).digest()
		self.peer_id = str(time.time())
		if len(self.peer_id) > 20:
			self.peer_id = self.peer_id[:20]
		else:
			while len(self.peer_id)!=20:
				self.peer_id += '0'

		self.port = 6881 # [TODO] Search between 6881 - 6889 instead
		
		self.send_tracker_request()
		if 'peers' in self.tracker_response_dict:
			self.get_peers()
		else:
			print("Tracker returned no peers")

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

		print("Sending a http request to", self.metafile_dict['announce-list'][0][0]) # [TODO] Check for UDP and act accordingly
		self.response = requests.get(self.metafile_dict['announce-list'][0][0], params=self.request_parameters)
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
			port = str(int(peers_list[4])*256 + int(peers_list[5]))
			self.peer_ips.append((ip, port))
			peers_list=peers_list[6:]

		print("The list of available peers is:", self.peer_ips)

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