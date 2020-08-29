"""
Module to prepare and serve data for visualization
"""

import http.server
import logging
import os
import signal
import socketserver
import sys
from shutil import copy

import requests

LOGGER = logging.getLogger(__name__)

HOST, PORT = "localhost", 8080

WWW_DIR = "/tmp/"


class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """ HTTP Handler to serve viz directory """
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

    # Write new index file to be served
    with open(target_index, "w") as target_fd:
        html_template = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "dynamic_network_analysis_3d-ui.html")
        with open(html_template, "r") as template_fd:
            for line in template_fd:
                if "JSON_DATA_FILE_HERE" in line:
                    target_fd.write(
                        line.replace("JSON_DATA_FILE_HERE", target_file))
                elif "WINDOW_TITLE_HERE" in line:
                    target_fd.write(
                        line.replace("WINDOW_TITLE_HERE",
                                     "Polaris - {}".format(json_data_file)))
                else:
                    target_fd.write(line)

    create_js(target_directory)
    create_favicon(target_directory)

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


def create_favicon(target_directory):
    """Create a favicon file

    :param target_directory: directory to write favicon file
    """
    # Writing a dummy icon file to avoid http 404 errors
    with open(os.path.join(target_directory, "favicon.ico"), "w") as icon_fd:
        icon_fd.write("A")


def create_js(target_directory):
    """Create javascript files
    """
    target_assets = [(os.path.join(target_directory, "3d-force-graph.js"),
                      "https://deepchaos.space/3d-force-graph.js"),
                     (os.path.join(target_directory, "d3.v5.min.js"),
                      "https://deepchaos.space/d3.v5.min.js"),
                     (os.path.join(target_directory,
                                   "three"), "https://unpkg.com/three"),
                     (os.path.join(target_directory, "three-spritetext"),
                      "https://unpkg.com/three-spritetext")]
    # Check if required JS libs are in target directory
    for asset in target_assets:
        if not os.path.isfile(asset[0]):
            with open(asset[0], "w") as lib_fd:
                LOGGER.info("Downloading dependency: %s", asset[0])
                req = requests.get(asset[1])
                lib_fd.write(req.text)

    local_files_dir = os.path.dirname(os.path.abspath(__file__))

    local_assets = [  # source, destination
        (os.path.join(local_files_dir, 'polaris.js'),
         os.path.join(target_directory, 'polaris.js')),
        (os.path.join(local_files_dir, 'style_sheet.css'),
         os.path.join(target_directory, 'style_sheet.css')),
    ]

    for asset in local_assets:
        LOGGER.info("Copying dependency to: %s", asset[1])
        copy(asset[0], asset[1])
