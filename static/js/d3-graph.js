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
var width = 900, height = 700, radius = 6, node, min, max, link;

var x = d3.scale.linear()
  .domain([0, width])
  .range([0, width]);

var y = d3.scale.linear()
  .domain([0, height])
  .range([height, 0]);

var lineScale = d3.scale.pow()
  .domain([3, 10])
  .range([0.5, 8]);

var nodeSizeScale = d3.scale.linear()
  .domain([0, 100000])
  .range([5, 50])
  .clamp(true);

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
      return lineScale(d.weight);
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
    .attr("dx", 20)
    .attr("text-anchor", "left")
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
      var details = getJSONDetails(json);
      $("div.detail-panel").html(details);

      $.getJSON("api/node_click?class=" + d['class-name'] + "&handle_id=" + d.id,
        function(json) {
          nodes.replaceContents(json.nodes);
          templinks = []
          min = 100, max = 0;
          json.links.forEach(function(e) { 
            max = e.weight > max ? e.weight : max;
            min = e.weight < max ? e.weight : min;
            templinks.push({source: findNode(e.source), target: findNode(e.target),
              weight: parseInt(e.weight)});
          });
          lineScale.domain([min, max]);
          links.replaceContents(templinks);
          update();
        });
    });

};

var LOCALE = {
  "OPP" : "Organizacja Pożytku Publicznego",
  "CITY" : "Miasto",
  "DISTRICT" : "Powiat",
  "VOIVODESHIP" : "Województwo",
  "LEGALFORM" : "Forma prawna",
  "PUBLICBENEFITAREA" : "Strefa pożytku publicznego",
  "AIM" : "Cel statutowy",
  "NAME": "Nazwa",
  "AVERAGE_SALARY": "Średnie wynagrodzenie",
  "NO_OF_BENEFICIARIES": "Liczba odbiorców działań organizacji",
  "SALARIES": "Odsetek budżetu przeznaczony na wynagrodzenia",
  "NO_OF_EMPLOYEES": "Liczba pracowników"
};

function gettext(string) {
  return LOCALE[string.toUpperCase()] ? LOCALE[string.toUpperCase()] : string;
}
function getJSONDetails(json){
  var items = [];
  items.push("<dt><h5>" + gettext(json["class-name"]) + "<h5></dt>");
  items.push("<dd><h4><strong>" + gettext(json["name"]) + "</strong><h4></dd>");
  items.push("<hr>");
  $.each(json, function(key, val) {
    if(["class-name", "model_id", "id", "name"].indexOf(key) < 0)
      items.push("<dt>" + gettext(key) + "</dt><dd>" + val + "</dd>");
  });
  items.push("<hr>");
  if(!isNaN(json["model_id"]))
    items.push("<a href='/OPP/"+json["model_id"]+"'>Więcej szczegółów</a>");
  var details = $("<dl/>", {
    html: items.join("")
  });
  return details;
}

function setNodeSize(d){
  if(d['class-name']=='OPP') return Math.max(10, nodeSizeScale(d.average_salary));
  return 20;
};
