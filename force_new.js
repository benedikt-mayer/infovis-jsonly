var baseNodes = [{
    id: "Süddeutsche Zeitung",
    group: 0,
    label: "Süddeutsche Zeitung",
    level: 1
  },
  {
    id: "Andrea Bachstein",
    group: 0,
    label: "Andrea Bachstein",
    level: 2
  },
  {
    id: "Ronen Steinke",
    group: 0,
    label: "Ronen Steinke",
    level: 2
  },
  {
    id: "Markus Balser",
    group: 0,
    label: "Markus Balser",
    level: 2
  },
  {
    id: "Larissa Holziki",
    group: 0,
    label: "Larissa Holziki",
    level: 2
  },
  {
    id: "Frankfurter Allgemeine",
    group: 1,
    label: "Frankfurter Allgemeine",
    level: 1
  },
  {
    id: "Dyrk Scherff",
    group: 1,
    label: "Dyrk Scherff",
    level: 2
  },
  {
    id: "Philip Plickert",
    group: 1,
    label: "Philip Plickert",
    level: 2
  },
  {
    id: "Spiegel",
    group: 2,
    label: "Spiegel",
    level: 1
  },
  {
    id: "Michael Kröger",
    group: 2,
    label: "Michael Kröger",
    level: 2
  },
  {
    id: "Christiane Hoffmann",
    group: 2,
    label: "Christiane Hoffmann",
    level: 2
  }
]
var baseLinks = [{
    target: "Süddeutsche Zeitung",
    source: "Andrea Bachstein",
    strength: 0.9
  },
  {
    target: "Süddeutsche Zeitung",
    source: "Ronen Steinke",
    strength: 0.9
  },
  {
    target: "Süddeutsche Zeitung",
    source: "Markus Balser",
    strength: 0.9
  },
  {
    target: "Süddeutsche Zeitung",
    source: "Larissa Holziki",
    strength: 0.9
  },
  {
    target: "Frankfurter Allgemeine",
    source: "Dyrk Scherff",
    strength: 0.8
  },
  {
    target: "Frankfurter Allgemeine",
    source: "Philip Plickert",
    strength: 0.8
  },
  {
    target: "Spiegel",
    source: "Michael Kröger",
    strength: 0.7
  },
  {
    target: "Spiegel",
    source: "Christiane Hoffmann",
    strength: 0.7
  },
  {
    target: "Spiegel",
    source: "Süddeutsche Zeitung",
    strength: 0.4
  },
  {
    target: "Spiegel",
    source: "Frankfurter Allgemeine",
    strength: 0.1
  },
  {
    target: "Süddeutsche Zeitung",
    source: "Frankfurter Allgemeine",
    strength: 0.1
  },

]


$(function () {
  let checkvalue = $('input[type=radio][name=Thema]:checked').val()
  console.log("initial force new: " + checkvalue)
  fetchAsyncForce(`http://127.0.0.1:5002/${checkvalue}`);
});

$('input[type=radio][name=Thema]').on('change', function () {
  console.log("changed in force new: " + $(this).val())
  fetchAsyncForce(`http://127.0.0.1:5002/${$(this).val()}`);
});

var jiggle = -20

async function fetchAsyncForce(url) {
  console.log("fetching force new")
  // $("#vis-container").find("circle").remove()
  let response = await fetch(url, {
    headers: {
      'Content-type': 'charset=UTF-8'
    },
    mode: 'cors'
  });
  // let text = await response.text();
  let data = await response.json();
  // console.log("data");
  // console.log(data);
  let newspaper_lists = data.reduce((newspaper_aggregated, element) => {
    if (!newspaper_aggregated[element.newsportal]) {
      newspaper_aggregated[element.newsportal] = [];
    }
    if (!Object.values(newspaper_aggregated).some(newspaper_collection => newspaper_collection.some(existing_element => existing_element.title == element.title))){
      newspaper_aggregated[element.newsportal].push({
        results: element.results,
        title: element.title,
        newsportal: element.newsportal
      });
    }
    return newspaper_aggregated;
  }, {});


  
  Object.entries(newspaper_lists).forEach(([newspaper_list_key, newspaper_list_value]) =>
  newspaper_lists[newspaper_list_key] = newspaper_list_value.slice(0, 15)
  )

  console.log("newspaper_lists")
  console.log(newspaper_lists)


  let summed_newspaper_data = Object.keys(newspaper_lists).map(newsportal => {
    return [
      newsportal, newspaper_lists[newsportal].reduce((sum, element, resultsIndex) => {
        let results = element.results
        Object.keys(results).map(resultKey => {
          if (!sum[resultKey]) {
            sum[resultKey] = results[resultKey].percentile / 100
          } else {
            sum[resultKey] = ((sum[resultKey] * resultsIndex) + (results[resultKey].percentile / 100)) / (resultsIndex + 1)
          }
        })
        return sum;
      }, {})
    ]
  })
  // console.log("summed_newspaper_data")
  // console.log(summed_newspaper_data)

  let newspaper_links = []
  summed_newspaper_data.forEach(source_newspaper_array => {
    let source_newspaper_name = source_newspaper_array[0]
    let source_newspaper_values = source_newspaper_array[1]
    summed_newspaper_data.forEach(target_newspaper_array => {
      let target_newspaper_name = target_newspaper_array[0]
      let target_newspaper_values = target_newspaper_array[1]
      if (source_newspaper_name != target_newspaper_name) {
        let distances = Object.keys(source_newspaper_values).map(result_key => {
          return source_newspaper_values[result_key] - target_newspaper_values[result_key]
        })
        let strength_value = Math.hypot(distances[0], distances[1], distances[2], distances[3], distances[4], distances[5], distances[6], distances[7], distances[8], distances[9])
        newspaper_links.push({
          target: target_newspaper_name,
          source: source_newspaper_name,
          strength: strength_value / 100
        })
      }

    })
  })

  let filtered_articles = Object.keys(newspaper_lists).reduce((accumulator, newspaper_key) => {
    return [...accumulator, ...newspaper_lists[newspaper_key]]
  }, [])

  // console.log("filtered_articles")
  // console.log(filtered_articles)
  
  newspaper_links = [...newspaper_links, ...filtered_articles.map(article => {
    return {
      target: article.newsportal,
      source: article.title,
      strength: 1.0
    };
  })]
  // console.log("newspaper_links")
  // console.log(newspaper_links)
  let newspapers = Object.keys(newspaper_lists)
  console.log("newspapers")
  console.log(newspapers)


  let newspaper_base_nodes = filtered_articles.map(element => {
    return {
      id: element.title,
      group: newspapers.indexOf(element.newsportal),
      label: "", 
      level: 2
    }
  })
  newspapers.forEach(newspaper => {
    newspaper_base_nodes.push({
      id: newspaper,
      group: newspapers.indexOf(newspaper),
      label: newspaper,
      level: 1
    })
  })
  // console.log("newspaper_base_nodes")
  // console.log(newspaper_base_nodes)
  baseNodes = newspaper_base_nodes;
  baseLinks = newspaper_links;
  nodes = [...baseNodes]
  links = [...baseLinks]
  updateSimulation()
}


// var nodes = [...baseNodes]
// var links = [...baseLinks]

function getNeighbors(node) {
  return baseLinks.reduce(function (neighbors, link) {
      if (link.target.id === node.id) {
        neighbors.push(link.source.id)
      } else if (link.source.id === node.id) {
        neighbors.push(link.target.id)
      }
      return neighbors
    },
    [node.id]
  )
}

function isNeighborLink(node, link) {
  return link.target.id === node.id || link.source.id === node.id
}

function getNodeColor(node, neighbors) {
  if (Array.isArray(neighbors) && neighbors.indexOf(node.id) > -1) {
    return node.level === 1 ? 'blue' : 'green'
  }
  return node.level === 1 ? 'red' : 'gray'
}

function getLinkColor(node, link) {
  return isNeighborLink(node, link) ? 'green' : '#E5E5E5'
}

function getTextColor(node, neighbors) {
  return Array.isArray(neighbors) && neighbors.indexOf(node.id) > -1 ? 'green' : 'black'
}
var width = window.innerWidth * 0.9
var height = window.innerHeight * 0.9
var svg = d3.select('#force-directed')
svg.attr('width', width).attr('height', height)//.call(zoom)//.call(zoom.transform, d3.zoomIdentity.translate(100,50).scale(0.5))
var linkElements,
  nodeElements,
  textElements
// we use svg groups to logically group the elements together
var linkGroup = svg.append('g').attr('class', 'links')
var nodeGroup = svg.append('g').attr('class', 'nodes')
var textGroup = svg.append('g').attr('class', 'texts')
// we use this reference to select/deselect
// after clicking the same element twice
var selectedId
// simulation setup with all forces
var linkForce = d3
  .forceLink()
  .id(function (link) {
    return link.id
  })
  .strength(function (link) {
    return link.strength
  })
var simulation = d3
  .forceSimulation()
  .force('link', linkForce)
  .force('charge', d3.forceManyBody().strength(jiggle))
  .force('center', d3.forceCenter(width / 2, height / 2))
var dragDrop = d3.drag().on('start', function (node) {
  node.fx = node.x
  node.fy = node.y
}).on('drag', function (node) {
  simulation.alphaTarget(0.7).restart()
  node.fx = d3.event.x
  node.fy = d3.event.y
}).on('end', function (node) {
  if (!d3.event.active) {
    simulation.alphaTarget(0)
  }
  node.fx = null
  node.fy = null
})
// select node is called on every click
// we either update the data according to the selection
// or reset the data if the same node is clicked twice
function selectNode(selectedNode) {
  if (selectedId === selectedNode.id) {
    selectedId = undefined
    resetData()
    updateSimulation()
  } else {
    selectedId = selectedNode.id
    updateData(selectedNode)
    updateSimulation()
  }
  var neighbors = getNeighbors(selectedNode)
  // we modify the styles to highlight selected nodes
  nodeElements.attr('fill', function (node) {
    return getNodeColor(node, neighbors)
  })
  textElements.attr('fill', function (node) {
    return getTextColor(node, neighbors)
  })
  linkElements.attr('stroke', function (link) {
    return getLinkColor(selectedNode, link)
  })
}
// this helper simple adds all nodes and links
// that are missing, to recreate the initial state
function resetData() {
  var nodeIds = nodes.map(function (node) {
    return node.id
  })
  baseNodes.forEach(function (node) {
    if (nodeIds.indexOf(node.id) === -1) {
      nodes.push(node)
    }
  })
  links = baseLinks
}
// diffing and mutating the data
function updateData(selectedNode) {
  var neighbors = getNeighbors(selectedNode)
  var newNodes = baseNodes.filter(function (node) {
    return neighbors.indexOf(node.id) > -1 || node.level === 1
  })
  var diff = {
    removed: nodes.filter(function (node) {
      return newNodes.indexOf(node) === -1
    }),
    added: newNodes.filter(function (node) {
      return nodes.indexOf(node) === -1
    })
  }
  diff.removed.forEach(function (node) {
    nodes.splice(nodes.indexOf(node), 1)
  })
  diff.added.forEach(function (node) {
    nodes.push(node)
  })
  links = baseLinks.filter(function (link) {
    return link.target.id === selectedNode.id || link.source.id === selectedNode.id
  })
}

function updateGraph() {
  // links
  linkElements = linkGroup.selectAll('line')
    .data(links, function (link) {
      return link.target.id + link.source.id
    })
  linkElements.exit().remove()
  var linkEnter = linkElements
    .enter().append('line')
    .attr('stroke-width', 1)
    .attr('stroke', 'rgba(50, 50, 50, 0.2)')
  linkElements = linkEnter.merge(linkElements)
  // nodes
  nodeElements = nodeGroup.selectAll('circle')
    .data(nodes, function (node) {
      return node.id
    })
  nodeElements.exit().remove()
  var nodeEnter = nodeElements
    .enter()
    .append('circle')
    .attr('r', 10)
    .attr('fill', function (node) {
      return node.level === 1 ? 'red' : 'gray'
    })
    .call(dragDrop)
    // we link the selectNode method here
    // to update the graph on every click
    .on('click', selectNode)
  nodeElements = nodeEnter.merge(nodeElements)
  // texts
  textElements = textGroup.selectAll('text')
    .data(nodes, function (node) {
      return node.id
    })
  textElements.exit().remove()
  var textEnter = textElements
    .enter()
    .append('text')
    .text(function (node) {
      return node.label
    })
    .attr('font-size', 15)
    .attr('dx', 15)
    .attr('dy', 4)
  textElements = textEnter.merge(textElements)
}



function updateSimulation() {

  let radius = 6;
  updateGraph()
  simulation.nodes(nodes).on('tick', () => 
  {
    nodeElements.attr("cx", function(d) { return d.x = Math.max(radius, Math.min(width - radius, d.x)); })
        .attr("cy", function(d) { return d.y = Math.max(radius, Math.min(height - radius, d.y)); });
    textElements.attr("x", function(d) { return d.x = Math.max(radius, Math.min(width - radius, d.x)); })
        .attr("y", function(d) { return d.y = Math.max(radius, Math.min(height - radius, d.y)); });

    linkElements.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });
  }
  /* {
    nodeElements
      .attr('cx', function (node) {
        return node.x
      })
      .attr('cy', function (node) {
        return node.y
      })
    textElements
      .attr('x', function (node) {
        return node.x
      })
      .attr('y', function (node) {
        return node.y
      })
    linkElements
      .attr('x1', function (link) {
        return link.source.x
      })
      .attr('y1', function (link) {
        return link.source.y
      })
      .attr('x2', function (link) {
        return link.target.x
      })
      .attr('y2', function (link) {
        return link.target.y
      })
  } */
  )
  simulation.force('link').links(links)
  simulation.alphaTarget(0.7).restart()
}
// last but not least, we call updateSimulation
// to trigger the initial render