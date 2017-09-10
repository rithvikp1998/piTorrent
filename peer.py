import socket
import time

class peer:
	def __init__(self, ip, port, info_dict_hash, peer_id):
		self.ip = ip
		self.port = port
		self.info_dict_hash = info_dict_hash
		self.peer_id = peer_id

	def handshake(self):
		pstr = "BitTorrent protocol"
		packet = chr(len(pstr)) + pstr + str(chr(0)*8) + str(self.info_dict_hash.decode('ISO-8859-1')) + self.peer_id
		assert len(packet) == 49 + len(pstr)
		peer_socket = socket.socket()
		peer_socket.settimeout(0.1)
		peer_socket.setblocking(True)
		i=('192.168.0.102', 6882) # To avoid port-forwarding discussion with my college ISP
		while True:				  # [TODO] See how Transmission's ports are forwarded
			try:
				peer_socket.connect(i)
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
		
		peer_socket.send(packet.encode())
		try:
			peer_response = peer_socket.recv(1024)
			print(peer_response)
		except:
			raise Exception