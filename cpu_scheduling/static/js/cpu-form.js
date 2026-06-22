/* cpu_scheduling/static/js/cpu-form.js */

function toggleFields() {
    var algoEl = document.getElementById("algorithm");
    if (!algoEl) return;

    var algo = algoEl.value;
    var needsPriority = ["priority_np", "priority_p"];
    var needsQuantum = ["rr"];

    var priorityField = document.getElementById("priority-field");
    var quantumField = document.getElementById("quantum-field");

    if (priorityField) {
        priorityField.style.display = needsPriority.indexOf(algo) !== -1 ? "block" : "none";
    }
    if (quantumField) {
        quantumField.style.display = needsQuantum.indexOf(algo) !== -1 ? "block" : "none";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    var algoEl = document.getElementById("algorithm");
    if (!algoEl) return;

    algoEl.addEventListener("change", toggleFields);
    algoEl.addEventListener("input", toggleFields);

    // Run once on load so the correct fields show for the current/selected value
    toggleFields();
});