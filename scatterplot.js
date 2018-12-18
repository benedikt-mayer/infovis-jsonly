//width and height
var w = 600;
var h = 400;
var padding = 40;




var dataset = [];
//load data
d3.csv('scatterplot.csv', function (d) {
    //data.forEach(function(d) {
    //dataset.push(d.precipitation);

    console.log(dataset)
    return {
        x: d.x,
        y: d.y,
        name: d.Name,
        zeitung: d.Zeitung
    };
}, function (d) {
    dataset.push([Number(d.x), Number(d.y), d.Name,d.Zeitung]);
    console.log(dataset)

    //var color = d3.scaleOrdinal(d3.schemeCategory20);
    var cValue = function(d) { return d.Name;},
    color = d3.scaleOrdinal(d3.schemeCategory20)
    //scale function
    var xScale = d3.scaleLinear()
        .domain([0, 1])
        .range([padding, w - padding]);

    var yScale = d3.scaleLinear()
        .domain([0, 1])
        .range([h - padding, padding]);

    var xAxis = d3.axisBottom().scale(xScale).ticks(5);

    var yAxis = d3.axisLeft().scale(yScale).ticks(5);

    var svgElement = document.getElementById("vis-container").getElementsByTagName("svg");
    if (svgElement.length == 0) {
        //create svg element
        var svg = d3.select("#vis-container")
            .append("svg")
            .attr("width", w)
            .attr("height", h);

        //x axis
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + (h - padding) + ")")
            .call(xAxis)
            .append("text")
            .attr("class", "label")
            .attr("x", w)
            .attr("y", -6)
            .style("text-anchor", "end")
            .text("Aggressiveness");

        //y axis
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + padding + ", 0)")
            .call(yAxis)
            .append("text")
            .attr("class", "label")
            .attr("y", 6)
            .attr("x", 30)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .text("Friendliness");

    } else {
        var svg = d3.select("#vis-container").select("svg")
    }
    // add the tooltip area to the webpage
    var tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);


    // draw dots
    svg.selectAll(".dot")
        .data(dataset)
        .enter()
        .append("circle")
        .attr("class", "dot")
        .attr("r", 3.5)
        .attr('fill', function(d, i) { 
            return color(d[2]);
          })
        .attr("cx", function (d) {
            return xScale(d[0]);
        })
        .attr("cy", function (d) {
            return yScale(d[1]);
        })
        .on("mouseover", function (d) {
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(d[2] + "<br/>"+d[3] + "<br/> (" + d[0]
                + ", " + d[1] + ")")
                .style("left", (d3.event.pageX + 10) + "px")
                .style("top", (d3.event.pageY - 40) + "px");
        })
        .on("mouseout", function (d) {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });



    // draw legend
    var legend = svg.selectAll(".legend")
        .data(color.domain())
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function (d, i) { return "translate(0," + i * 20 + ")"; });

    // draw legend colored rectangles
    legend.append("rect")
        .attr("x", w - 18)
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", color);

    // draw legend text
    legend.append("text")
        .attr("x", w - 24)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function (d) { return d; })

});