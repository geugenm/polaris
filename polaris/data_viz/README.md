Dataviz for Polaris


sample\_data\_fimps.json
=========================

JSON file model representing the graph that is visualized.
It is a document composed of two main arrays called
 - "nodes"
 - "links"

Nodes have an `id` field used to describe which `source` and `target` each link has.

All other parameters are optional for the graph structure construction.
However they are used for:
  - node colors
  - link weight or color
  - particle speed


dynamic\_network\_analysis\_3d-ui.html
=======================================


Get the requirements
--------------------

One requirement used by the HTML5 page is the [3D Force Graph library](https://vasturiano.github.io/3d-force-graph/).

The page uses `3d-force-graph.js version 1.52.0`, different solutions to get it:
 - `wget https://deepchaos.space/3d-force-graph.js`
 - or get the file from [github/vasturiano/3d-force-graph releases](https://github.com/vasturiano/3d-force-graph/releases)
 - or replace the corresponding script html tag by `<script src="//unpkg.com/3d-force-graph"></script>`


How to deploy locally
----------------------

Position yourself in the folder where you have the following files:
 - sample\_data\_fimps.json
 - 3d-force-graph.js
 - dynamic\_network\_analysis\_3d-ui.html

Then start a simple python webserver:
```bash
python -m http.server
```

Then open the indicated host and port, generally this would work: `http://0.0.0.0:8000/dynamic_network_analysis_3d-ui.html`

You could also copy all the files to one of the root of an already running webserver.
Configurations of webservers such as nginx or apache are not covered here.


Other Info
==========

**dynamic\_network\_analysis\_3d-ui.html** is meant to be a Dynamic Network Analysis for operators awareness. DNA for space operations is a concept which has been presented at the [SpaceOps 2018 Conference](https://www.researchgate.net/publication/325388857_Enhanced_Awareness_In_Space_Operations_Using_Multipurpose_Dynamic_Network_Analysis).

Operators should be able to explore relationships between nodes (e.g. telemetry parameters) using graph concepts.


