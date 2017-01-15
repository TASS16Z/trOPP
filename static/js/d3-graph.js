String.prototype.trunc = String.prototype.trunc ||
  function(n){
    return (this.length > n) ? this.substr(0,n-1)+'...' : this;
  };

Array.prototype.replaceContents = function (array2) {
  var newContent = array2.slice(0);
  this.length = 0;
  this.push.apply(this, newContent);
};

var color = d3.scale.category10();
var width = 900, height = 700, radius = 6, node, link;

var x = d3.scale.linear()
  .domain([0, width])
  .range([0, width]);

var y = d3.scale.linear()
  .domain([0, height])
  .range([height, 0]);

var svg;
var force = d3.layout.force()
  .gravity(0.5)
  .linkStrength(0.3)
  .charge(-1300)
  .size([width, height])
  .friction(0.5)
  .linkDistance(40)
  .on("tick", tick);

var nodes = force.nodes(),
  links = force.links(); 
// Add and remove elements on the graph object
function addNode(n) {
  nodes.push(n);
  update();
};

function findNode(id) {
  for (var i in nodes) {
    if (nodes[i]["id"] === id) return nodes[i];
  }
  ;
};

function findNodeIndex(id) {
  for (var i = 0; i < nodes.length; i++) {
    if (nodes[i].id == id) {
      return i;
    }
  }
  ;
};
function removeAllLinks(){
  links.splice(0,links.length);
  update();
};

function removeAllNodes(){
  nodes.splice(0,nodes.length);
  update();
};

function updateGraph(url) {
  d3.json(url, function(error, json) {
    nodes.replaceContents(json.nodes);
    templinks = []
    json.links.forEach(function(e) { 
      templinks.push({source: findNode(e.source), target: findNode(e.target),
                      weight: parseInt(e.weight)});
    });
    links.replaceContents(templinks);
    update();
  });
}

function update() {
  // Update the links…
  link = svg.selectAll("line.link")
    .data(links, function (d) {
      return d.source.id + "-" + d.target.id;
    });
  // Enter any new links.
  link.enter().insert("svg:line", ".node")
    .attr("id", function (d) {
      return d.source.id + "-" + d.target.id;
    })
    .attr("class", "link")
    .style("stroke-width", function (d) {
      return d.weight;
    })
    .attr("x1", function(d) { return d.source.x; })
    .attr("y1", function(d) { return d.source.y; })
    .attr("x2", function(d) { return d.target.x; })
    .attr("y2", function(d) { return d.target.y; });
  // Exit any old links.
  link.exit().remove();
  // Update the nodes…
  node = svg.selectAll(".node")
    .data(nodes, function (d) {
      return d.id;
    });

  var nodeEnter = node.enter().append("g")
    .attr("class", "node")
    .on("click", nodeClick)
    .call(force.drag);

  nodeEnter.append("svg:circle")
    .attr("r", setNodeSize)
    .attr("id", function (d) {
      return "Node;" + d.id;
    })
    .attr("class", "nodeStrokeClass")
    .attr("fill", function(d) { return color(d['class-name']); });

  nodeEnter.append("svg:text")
    .attr("dy", 10)
    .attr("text-anchor", "middle")
    .text(function(d) { return d.name.trunc(10) });

  nodeEnter.append("title").text(function(d) { return d.name;} );

  node.exit().remove();
  force.start();
};

function tick() {
  link.attr("x1", function(d) { return x(d.source.x); })
    .attr("y1", function(d) { return y(d.source.y); })
    .attr("x2", function(d) { return x(d.target.x); })
    .attr("y2", function(d) { return y(d.target.y); });
  node.attr("transform", function(d) {
    return "translate(" + x(d.x) + "," + y(d.y) + ")"; });
  update();
};

function nodeClick(d){
  $.getJSON("api/details?class=" + d['class-name'] + "&handle_id=" + d.id,
    function(json) {
      var items = [];
      $.each(json, function(key, val) {
        items.push("<dt>" + key + "</dt><dd>" + val + "</dd>");
      });
      var details = $("<d1/>", {
        html: items.join("")
      });
      $("div.detail-panel").html(details);
      $.getJSON("api/node_click?class=" + d['class-name'] + "&handle_id=" + d.id,
        function(json) {
          nodes.replaceContents(json.nodes);
          templinks = []
          json.links.forEach(function(e) { 
            templinks.push({source: findNode(e.source), target: findNode(e.target),
              weight: parseInt(e.weight)});
          });
          links.replaceContents(templinks);
          update();
        });
    });

};

function setNodeSize(d){
  if(d['class-name']=='OPP') return Math.max(10, d.average_salary/100);
  return 20;
};
