/* cpu_scheduling/static/js/gantt-chart.js */

(function () {
    var el = document.getElementById("chart-data");
    if (!el) return; // Only run if results are present

    var ganttData = JSON.parse(el.getAttribute("data-gantt"));
    var uniquePids = JSON.parse(el.getAttribute("data-pids"));

    var palette = [
        "#4e79a7",
        "#f28e2b",
        "#e15759",
        "#76b7b2",
        "#59a14f",
        "#edc948",
        "#b07aa1",
        "#ff9da7",
        "#9c755f",
        "#bab0ac",
    ];

    var colorMap = {};
    uniquePids.forEach(function (pid, i) {
        colorMap[pid] = palette[i % palette.length];
    });

    var labels = ganttData.map(function (_, i) {
        return "#" + (i + 1);
    });
    var offsets = ganttData.map(function (d) {
        return d.start;
    });
    var durations = ganttData.map(function (d) {
        return d.duration;
    });
    var bgColors = ganttData.map(function (d) {
        return colorMap[d.pid];
    });
    var pidLabels = ganttData.map(function (d) {
        return d.pid;
    });

    new Chart(document.getElementById("ganttChart"), {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Offset",
                    data: offsets,
                    backgroundColor: "rgba(0,0,0,0)",
                    borderWidth: 0,
                },
                {
                    label: "Execution",
                    data: durations,
                    backgroundColor: bgColors,
                    borderColor: "#333",
                    borderWidth: 1,
                },
            ],
        },
        options: {
            indexAxis: "y",
            responsive: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            if (ctx.datasetIndex === 0) {
                                return null;
                            }
                            var i = ctx.dataIndex;
                            return (
                                pidLabels[i] +
                                "  [" +
                                offsets[i] +
                                " → " +
                                (offsets[i] + durations[i]) +
                                "]"
                            );
                        },
                    },
                },
            },
            scales: {
                x: {
                    stacked: true,
                    title: { display: true, text: "Time" },
                    beginAtZero: true,
                },
                y: {
                    stacked: true,
                    title: { display: true, text: "Slot" },
                },
            },
        },
        plugins: [
            {
                id: "pidLabels",
                afterDatasetsDraw: function (chart) {
                    var ctx2 = chart.ctx;
                    var meta = chart.getDatasetMeta(1);
                    meta.data.forEach(function (bar, i) {
                        ctx2.save();
                        ctx2.fillStyle = "#fff";
                        ctx2.font = "bold 12px sans-serif";
                        ctx2.textAlign = "center";
                        ctx2.textBaseline = "middle";
                        ctx2.fillText(
                            pidLabels[i],
                            bar.x - (bar.width / 2 || 0),
                            bar.y,
                        );
                        ctx2.restore();
                    });
                },
            },
        ],
    });
})();