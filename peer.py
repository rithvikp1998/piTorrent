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
			'keep_alive' : '0',
			'choke' : '10',
			'unchoke' : '11',
			'interested' : '12',
			'not_interested' : '13',
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
					self.send_message('unchoke', 0) #Currently present for testing
			else:
				self.peer_socket.close()
		except:
			raise Exception

	def send_message(self, type, value):
		if self.handshake_made == 0:
			print("A handshake is not made with this peer ")
			return
		if type in self.no_payload_messages:
			print("Message value is", self.no_payload_messages[type])
			self.peer_socket.send(self.no_payload_messages[type].encode('ISO-8859-1'))
			time.sleep(1)