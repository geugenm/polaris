"""
Tool for analyzing satellite telemetry
"""
import logging

import click

from polaris import __version__
from polaris.data_fetch.data_fetch_decoder import data_fetch_decode_normalize
from polaris.data_viz.server import launch_webserver
from polaris.learning.analysis import cross_correlate, feature_extraction

# Logger configuration

# Set the logger name explicitly to 'polaris'; if we use __name__
# here, we get 'polaris.polaris', which is redundant. It also allows
# modules to use the parent logger, as their __name__ begins with
# 'polaris', not 'polaris.polaris'.
LOGGER = logging.getLogger('polaris')
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
    data_fetch_decode_normalize(sat, output_directory, start_date, end_date)


@click.command('learn',
               short_help='learning help',
               help='INPUT_FILE in csv or json format')
@click.argument('input_file', nargs=1, required=True)
@click.option('--output_graph_file',
              '-g',
              is_flag=False,
              help='Output json graph file')
@click.option('--graph_link_threshold',
              '-t',
              is_flag=False,
              help='Threshold of influence to show edges')
@click.option('--col',
              '-c',
              is_flag=False,
              help='Target column to extract features for')
@click.option('--csv_sep',
              '-s',
              is_flag=False,
              help='The separator used in the input csv file')
def cli_learning(input_file,
                 output_graph_file=None,
                 graph_link_threshold=0.1,
                 col=None,
                 csv_sep=','):
    """
    Enter learning module
    """
    if col is not None:
        feature_extraction(input_file, col)
    elif output_graph_file is not None:
        cross_correlate(input_file,
                        output_graph_file,
                        graph_link_threshold,
                        csv_sep=csv_sep)
    else:
        LOGGER.warning("Nothing learnt from file: %s", input_file)


@click.command('viz', short_help='Display results')
@click.argument('graph_file', nargs=1, required=True)
def cli_data_viz(graph_file):
    """ Serving HTML5 visualization from directory with JSON graph file

        :param graph_file: JSON data file with graph information about nodes
        and edges.
    """
    launch_webserver(graph_file)


# click doesn't automagically add the commands to the group
# (and thus to the help output); you have to do it manually.
cli.add_command(cli_data_fetch)
cli.add_command(cli_learning)
cli.add_command(cli_data_viz)
