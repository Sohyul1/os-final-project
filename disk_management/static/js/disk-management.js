/* disk_management/static/js/disk-management.js */

function toggleDirection() {
    var algoEl = document.getElementById("algorithm");
    if (!algoEl) return;

    var algo = algoEl.value;
    var needsDir = ["scan", "look"];

    var directionField = document.getElementById("direction-field");
    if (directionField) {
        directionField.style.display = needsDir.indexOf(algo) !== -1 ? "block" : "none";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    var algoEl = document.getElementById("algorithm");
    if (algoEl) {
        algoEl.addEventListener("change", toggleDirection);
        algoEl.addEventListener("input", toggleDirection);
        toggleDirection(); // run once on load for the current/selected value
    }

    var chartEl = document.getElementById("disk-chart-data");
    if (!chartEl) return; // Only run if results are present

    var chartData = JSON.parse(chartEl.getAttribute("data-chart"));
    var sequence = chartData.sequence;

    var labels = sequence.map(function (_, i) {
        return "Step " + i;
    });

    // Mark the initial head position point differently
    var pointColors = sequence.map(function (_, i) {
        return i === 0 ? "#e15759" : "#4e79a7";
    });
    var pointSizes = sequence.map(function (_, i) {
        return i === 0 ? 8 : 5;
    });

    new Chart(document.getElementById("diskChart"), {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Disk Head Position",
                    data: sequence,
                    borderColor: "#4e79a7",
                    backgroundColor: "rgba(78, 121, 167, 0.05)",
                    borderWidth: 2,
                    pointBackgroundColor: pointColors,
                    pointRadius: pointSizes,
                    pointBorderColor: "#333",
                    pointBorderWidth: 1,
                    fill: false,
                    tension: 0, // straight lines between points
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            return ctx.dataIndex === 0
                                ? "Initial Head: " + ctx.parsed.y
                                : "Cylinder: " + ctx.parsed.y;
                        },
                    },
                },
            },
            scales: {
                x: {
                    title: { display: true, text: "Service Order" },
                },
                y: {
                    title: { display: true, text: "Cylinder Number" },
                    beginAtZero: true,
                },
            },
        },
    });
});