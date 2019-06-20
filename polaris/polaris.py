from argparse import ArgumentParser

import data_fetch

import data_viz

import learning

if __name__ == "__main__":
    parser = ArgumentParser(
        prog='polaris', description="Tool for analyzing satellite telemetry")
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands')

    # parser for 'data-fetch' subcommand
    parser_fetch = subparsers.add_parser('data_fetch', help='data-fetch help')
    parser_fetch.add_argument('foo',
                              type=int,
                              help='subcommand argument example')
    parser_fetch.set_defaults(func=data_fetch)

    # parser for 'learning' subommand
    parser_learning = subparsers.add_parser('learning', help='learning help')
    parser_learning.set_defaults(func=learning)

    # parser for 'data-viz' subcommand
    parser_viz = subparsers.add_parser('data_viz', help='data-viz help')
    parser_viz.set_defaults(func=data_viz)

    args = parser.parse_args()
