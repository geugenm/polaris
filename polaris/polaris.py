import click

from data_fetch.data_fetch_decoder import data_fetch_decode

import data_viz

import learning


# TODO: See
# https://github.com/pallets/click/blob/master/examples/repo/repo.py
# for some cool options
@click.group()
def cli():
    """Tool for analyzing satellite telemetry
    """
    pass


@click.command('data_fetch', short_help='Download data set(s)')
def cli_data_fetch():
    data_fetch_decode()


@click.command('learning', short_help='learning help')
def cli_learning():
    print('[FIXME] Learning goes here')
    learning()


@click.command('data_viz', short_help='data-viz help')
def cli_data_viz():
    print('[FIXME] Data visualization goes here')
    data_viz()


# click doesn't automagically add the commands to the group
# (and thus to the help output); you have to do it manually.
cli.add_command(cli_data_fetch)
cli.add_command(cli_learning)
cli.add_command(cli_data_viz)

if __name__ == "__main__":
    cli()
