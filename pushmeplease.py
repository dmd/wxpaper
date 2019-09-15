#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import wxpaper


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        if self.path == "/pushmeplease":
            print("got push request")
            try:
                wxpaper.do_update()
                self.wfile.write(b"ok\n")
            except:
                self.wfile.write(b"uh oh\n")
        else:
            print("got invalid request")
            self.wfile.write(b"go away\n")


def run(server_class=HTTPServer, handler_class=S, port=8099):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd...")
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
