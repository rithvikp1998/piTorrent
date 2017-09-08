import os.path
import argparse

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

		self.metafile = open(file_name, 'r', encoding = "ISO-8859-1")
		
		if self.metafile.read(1)=='d':
			self.metafile_dict = parser.get_dict(self.metafile)
			for key in self.metafile_dict:
				print(key, ':', self.metafile_dict[key])

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