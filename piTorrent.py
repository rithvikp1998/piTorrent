import os.path
import argparse

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

def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('--metafile', help='Name of the .torrent file', nargs=1, type=lambda value:check_input_file_name(value))
	parser.add_argument('--dest', help='Location where the file needs to be downloaded', nargs=1, type=lambda value:check_output_location(value))

	args = parser.parse_args()
	if not args.metafile:
		print("Please specify a metafile using --metafile option")
		return
	if not args.dest:
		print("Please specify a output destination using --dest option")
		return
	file = open(args.metafile[0], 'r', encoding = "ISO-8859-1")
	print(file.read(10))

if __name__=='__main__':
	main()