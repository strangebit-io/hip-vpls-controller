from binascii import hexlify

class Utils():
	"""
	Various utilities
	"""
	@staticmethod
	def hits_equal(hit1, hit2):
		"""
		Checks if two Host Identity Tags are equal
		"""
		if len(hit1) != len(hit2):
			return False;
		for i in range(0, len(hit1)):
			if hit1[i] != hit2[i]:
				return False;
		return True;
		
	@staticmethod
	def ipv6_bytes_to_hex(address_bytes):
		"""
		Converts IPv6 bytes to a hexidecimal string
		"""
		return hexlify(address_bytes).decode("ascii");

	@staticmethod
	def ipv4_bytes_to_string(address_bytes):
		if len(address_bytes) != 0x4:
			return "";
		return str(address_bytes[0]) + "." + \
			str(address_bytes[1]) + "." + \
			str(address_bytes[2]) + "." + \
			str(address_bytes[3]);


	@staticmethod
	def ipv6_bytes_to_hex_formatted(address_bytes):
		address = Utils.ipv6_bytes_to_hex(address_bytes);
		
		formatted = "";
		c = 1;
		for h in address:
			formatted += h;
			if c % 4 == 0:
				formatted += ":"
			c += 1;
		return formatted.rstrip(":");

	@staticmethod
	def ipv4_to_bytes(address):
		try:
			parts = address.split(".");
			address_as_bytearray = bytearray([0] * 4);
			address_as_bytearray[0] = int(parts[0]);
			address_as_bytearray[1] = int(parts[1]);
			address_as_bytearray[2] = int(parts[2]);
			address_as_bytearray[3] = int(parts[3]);
			return address_as_bytearray
		except:
			return None;

	@staticmethod
	def ipv4_to_int(address):
		"""
		Converts IPv4 address to integer
		"""
		try:
			parts = address.split(".");
			address_as_int = 0;
			address_as_int |= (int(parts[0]) << 24);
			address_as_int |= (int(parts[1]) << 16);
			address_as_int |= (int(parts[2]) << 8);
			address_as_int |= (int(parts[3]));
			return address_as_int
		except:
			return 0;


