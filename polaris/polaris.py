import datetime

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


@click.command('fetch', short_help='Download data set(s)')
@click.argument('sat_name', nargs=1, required=True)
@click.argument('output_dir',
                nargs=1,
                required=False,
                default="/tmp/",
                type=click.Path(exists=True, resolve_path=True))
@click.option('--start_date', '-s', is_flag=False,
              default=(datetime.datetime.utcnow() -
                       datetime.timedelta(seconds=3600)),
              help='Start date of the fetching period. ' +
              'default: set to 1h ago from now.')
@click.option('--end_date', '-e', is_flag=False,
              help='End date of fetching period. ' +
              'default: 1h period from start date.')
def cli_data_fetch(sat_name, start_date, end_date, output_dir):
    data_fetch_decode()


@click.command('learning', short_help='learning help')
def cli_learning():
    print('[FIXME] Learning goes here')
    learning()


@click.command('viz', short_help='data-viz help')
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
