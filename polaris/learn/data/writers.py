"""
Helpers to write data file as input for different targets.

"""

import json
import os
from pathlib import Path

import numpy as np

from polaris.common import constants


def heatmap_to_graph(heatmap,
                     output_graph_file,
                     graph_link_threshold=0.1,
                     **kwargs):
    """
        Creating a json file for graph visualization

        JSON model used is the one for:
        https://vasturiano.github.io/3d-force-graph/

        :param heatmap: The map to transform to graph
        :param output_graphfile: Out file path for the generated graph
        :param graph_link_threshold: Only keeps links with value greater
        than this threshold.
        :param **kwargs: A dictionary containing
        the keys name to use for building the graph.
        """

    nodes_key = kwargs.get('nodes', "nodes")
    links_key = kwargs.get('links', "links")
    target_key = kwargs.get('target', "target")
    source_key = kwargs.get('source', "source")
    value_key = kwargs.get('value', "value")

    if graph_link_threshold is None:
        graph_link_threshold = 0.1

    if heatmap is not None:
        graph_dict = {nodes_key: [], links_key: []}

        # Adding all possible nodes
        for col in heatmap.columns:
            graph_dict[nodes_key].append({"id": col, "name": col, "group": 0})

        # Adding all edges to graph
        mdict = heatmap.to_dict("dict")
        for source in heatmap.to_dict("dict"):
            for target in mdict[source]:
                if target == source:
                    continue
                if (np.isnan(mdict[source][target])
                        or isinstance(mdict[source][target], str)):
                    continue
                if mdict[source][target] >= graph_link_threshold:
                    graph_dict[links_key].append({
                        source_key:
                        source,
                        target_key:
                        target,
                        value_key:
                        mdict[source][target]
                    })

        # Create parent directory if not already present
        create_parent_directory(output_graph_file)

        with open(output_graph_file, "w") as graph_file:
            json.dump(graph_dict, graph_file, indent=constants.JSON_INDENT)


def create_parent_directory(file_name):
    """Create parent directory for file if needed
    """
    directory = os.path.dirname(file_name)
    Path(directory).mkdir(parents=True, exist_ok=True)
