from pyftpdlib import servers
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from socket import gethostbyname, gethostname
auth = DummyAuthorizer()
auth.add_user('user','pass','./ftp_server_root',perm='elradfmwMT')
address = gethostbyname(gethostname())
handler = FTPHandler
handler.authorizer = auth
print(address)
address = (address, 21)  # listen on every IP on my machine on port 21
server = servers.FTPServer(address, handler)
server.serve_forever()