String.prototype.trunc = String.prototype.trunc ||
  function(n){
    return (this.length > n) ? this.substr(0,n-1)+'...' : this;
  };

var color = d3.scale.category10();
var width = 700, height = 700, graph, node, link;

var force = d3.layout.force()
  .size([width, height])
  .on("tick", tick)
  .charge(-400)
  .gravity(0.1)
  .friction(0.5)
  .linkDistance(50);

function updateGraph(url, isDirect) {
  d3.json(url + "?isDirect=" + isDirect, function(error, g) {
    var nodeMap = {};
    g.nodes.forEach(function(x) { nodeMap[x.id] = x; });
    g.links = g.links.map(function(x) {
      return {
        source: g.nodes.indexOf(nodeMap[x.source]),
        target: g.nodes.indexOf(nodeMap[x.target])
      };
    });
    graph = g;
    update();
  });
}

function update() {
  link = svg.selectAll("line.link")
    .remove();
  node = svg.selectAll(".node")
    .remove();
  // Start the force layout.
  force
    .nodes(graph.nodes)
    .links(graph.links)
    .start();
  // Update the links…
  link = svg.selectAll("line.link")
    .data(graph.links);//, function(d) { return d.target.id; });
  // Enter any new links.
  link.enter().insert("svg:line", ".node")
    .attr("class", "link")
    .attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });
  // Exit any old links.
  link.exit().remove();
  // Update the nodes…
  node = svg.selectAll(".node")
    .data(graph.nodes);

  var nodeE = node.enter();

  var nodeG = nodeE.append("g")
    .attr("class", "node")
    .call(force.drag);

  nodeG.append("circle")  
    .attr("r", 10)
  //    .on("click", click)
    .style("fill", function(d) { return color(d['class-name']);});

  nodeG.append("text")
    .attr("dy", 10 + 15)
    .attr("text-anchor", "middle")
    .text(function(d) { return d.name.trunc(10) });

  node.exit().remove();

};

function tick() {
  link.attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });

  node.attr("transform", function(d) {
    return "translate(" + d.x + "," + d.y + ")"; });
};
