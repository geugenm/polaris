"""
Helpers to write data file as input for different targets.

"""

import json

import numpy as np

from polaris.common import constants


def importances_map_to_graph(importances_map,
                             output_graph_file,
                             graph_link_threshold=0.1):
    """
        Creating a json file for graph visualization

        JSON model used is the one for:
        https://vasturiano.github.io/3d-force-graph/
        """

    if graph_link_threshold is None:
        graph_link_threshold = 0.1

    if importances_map is not None:
        graph_dict = {"nodes": [], "links": []}

        # Adding all possible nodes
        for col in importances_map.columns:
            graph_dict["nodes"].append({"id": col, "name": col, "group": 0})

        # Adding all edges to graph
        mdict = importances_map.to_dict("dict")
        for source in importances_map.to_dict("dict"):
            for target in mdict[source]:
                if target == source:
                    continue
                if (np.isnan(mdict[source][target])
                        or isinstance(mdict[source][target], str)):
                    continue
                elif mdict[source][target] >= graph_link_threshold:
                    graph_dict["links"].append({
                        "source": source,
                        "target": target,
                        "value": mdict[source][target]
                    })

        with open(output_graph_file, "w") as graph_file:
            json.dump(graph_dict, graph_file, indent=constants.JSON_INDENT)
