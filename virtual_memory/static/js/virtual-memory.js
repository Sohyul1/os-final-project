/* virtual_memory/static/js/virtual-memory.js */

(function () {
    var el = document.getElementById("chart-data");
    if (!el) return; // Only run if results are present

    var steps = JSON.parse(el.getAttribute("data-steps"));
    var faults = JSON.parse(el.getAttribute("data-faults"));
    var summary = JSON.parse(el.getAttribute("data-summary"));

    // ── Line chart: cumulative faults ──────────────────────
    new Chart(document.getElementById("faultLineChart"), {
        type: "line",
        data: {
            labels: steps,
            datasets: [
                {
                    label: "Cumulative Page Faults",
                    data: faults,
                    borderColor: "#e15759",
                    backgroundColor: "rgba(225, 87, 89, 0.1)",
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: "#e15759",
                    fill: true,
                    tension: 0.1,
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
                            return "Faults so far: " + ctx.parsed.y;
                        },
                    },
                },
            },
            scales: {
                x: {
                    title: { display: true, text: "Step (Page Reference)" },
                    ticks: {
                        callback: function (val, i) {
                            return "Step " + steps[i];
                        },
                    },
                },
                y: {
                    title: { display: true, text: "Cumulative Faults" },
                    beginAtZero: true,
                    ticks: { stepSize: 1 },
                },
            },
        },
    });

    // ── Bar chart: faults vs hits ───────────────────────────
    new Chart(document.getElementById("summaryBarChart"), {
        type: "bar",
        data: {
            labels: summary.labels,
            datasets: [
                {
                    label: "Count",
                    data: summary.data,
                    backgroundColor: summary.colors,
                    borderColor: "#333",
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 },
                    title: { display: true, text: "Count" },
                },
            },
        },
    });
})();