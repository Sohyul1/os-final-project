/* cpu_scheduling/static/js/cpu-form.js */

function toggleFields() {
    var algo = document.getElementById("algorithm").value;
    var needsPriority = ["priority_np", "priority_p"];
    var needsQuantum = ["rr"];

    document.getElementById("priority-field").style.display =
        needsPriority.indexOf(algo) !== -1 ? "block" : "none";
    document.getElementById("quantum-field").style.display =
        needsQuantum.indexOf(algo) !== -1 ? "block" : "none";
}

// Run on page load
toggleFields();