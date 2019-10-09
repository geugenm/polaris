"""
Module to prepare and serve data for visualization
"""

import http.server
import logging
import os
import signal
import socketserver
import sys

import requests

LOGGER = logging.getLogger(__name__)

HOST, PORT = "localhost", 8080

WWW_DIR = "/tmp/"


class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """ HTTP Handler to serve data_viz directory """

    def handle(self):
        # pylint: disable=W0603
        global WWW_DIR
        self.directory = WWW_DIR
        super().handle()


def launch_webserver(json_data_file):
    """ Start the server

        - Generates index file with right JSON input data
        - Launch server from the JSON input data file directory
    """

    # Define path for index.html
    target_directory, target_file = os.path.split(
        os.path.abspath(json_data_file))
    target_index = os.path.join(target_directory, "index.html")
    target_icon = os.path.join(target_directory, "favicon.ico")
    target_lib = os.path.join(target_directory, "3d-force-graph.js")

    # Read path for source template
    html_template = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "dynamic_network_analysis_3d-ui.html")

    # Write new index file to be served
    with open(target_index, "w") as target_fd:
        with open(html_template, "r") as template_fd:
            for line in template_fd:
                target_fd.write(
                    line.replace("JSON_DATA_FILE_HERE", target_file))

    with open(target_icon, "w") as icon_fd:
        icon_fd.write("A")

    # Check if required JS libs are in target directory
    if not os.path.isfile(target_lib):
        with open(target_lib, "w") as lib_fd:
            LOGGER.info("Downloading dependency: %s", target_lib)
            req = requests.get('https://deepchaos.space/3d-force-graph.js')
            lib_fd.write(req.text)

    # Setup web directory
    # pylint: disable=W0603
    global WWW_DIR
    WWW_DIR = target_directory

    socketserver.TCPServer.allow_reuse_address = True
    # Launch the unglaublich webserver
    with socketserver.TCPServer((HOST, PORT), CustomHTTPHandler) as httpd:
        LOGGER.info("Serving ready: http://%s:%s", HOST, PORT)

        # Catching ctrl+c for clean exit
        def signal_handler(sig, frame):
            LOGGER.info("Shutdown server from ctrl+c")
            LOGGER.debug("%s | %s", sig, frame)
            httpd.server_close()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Launch the server
        httpd.serve_forever()
