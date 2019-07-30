"""
Tool for analyzing satellite telemetry
"""
import logging

import click

from polaris import __version__
from polaris.data_fetch.data_fetch_decoder import data_fetch_decode

# Logger configuration
LOGGER = logging.getLogger(__name__)
CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
FORMATTER = logging.Formatter(LOG_FORMAT)
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)

# Uncomment these imports when we're ready to start using them
# import data_viz
# import learning


@click.version_option(version=__version__)
@click.group()
def cli():
    """
    Tool for analyzing satellite telemetry
    """
    return


@click.command('fetch',
               context_settings={"ignore_unknown_options": True},
               short_help='Download data set(s)')
@click.argument('sat', nargs=1, required=True)
@click.argument('output_directory',
                required=False,
                default="/tmp",
                type=click.Path(exists=True, resolve_path=True))
@click.option('--start_date',
              '-s',
              is_flag=False,
              help='Start date of the fetching period.'
              ' Default: set to 1h ago from now.')
@click.option('--end_date',
              '-e',
              is_flag=False,
              help='End date of fetching period.'
              ' Default: 1h period from start date.')
def cli_data_fetch(sat, start_date, end_date, output_directory):
    """ Retrieve and decode the telemetry corresponding to SAT (satellite name
     or NORAD ID) """
    LOGGER.info("output dir: %s", output_directory)
    data_fetch_decode(sat, output_directory, start_date, end_date)


@click.command('learning', short_help='learning help')
def cli_learning():
    """
    Enter learning module
    """
    LOGGER.debug('[FIXME] Learning goes here')
    # learning()


@click.command('viz', short_help='data-viz help')
def cli_data_viz():
    """
    Enter visualization module
    """
    LOGGER.debug('[FIXME] Data visualization goes here')
    # data_viz()


# click doesn't automagically add the commands to the group
# (and thus to the help output); you have to do it manually.
cli.add_command(cli_data_fetch)
cli.add_command(cli_learning)
cli.add_command(cli_data_viz)
