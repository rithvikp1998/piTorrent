import socket
import time

class peer:
	def __init__(self, ip, port, info_dict_hash, peer_id):
		self.ip = ip
		self.port = port
		self.info_dict_hash = info_dict_hash
		self.peer_id = peer_id
		self.handshake_made = 0
		self.peer_choking = 1
		self.peer_interested = 0
		self.client_interested = 0
		self.client_choking = 1
		self.no_payload_messages = {
			'keep_alive' : b'\x00\x00\x00\x00',			#length : 0, id : None
			'choke' : b'\x00\x00\x00\x01\x00',			#length : 1, id : 0
			'unchoke' : b'\x00\x00\x00\x01\x01',		#length : 1, id : 1
			'interested' : b'\x00\x00\x00\x01\x02',		#length : 1, id : 2
			'not_interested' : b'\x00\x00\x00\x01\x03',	#length : 1, id : 3
		}

	def handshake(self):
		pstr = "BitTorrent protocol"
		packet = chr(len(pstr)) + pstr + str(chr(0)*8) + str(self.info_dict_hash.decode('ISO-8859-1')) + self.peer_id
		assert len(packet) == 49 + len(pstr)
		self.peer_socket = socket.socket()
		self.peer_socket.settimeout(0.1)
		self.peer_socket.setblocking(True)
		i=('192.168.0.102', 6882) # To avoid port-forwarding discussion with my college ISP
		while True:				  # [TODO] See how Transmission's ports are forwarded
			try:
				self.peer_socket.connect(i)
				break
			except socket.timeout:
				print("Timeout exception")
				break
			except socket.error:
				print("Socket error exception")
				time.sleep(5)
				continue
			except:
				raise Exception

		self.peer_socket.send(packet.encode('ISO-8859-1'))
		print("Handshake packet sent to", i)

		try:
			self.peer_response = self.peer_socket.recv(1024)
			if self.peer_response[28:48] == self.info_dict_hash:
				self.handshake_made = 1
				while True:
					self.send_message('unchoke') #Currently present for testing
					time.sleep(3)
			else:
				self.peer_socket.close()
		except:
			raise Exception

	def send_message(self, type):
		if self.handshake_made == 0:
			print("A handshake is not made with this peer ")
			return
		if type in self.no_payload_messages:
			print("Message value is", self.no_payload_messages[type])
			self.peer_socket.send(self.no_payload_messages[type])
		else:
			print("Incorrect message type for no-payload message")

	def send_message_have(self, piece_index):
		'''
		Message type : have
		length : 5 (b'\x00\x00\x00\x05')
		id : 4	(b'\x04')
		payload : piece_index
		'''
		try:
			self.peer_socket.send(b'\x00\x00\x00\x05'+b'\x04'+piece_index)
		except:
			print("Exception while sending the 'have' message")

	def send_message_bitfield(self, bitfield):
		'''
		Message type : bitfield
		length : 1 + len(bitfield)
		id : 5 (b'\x05')
		payload : bitfield
		'''
		try:
			self.peer_socket.send((len(bitfield)+1).to_bytes(4, byteorder='big')
									+(b'\x05')+bitfield)
		except:
			print("Exception while sending the 'bitfield' message")

	def send_message_request(self, index, begin, length):
		'''
		[TODO] Section under dispute, reimplement if necessary
		Message type : request
		length : 13 (b'\x00\x00\x00\r')
		id : 6 (b'\x06')
		payload : index, begin, length
		'''
		try:
			self.peer_socket.send(b'\x00\x00\x00\r'+b'\x06'+index+begin+length)
		except:
			print("Exception while sending the 'request' message")

	def send_message_piece(self, index, begin, block):
		'''
		Message type : piece
		length : 9 + len(block)
		id : 7 (b'\x07')
		payload : index, begin, block
		'''
		try:
			self.peer_socket.send((len(block)+9).to_bytes(4, byteorder='big')
									+b'\x07'+index+begin+block)
		except:
			print("Exception while sending the 'piece' message")

	def send_message_cancel(self, index, begin, length):
		'''
		Message type : cancel
		length : 13 (b'\x00\x00\x00\r')
		id : 8 (b'\x08')
		payload : index, begin, length
		'''
		try:
			self.peer_socket.send(b'\x00\x00\x00\r'+b'\x08'+index+begin+length)
		except:
			print("Exception while sending the 'cancel' message")

	def send_message_port(self, listen_port):
		'''
		[The port message is sent by newer versions of the Mainline that implements a DHT tracker]
		Message type : port
		length : 3 (b'\x03')
		id : 9 (b'\t')
		payload : listen_port
		'''
		try:
			self.peer_socket.send(b'\x03'+b'\t'+listen_port)
		except:
			print("Exception while sending the 'port' message")