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
            except:
                print("something went wrong calling wxpaper")
                pass
        else:
            print("got invalid request")
            self.wfile.write(b"go away\n")


def run(server_class=HTTPServer, handler_class=S, port=33223):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print("Starting httpd...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
