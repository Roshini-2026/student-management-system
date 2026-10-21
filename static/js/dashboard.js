document.addEventListener("DOMContentLoaded", function () {
    const dataElement = document.getElementById("course-chart-data");
    const canvas = document.getElementById("course-chart");
    if (!dataElement || !canvas || typeof Chart === "undefined") {
        return;
    }
    const data = JSON.parse(dataElement.textContent);
    new Chart(canvas, {
        type: "bar",
        data: {
            labels: data.labels,
            datasets: [{ label: "Students", data: data.values, backgroundColor: "#0d6efd" }],
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
        },
    });
});