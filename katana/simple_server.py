import BaseHTTPServer
import webbrowser
from SimpleHTTPServer import SimpleHTTPRequestHandler
from BaseHTTPServer import BaseHTTPRequestHandler

warning_message = "<h1>You are not running django! </h1>" \
                 "Please make sure you are running katana with django installed for the server. <p>" \
                 "<a target=\"_blank\" href=\"https://docs.djangoproject.com/en/1.11/topics/install/\">" \
                 "Documentation for Installing Django.</a>"


class SimpleHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body>{0}</body></html>".format(warning_message))


def main(port):
    print "\nYou are missing the django framework.\n" \
          "Please install django on you system.\n" \
          "Try  sudo pip install django\n\n" \
          "Refer to this link for more information\n" \
          "https://docs.djangoproject.com/en/1.11/topics/install/\n"

    handler_class = SimpleHTTPRequestHandler
    server_class = BaseHTTPServer.HTTPServer
    ip = "localhost"

    handler_class.protocol_version = "HTTP/1.0"
    httpd = server_class((ip, int(port)), SimpleHandler)
    address, port_number = httpd.socket.getsockname()
    print "-- WARNING -- Serving django-less server on http://{0}:{1}\n".format(address, port_number)

    open_browser(ip, port)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


def open_browser(ip, port):
    try:
        webbrowser.open('http://{0}:{1}/'.format(ip, port), new=2)
    except Exception as e:
        print "-- ERROR -- Could not open browser due to :\n{0}".format(e)
