//width and height
var w = 600;
var h = 400;
var padding = 40;
var dataset = [];

const SPD = "SPD"
const AfD = "SPD"
const CDU = "SPD"

$(function () {
    let checkvalue = $('input[type=radio][name=Scatter]:checked').val()
    console.log("initial scatter: " + checkvalue)
    fetchAsyncScatter(`http://127.0.0.1:5002/${checkvalue}`);
});

$('input[type=radio][name=Scatter]').on('change', function() {
    console.log("changed in scatter: " + $(this).val())
    fetchAsyncScatter(`http://127.0.0.1:5002/${$(this).val()}`);
});

async function fetchAsyncScatter(url) {
    console.log("async scatter")
    $("#vis-container").find("circle").remove()
    let response = await fetch(url, {
        headers: {
            'Content-type': 'charset=UTF-8'
        },
        mode: 'cors'
    });
    // let text = await response.text();
    let data = await response.json();
    console.log(data);
    formattedData = data.map(element => {
        return [
            element.results.aggressive.percentile / 100,
            element.results.positive.percentile / 100,
            element.author,
            element.newsportal,
            element.title,
            element.date
        ]
    })
    // formattedData = {
    //     x: data.aggressive,
    //     y: data.positive,
    //     Name: data.Name,
    //     Zeitung: data.Zeitung
    // }
    // console.log(formattedData);
    dod3magic(formattedData);
}


//load data
function dod3magic(data) {
    // dataset.push([Number(d.x), Number(d.y), d.Name, d.Zeitung]);
    dataset = data;
    console.log(dataset)

    //var color = d3.scaleOrdinal(d3.schemeCategory20);
    var cValue = function (d) {
            return d.Zeitung;
        },
        color = d3.scaleOrdinal(d3.schemeCategory10).range(d3.schemeCategory10);
    //scale function
    var xScale = d3.scaleLinear()
        .domain([0, 1])
        .range([padding, w - padding]);

    var yScale = d3.scaleLinear()
        .domain([0, 1])
        .range([h - padding, padding]);

    var margin = {
            top: 20,
            right: 20,
            bottom: 50,
            left: 70
        },
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

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
            .attr("y", 30)
            .style("text-anchor", "end")
            .style("fill", "black")
            .text("Aggressiveness");

        //y axis
        svg.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + padding + ", 0)")
            .call(yAxis)
            .append("text")
            .style("text-anchor", "middle")
            .attr("class", "label")
            .attr("y", 20)
            .attr("x", 20)
            .attr("dy", ".71em")
            .style("text-anchor", "end")
            .style("fill", "black")
            .text("Friendliness");

    } else {
        var svg = d3.select("#vis-container").select("svg")
    }
    // add the tooltip area to the webpage
    var tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    console.log("color domain before: " + color.domain())

    // draw dots
    svg.selectAll(".dot")
        .data(dataset)
        .enter()
        .append("circle")
        .attr("class", "dot")
        .attr("r", 3.5)
        .attr('fill', function (d, i) {
            return color(d[3]);
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
                .style("opacity", 1);
            tooltip.html(d[2] + "<br/>" + d[3] + "<br/>" + d[4] + "<br/>" + d[5] + "<br/> (" + d[0] +
                    ", " + d[1] + ")")
                .style("left", (d3.event.pageX + 20) + "px")
                .style("top", (d3.event.pageY - 200) + "px")
                .style("border", "1px solid black")
                .style("border-radius", "4px")
                .style("padding", "0.8rem")
                .style("height", "fit-content")
                .style("background-color", "white");
        })
        .on("mouseout", function (d) {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });

    console.log("color domain" + color.domain())

    // draw legend
    var legend = svg.selectAll(".legend")
        .data(color.domain())
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function (d, i) {
            return "translate(0," + i * 20 + ")";
        });

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
        .text(function (d) {
            return d;
        })

}