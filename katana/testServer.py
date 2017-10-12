import sys
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

warningMessage="""
<H1>You are not running django! </H1>
	Please make sure you are running katana with django installed for the server. <p>
	<a href="https://docs.djangoproject.com/en/1.11/topics/install/">Documentation for installing django here.</a>
""";

HandlerClass = SimpleHTTPRequestHandler
ServerClass  = BaseHTTPServer.HTTPServer
Protocol     = "HTTP/1.0"
REDIRECTIONS = {"/": "http://python.org/",
                "/katana/": "http://google.com/"}
LAST_RESORT = "http://google.com/"

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body>%s</body></html>" % warningMessage)

	def do_HEAD(self):
		self.send_response(301)
		self.send_header("Location", REDIRECTIONS.get(self.path, LAST_RESORT))
		self.end_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")


if sys.argv[1:]: 
    port = int(sys.argv[1]) 
else: 
    port = 5000 
server_address = ('127.0.0.1', port) 
HandlerClass.protocol_version = Protocol 
httpd = ServerClass(server_address, SimpleHandler)
sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
try:
	httpd.serve_forever()
except KeyboardInterrupt:
	pass
httpd.server_close()
