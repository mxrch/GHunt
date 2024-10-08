import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import *

from ghunt.objects.base import SmartObj


class DataBridge(SmartObj):
    def __init__(self):
        self.data = None

class Server(BaseHTTPRequestHandler):    
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()

    def do_GET(self):
        if self.path == "/ghunt_ping":
            self._set_response()
            self.wfile.write(b"ghunt_pong")

    def do_POST(self):
        if self.path == "/ghunt_feed":
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            self.data_bridge.data = post_data.decode('utf-8')

            self._set_response()
            self.wfile.write(b"ghunt_received_ok")

    def log_message(self, format, *args):
        return

def run(server_class=HTTPServer, handler_class=Server, port=60067):
    server_address = ('127.0.0.1', port)
    handler_class.data_bridge = DataBridge()
    server = server_class(server_address, handler_class)
    try:
        print(f"GHunt is listening on port {port}...")

        while True:
            server.handle_request()
            if handler_class.data_bridge.data:
                break

    except KeyboardInterrupt:
        print("[-] Exiting...")
        exit(os.CLD_KILLED)
    else:
        if handler_class.data_bridge.data:
            print("[+] Received cookies !")
            return handler_class.data_bridge.data