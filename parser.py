def get_list(metafile):
	satellite_list = []
	lc = 1
	while lc!=0:
		c=metafile.read(1)
		if c=='l':
			lc+=1
		elif c=='e':
			lc-=1
		elif c=='d':
			satellite_list.append(get_dict(metafile))
		else:
			length_list_item = ''
			while c!=':':
				length_list_item += c
				c = metafile.read(1)
			length_list_item=int(length_list_item)
			satellite_list.append(metafile.read(length_list_item))
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
	dict = {}
	while True:
		'''
		Get key name, which will always be a string
		'''
		c = metafile.read(1)
		if c=='e':
			return dict
		else:
			key_name = get_str(metafile, c)

		# Since 'pieces' corresponds to the concatenated string of 20-byte hash values, I'll handle this case later [TODO]
		if key_name == 'pieces': 
			return dict
		
		'''
		Get satellite value that corresponds to the key. It can be dict, list, string or int
		'''
		c = metafile.read(1)

		# If the satellite value is a list
		if c=='l':
			dict[key_name] = get_list(metafile)

		# If the satellite value is an int
		elif c=='i':
			dict[key_name] = get_int(metafile)

		# If the satellite value is a dict
		elif c=='d':
			dict[key_name] = get_dict(metafile)

		#If the dict reached an end
		elif c=='e':
			return dict

		# If the satellite value is a string
		else:
			dict[key_name] = get_str(metafile, c)

def bencode_dict(dict):
	result = 'd'
	for key in dict:
		result += str(len(key)) + ':' + key
		result += str(len(str(dict[key]))) + ':' + str(dict[key])
	result += 'e'
	return result