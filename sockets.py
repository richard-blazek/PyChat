import socket
import errno
import json

CLOSED=-1

class sock:
    def __init__(self, s):
        self.s=s

    def recv(self):
        text=b''
        try:
            while True:
                data=self.s.recv(4096)
                if not data:
                    return CLOSED
                else:
                    text += data
        except socket.error as err:
            if err.args[0]==errno.EWOULDBLOCK:
                return text
            else:
                raise

    def recv_str(self):
        string=self.recv()
        return string.decode() if string!=CLOSED else CLOSED

    def recv_json(self):
        recieved=self.recv_str()
        if recieved==CLOSED:
            return CLOSED
        if recieved=='':
            return []
        jsons=recieved.split(sep='\0')[0:-1]
        return [json.loads(x) for x in jsons]

    def send(self, message):
        self.s.sendall(message)

    def send_str(self, message):
        self.send(message.encode())

    def send_json(self, data):
        self.send_str(json.dumps(data)+'\0')

    def close(self):
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()

    def isblocking(self):
        return self.s.gettimeout()==None

    def isnonblocking(self):
        return self.s.gettimeout()==0.0

    def istimeout(self):
        return self.s.gettimeout()!=0.0 and self.s.gettimeout()!=None

    def setblocking(self, blocking):
        self.s.settimeout(None if blocking else 0.0)

    def gettimeout(self):
        return self.s.gettimeout()

    def settimeout(self, timeout):
        self.s.settimeout(timeout)

    def getsockname(self):
        return self.s.getsockname()

    def gethostname(self):
        return self.getsockname()[0]

    def getportname(self):
        return self.getsockname()[1]

    def getfamily(self):
        return self.s.family

    def gettype(self):
        return self.s.type

    def getprotocol(self):
        return self.s.proto

class client(sock):
    def __init__(self, **kwargs):
        super().__init__(socket.socket(**kwargs))

    def connect(self, host, port, timeout, result_blocking=False):
        self.settimeout(timeout)
        self.s.connect((host, port))
        self.setblocking(result_blocking)

class server(sock):
    def __init__(self, **kwargs):
        super().__init__(socket.socket(**kwargs))

    def bind(self, host, port):
        self.s.bind((host, port))

    def start(self):
        self.s.listen(10)

    def accept(self, timeout, result_blocking=False):
        self.settimeout(timeout)
        try:
            s, _=self.s.accept()
            s.setblocking(result_blocking)
            return sock(s)
        except socket.error as err:
            if err.args[0]==errno.EWOULDBLOCK:
                return None
            else:
                raise


def connect(host, port, blocking=False):
    s = client()
    try:
        s.connect(host, port, None, blocking)
        return s
    except socket.error:
        s = server()
        s.bind('', port)
        s.start()
        s=s.accept(None, blocking)
        return s
