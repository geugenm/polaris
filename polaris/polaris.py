from argparse import ArgumentParser
import argparse
import subprocess
from data_fetch.data_fetch_decoder import *
import data_viz
import learning

class Fetch(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        data_fetch_decode()
if __name__ == "__main__":
    parser = ArgumentParser(
        prog='polaris', description="Tool for analyzing satellite telemetry")
    subparsers = parser.add_subparsers(
        title='subcommands', description='valid subcommands')

    # parser for 'data-fetch' subcommand
    parser_fetch = subparsers.add_parser('data_fetch', help='data-fetch help')
    parser_fetch.add_argument(
        'foo', type=int, help='subcommand argument example',action=Fetch)
    # parser_fetch.set_defaults(func=data_fetch_decode)

    # parser for 'learning' subommand
    parser_learning = subparsers.add_parser('learning', help='learning help')
    parser_learning.set_defaults(func=learning)

    # parser for 'data-viz' subcommand
    parser_viz = subparsers.add_parser('data_viz', help='data-viz help')
    parser_viz.set_defaults(func=data_viz)

    args = parser.parse_args()
