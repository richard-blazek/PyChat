import sockets
import sys

s = sockets.connect(sys.argv[1] if len(sys.argv)>1 else '127.0.0.1', 5000)
while True:
	print(s.send_str(input()+'\n'))
	recieved=s.recv_str()
	if recieved==sockets.CLOSED:
		print('Disconnected! Press enter to end program')
		input()
		break
	else:
		print(recieved)
