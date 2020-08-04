// ---- Global constants
const graph_elt = document.getElementById("3d-graph");
const hud_elt = document.getElementById("graph-hud");
const nodeslist_elt = document.getElementById("nodeslist");
const search_elt = document.getElementById("graph-search-input");
const node_base_color = "#BBF";
// unused collection of nicely separated colors
const polaris_color_set = [
  "#9A6324",
  "#fffac8",
  "#3cb44b",
  "#4644c0",
  "#aaffc3",
  "#e6194B",
  "#42d4f4",
  "#f032e6",
  "#ffe119",
  "#f58231",
  "#ffffff",
];
const color_scale = d3
      .scaleOrdinal()
      .domain([1, polaris_color_set.length])
      .range(polaris_color_set);
var color_step = 0;
var Graph; // Will be filled in up ahead

var Metadata; // Will be filled in up ahead

// ---- Graph's routines ---- //

// Converts node info to HTML for screen display
function node_to_html(node) {
  if (node && typeof node == "object" && node.hasOwnProperty("id"))
    return (
      "id: " + node.id + ", name: <b>" + node.name + "</b>/" + node.group
    );
  // If "node" is already just a string
  return node;
}

// This function updates the HUD in a custom way
function hud_update(action, node) {
  let metadata_header = "<b>" + formatMetadata(Metadata) + "</b>";
  let action_header = "";
  if (action) {
    action_header = "<tiny>" + action + "</tiny>";
  }
  let br = "<br/>";
  let info = node_to_html(node);
  hud_elt.innerHTML = metadata_header + br + action_header + br + info + br;
}

// A zoom and fly to node function
function jetpack_to(node) {
  // node: this is the clicked node to lookAt. {x,y,z}
  // Aim at node from outside it
  const distance = 40;
  const distRatio = 1 + distance / Math.hypot(node.x, node.y, node.z);

  Graph.cameraPosition(
    // aiming at new position
    {
      x: node.x * distRatio,
      y: node.y * distRatio,
      z: node.z * distRatio,
    },
    // lookAt point
    node,
    // transition duration in ms
    3000
  );
}

// ---- Graph creation and customization ---- //

// Metadata creation

function createMetadata(metadata) {
  return metadata;
}

function formatMetadata() {
  return Metadata.satellite_name;
}

// Data loading
async function loadGraphData(jsonUrl) {
  return await fetch(jsonUrl)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      if (data.hasOwnProperty("nodes") && data.hasOwnProperty("links")) {
        // The original format for Polaris Graph files: bare nodes &
        // links.  Return as-is.
        return data;
      } else if (data.hasOwnProperty("graph")) {
	if (data.hasOwnProperty("metadata")) {
	  Metadata = createMetadata(data.metadata);
	  // Give empty strings as arguments so that we don't have
	  // "undefined" in HUD when first called
	  hud_update("", "");
	}
        if (data.graph.data_format_version === 1) {
          // Version 1 of Polaris Graph format
          return data.graph;
        }
      } else {
        // Unknown format for graph file. Returning loaded data untouched.
        return data;
      }
    });
}

async function createGraph(dataFile) {
  loadGraphData(dataFile).then((data) => {
    Graph = ForceGraph3D()(graph_elt)
      .graphData(data)
      .nodeLabel((node) => node.name + ":" + node.group)
      .nodeColor((node) =>
        localStorage.getItem(node.name)
          ? localStorage.getItem(node.name)
          : node.color
          ? node.color
          : node_base_color
      )
      .onNodeHover(
        (node) => (graph_elt.style.cursor = node ? "pointer" : null)
      )
      .onNodeClick((node) => {
        hud_update("clicked", node);
        jetpack_to(node);
      })
      .linkOpacity(0.4)
      .linkWidth(1)
    // visible traveling particule(s) per link
      .linkDirectionalParticles(2)
    // Speed as a ratio of link length per frame
    // and d.value is included in [0;1]
    // as per input definition: feature importance.
      .linkDirectionalParticleSpeed((d) => d.value * 0.01);
  });
}

// ---- Search events and routines ---- //

// This function will be used to fill the datalist
// The datalist is the database for the input auto-complete
function fill_nodeslist() {
  nodeslist_elt.innerHTML = "";
  const { nodes, links } = Graph.graphData();
  for (node of nodes) {
    nodeslist_elt.innerHTML +=
      '<option value="' +
      node.id +
      ":" +
      node.name +
      "/" +
      node.group +
      '"/>';
  }
}

// Multi-function search for string
// for now search by ID.
function find_node(search_str) {
  var node_id = search_str.split(":")[0];

  const { nodes, links } = Graph.graphData();
  for (node of nodes) {
    if (node.id.toString() == node_id) {
      return node;
    }
  }

  return undefined;
}

// Highlight nodes based on the nodes names
function highlight_nodes(search_str, color, reset_color = false) {
  const { nodes, links } = Graph.graphData();
  for (node of nodes) {
    if (reset_color) {
      node.color = color;
    } else if (node.name.includes(search_str)) {
      node.color = color;
    } else {
      node.color = localStorage.getItem(node.name)
        ? localStorage.getItem(node.name)
        : node_base_color;
    }
  }
  Graph.nodeColor((node) => (node.color ? node.color : node_base_color));
}

// Catching keypress events and launching actions
function searchInputCallback(evt) {
  // evt.key is the named key so here we're looking for "Enter"
  // NB: evt.which is deprecated so using only keyCode here.
  // NB: evt.code should be what evt.keyCode is according to W3C standards.
  //     Watch that for eventual future changes.
  if (evt.keyCode === 13 || evt.key == "Enter") {
    // ASCII for Enter (Return Carriage) is 13 (Firefox)
    // For line feed this is 10 (chrome) in UIs generally ctrl+Enter is a linefeed.
    if (evt.ctrlKey) {
      if (evt.shiftKey) {
        // highlight nothing and reset
        hud_update("Resetting colors", "")
        highlight_nodes("", node_base_color, true);
      } else {
        // Control key is pressed: node highligting
        hud_update("highlighting search pattern", search_elt.value);
        color_step += 1;
        // if (color_step > polaris_color_set.length) prompt for user input
        // to give a new color or do nothing: colors will rotate then.
        highlight_nodes(search_elt.value, color_scale(color_step));
      }
    } else {
      // Control key is NOT pressed: jetpacking
      hud_update("searching", search_elt.value);
      const node = find_node(search_elt.value);

      if (node) {
        hud_update("jetpacking", node);
        jetpack_to(node);
      } else {
        hud_update("search stopped", node);
      }
    }
    // Stop processing of the event here.
    evt.stopPropagation();
    evt.preventDefault();
  } // --- end of "Enter" event and derivatives
}

// save the colors to localStorage
function save_color() {
  const { nodes, links } = Graph.graphData();
  for (node of nodes) {
    if (node.color) {
      localStorage.setItem(node.name, node.color);
    }
  }
}

// Autosave every few seconds
var intervalID = window.setInterval(save_color, 5000);

// search: Click event only to check status of datalist
search_elt.addEventListener("click", function () {
  if (nodeslist_elt.innerHTML == "") {
    fill_nodeslist();
  }
});

// search: Keyboard events
search_elt.addEventListener("keydown", searchInputCallback);
