/* memory_management/static/js/memory-management.js */

(function () {
    var el = document.getElementById("mem-chart-data");
    if (!el) return; // Only run if results are present

    var datasets = JSON.parse(el.getAttribute("data-datasets"));
    var labels = JSON.parse(el.getAttribute("data-labels"));

    var chartDatasets = datasets.map(function (ds) {
        return {
            label: ds.label,
            data: ds.data,
            backgroundColor: ds.backgroundColor,
            borderColor: ds.borderColor,
            borderWidth: ds.borderWidth,
            segStart: ds.segment_start,
            segSize: ds.segment_size,
            segLabel: ds.segment_label,
        };
    });

    new Chart(document.getElementById("memoryChart"), {
        type: "bar",
        data: {
            labels: labels,
            datasets: chartDatasets,
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            var ds = ctx.dataset;
                            return ds.segLabel + " | Start: " + ds.segStart + " KB | Size: " + ds.segSize + " KB";
                        },
                    },
                },
            },
            scales: {
                x: {
                    stacked: true,
                    title: { display: true, text: "Memory Address (KB)" },
                    beginAtZero: true,
                },
                y: { stacked: true },
            },
        },
        plugins: [{
            id: "segmentLabels",
            afterDatasetsDraw: function (chart) {
                var ctx2 = chart.ctx;
                chart.data.datasets.forEach(function (ds, i) {
                    var meta = chart.getDatasetMeta(i);
                    if (!meta.hidden && meta.data.length > 0) {
                        var bar = meta.data[0];
                        var barWidth = bar.width;
                        if (barWidth > 30) {
                            ctx2.save();
                            ctx2.fillStyle = "#000";
                            ctx2.font = "11px sans-serif";
                            ctx2.textAlign = "center";
                            ctx2.textBaseline = "middle";
                            ctx2.fillText(ds.segLabel, bar.x - barWidth / 2, bar.y);
                            ctx2.restore();
                        }
                    }
                });
            },
        }],
    });
})();