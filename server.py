import sockets

connections=[]

def disconnect(con):
	print(con.getsockname(), ' is disconnected!')
	con.close()
	connections.remove(con)

def connect_next(s):
	con=s.accept(0)
	if con!=None:
		print(con.getsockname(), ' is connected!')
		connections.append(con)

def broadcast(message, sock):
	for con in connections:
		if con!=sock:
			con.send_str(message)

def send_message(message, sock):
	if message!='':
		print(sock.getsockname(), ' writes: ', message)
		broadcast(message, sock)

def process_message(message, sock):
	if message==sockets.CLOSED:
		disconnect(sock)
	else:
		send_message(message, sock)

s=sockets.server()
s.bind('', 5000)
s.start()
while True:
	connect_next(s)
	for con in connections:
		process_message(con.recv_str(), con)
		
