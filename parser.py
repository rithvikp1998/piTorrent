import io

from collections import OrderedDict

def get_list(metafile):
	satellite_list = []
	while True:
		c=metafile.read(1)
		if c=='l':
			satellite_list.append(get_list(metafile))
		elif c=='e':
			return satellite_list
		elif c=='d':
			satellite_list.append(get_dict(metafile))
		else:
			satellite_list.append(get_str(metafile, c))

	return satellite_list

def get_int(metafile):
	integer = ''
	c = metafile.read(1)
	while c!='e':
		integer += c
		c = metafile.read(1)
	integer = int(integer)
	return integer

def get_str(metafile, c):
	length = ''
	while c!=':':
		length += c
		c = metafile.read(1)
	length = int(length)
	return(metafile.read(length))

def get_dict(metafile):
	dictionary = OrderedDict()
	while True:
		'''
		Get key name, which will always be a string
		'''
		c = metafile.read(1)
		if c=='e':
			return dictionary
		else:
			key_name = get_str(metafile, c)

		'''
		Get satellite value that corresponds to the key. It can be dict, list, string or int
		'''
		c = metafile.read(1)

		# If the satellite value is a list
		if c=='l':
			dictionary[key_name] = get_list(metafile)

		# If the satellite value is an int
		elif c=='i':
			dictionary[key_name] = get_int(metafile)

		# If the satellite value is a dict
		elif c=='d':
			dictionary[key_name] = get_dict(metafile)

		#If the dict reached an end
		elif c=='e':
			return dictionary

		# If the satellite value is a string
		else:
			dictionary[key_name] = get_str(metafile, c)

def bencode_dict(dictionary):
	result = 'd'
	for key in dictionary:
		result += str(len(key)) + ':' + key
		if isinstance(dictionary[key], str):
			result += str(len(dictionary[key])) + ':' + dictionary[key]
		elif isinstance(dictionary[key], int):
			result += 'i' + str(dictionary[key]) + 'e'
		elif isinstance(dictionary[key], list):
			result += bencode_list(dictionary[key])
		elif isinstance(dictionary[key], dict):
			result += bencode_dict(dictionary[key])
		else:
			print("Unknown type error in parser.bencode_dict")

	result += 'e'
	return result

def bencode_list(data):
	result = 'l'
	for i in data:
		if isinstance(i, str):
			result += str(len(i)) + ':' + i
		elif isinstance(i, int):
			result += 'i' + str(i) + 'e'
		elif isinstance(i, list):
			result += bencode_list(i)
		elif isinstance(i, dict):
			result += bencode_dict(i)
		else:
			print("Unknown type error in parser.bencode_list")
	result += 'e'
	return result

def bdecode_response_string(response_string):
	f = io.StringIO(response_string)
	if f.read(1)=='d':
		dictionary = get_dict(f)
		return dictionary
	else:
		print("Invalid response string. The response should be a bencoded dictionary")