//-- String Method to Unescape Html Entities 
String.prototype.unescapeHtml = function () {
    var temp = document.createElement("div");
    temp.innerHTML = this;
    return temp.childNodes[0].nodeValue;
}

///////////-- Chart Setup --////////////

//-- Initialize geometry, format and colors
var diameter = 600,           // 856 | 960 ?
    format = d3.format(",d"),
//  color = d3.scale.category20c();
    color = d3.scale.linear()
      .domain([0.0,1.2,2.3,3.5,4.4,5.3,6.0])
      .range(["#993333", "red", "orange", "yellow", "green", "#88AAEE","#E898FF"]);

//-- The pack layout of d3 for packing hierarchies of
//-- circular nodes. [It will be used with flat data
//-- (depth of only one level) to make a bubble chart]
var bubble = d3.layout.pack()
    .sort(null)
    .size([diameter, diameter])
    .padding(1.5);

//-- Set up the svg for the chart
var svg = d3.select("#chart").append("svg")
    .attr("width", diameter)
    .attr("height", diameter)
    .attr("class", "center-block");



/////////-- Draw Each Node --//////////

//-- The following bubble.nodes() is where the layout magic happens.
//-- The passed data (movieData) needs special structure. For
//-- example, it has to have the {"children": array_of_objects}
//-- structure. Also, the objects in that array need to have
//-- a "value" attribute. Other attributes like x, y, r are
//-- calculated from this "value". The .filter following .data
//-- is also necessary, it won't work without it.

//-- Calculate the layout: determine the coordinates and 
//-- radii of every node and start entering elements.
console.log('yo')
console.log(window.movieData)
var node = svg.selectAll(".node")
    .data(bubble.nodes(window.movieData)         
    .filter(function(d) { return !d.children; }))
  .enter()

    //-- Link to detail view on click ("a" must come before
    //-- the elements to be drawn, like "g")
    .append("a")
    .attr("xlink:href", function(d) { return d.url; })

    //-- Enter the entire group of nodes and move each
    //-- node to thecalculated coordinates
    .append("g")
    .attr("class", "node")
    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

//-- Text that the browser shows when mouse hovers over a node
node.append("title")
    .text(function(d) { return d.name.unescapeHtml() +" ("+ d.unicode_stars +")"; });

//-- Draw the circles for all nodes with the already calculated radii
//-- (Add a small random element to the integer value for color purposes,
//-- this way there will be discretely different colors but with some
//-- fluctuation in shades of each discerete color)
node.append("circle")
    .attr("r", function(d) { return d.r; })
    .style("fill", function(d) { return color(d.score); });

//-- The text that permaently appears on the circle. Cut to fit.
node.append("text")
    .attr("dy", ".3em")
    .attr("class", "label")
    .style("text-anchor", "middle")
    .text(function(d) { return d.name.unescapeHtml().substring(0, d.r / 3); });



///////-- Final Frame Geometry --///////

//-- Set the heights of the divs to the diameter value
//-- of the chart (initialized at the beginning)
d3.select("#chart").style("height", diameter + "px");
d3.select("#chart_area").style("height", diameter + "px");
