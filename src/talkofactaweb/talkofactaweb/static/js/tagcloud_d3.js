/**
 * D3TagCloud adapted for the Talk of Europe project.
 *
 * Copyright 2015, Konstantin Tretyakov, Ilya Kuzovkin, Aleksandr Tkachenko.
 * License: MIT
 */
function D3TagCloud(rootElement) {
    var self = this;
    this.rootElement = d3.select(rootElement);
    this.words = null;

    this.fill = d3.scale.ordinal()
        .domain(d3.range(11))
        .range(colorbrewer.Spectral[11]);
    this.width = 800;
    this.height = 500;
    this.x_offset = this.width/2;
    this.y_offset = this.height/2;
    this.layout = d3.layout.cloud()
                    .size([this.width, this.height])
                    .padding(2)
                    .rotate(function() { return 0; })
                    .font("Impact")
                    .fontSize(function(d) { return d.size; })
                    .on("end", function(w) { self._drawCloud(w) });

    this.rootElement.append("svg")
        .attr("width", self.width)
        .attr("height", self.height)
        .append("g")
        .attr("transform", "translate(" + self.x_offset + ", " + self.y_offset + ")")

    this.rootG = this.rootElement.select("g");
}

D3TagCloud.prototype.init = function(words) {
    var self = this;
    this.layout
        .stop()
        .words(words)
        .start();
}

/**
 * Invoked for words after they are laid out.
 */
D3TagCloud.prototype._drawCloud = function(words) {
    var self = this;
    var sel = this.rootG.selectAll("text")
            .data(words, function(d) { return d.text });
    sel.transition()
        .duration(500)
        .style("font-size", function(d) { return d.size + "px"; })
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        });
    sel.enter().append("text")
        .text(function(d) { return d.text; })
        .style("font-family", "Impact")
        .attr("class", "tag")
        .style("fill", function(d, i) {
                            var cid = 10 - Math.floor((d.size - 12)/(70-12)*10);
                            if (cid >= 5 && cid <= 6) cid = 7;
                            return  self.fill(cid);
                        })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .transition()
            .duration(500)
            .style("font-size", function(d) { return d.size + "px"; });
    sel.exit().transition()
        .duration(500)
        .style("font-size", "0px")
        .remove();
}

D3TagCloud.prototype.update = function(words) {
    if (this.words == null) {
        this.init(words);
        return;
    }
}