# Dataviz for Polaris

## Required HTML5 library

The data visualization of Polaris is based on a single HTML5 file ([`dynamic\_network\_analysis\_3d-ui.html`](dynamic_network_analysis_3d-ui.html)) which uses the [3D Force Graph library version 1.52.0](https://vasturiano.github.io/3d-force-graph/). The library is not included in the the repo, but there are different ways to get it:
 - `wget https://deepchaos.space/3d-force-graph.js` (version 1.52)
 - `wget https://unpkg.com/3d-force-graph -O 3d-force-graph.js` (latest version)
 - Download the file from [github/vasturiano/3d-force-graph releases](https://github.com/vasturiano/3d-force-graph/releases)
 - Replace the corresponding script html tag by `<script src="//unpkg.com/3d-force-graph"></script>` (in `dynamic\_network\_analysis\_3d-ui.html`, this option won't work if you locally open the html file with your browser)

## Required JSON data file

The data is obtained from the file `sample_data_fimps.json`, which contains an object composed of two main arrais called "nodes" and "links". Nodes have an `id` field used to describe which `source` and `target` each link has.

All other parameters are optional for the graph structure construction. However they are used for:
 - node colors
 - link weight or color
 - particle speed

## Run the server locally

Execute `polaris viz` and open the indicated host and port, generally this would work: `http://0.0.0.0:8000/dynamic_network_analysis_3d-ui.html`.

## User Interface guide for the the graph HTML5 page

### From the search input field

 - **CTRL+RETURN**: every node with the entered pattern will be colored. It can be repeated and colors will rotate.
 - **CTRL+SHIFT+RETURN**: reset node color highlighting completely if the search field is empty, or with one color to highlight only the current pattern.

