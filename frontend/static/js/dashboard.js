document.addEventListener("DOMContentLoaded", function () {
  // 1. Progress Bar Logic
  const scoreBar = document.getElementById("trustScoreBar");
  if (scoreBar) {
    const score = scoreBar.getAttribute("data-score");
    setTimeout(() => {
      scoreBar.style.width = score + "%";
    }, 300);
  }

  // 2. Chart.js Logic (The REAL FIX)
  const ctx = document.getElementById("sellerSalesChart");
  if (ctx) {
    const labels = JSON.parse(ctx.getAttribute("data-labels"));
    const values = JSON.parse(ctx.getAttribute("data-values"));

    new Chart(ctx.getContext("2d"), {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Daily Revenue",
            data: values,
            borderColor: "#007bff",
            borderWidth: 4,
            fill: true,
            backgroundColor: "rgba(0, 123, 255, 0.1)",
            tension: 0.4,
            pointRadius: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true }, x: { grid: { display: false } } },
      },
    });
  }
});
