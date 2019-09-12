"""
Module to prepare and serve data for visualization
"""

import http.server
import logging
import os
import socketserver

LOGGER = logging.getLogger(__name__)

HOST, PORT = "localhost", 8080


class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """ HTTP Handler to serve data_viz directory """

    def handle(self):
        self.directory = os.path.dirname(os.path.abspath(__file__))
        super().handle()


def launch():
    """ Start the server """
    with socketserver.TCPServer((HOST, PORT), CustomHTTPHandler) as httpd:
        LOGGER.info("Serving ready: http://%s:%s", HOST, PORT)
        httpd.serve_forever()
