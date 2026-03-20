document.addEventListener("DOMContentLoaded", function () {
  // 1. Data Parsing Safely
  const salesDataEl = document.getElementById("sales-data");
  if (!salesDataEl) return;
  const chartData = JSON.parse(salesDataEl.textContent);

  // 2. Neon Progress Bar Animation (Anti-Error Fix)
  const progressBar = document.getElementById("trustScoreBar");
  if (progressBar) {
    const score = progressBar.getAttribute("data-score");
    // Setting width via JS to bypass Jinja Syntax Errors
    setTimeout(() => {
      progressBar.style.width = score + "%";
    }, 500);
  }

  // 3. Chart.js Initialization
  const ctx = document.getElementById("sellerSalesChart").getContext("2d");
  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, "rgba(79, 172, 254, 0.4)");
  gradient.addColorStop(1, "rgba(79, 172, 254, 0)");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [
        {
          label: "Earnings (₹)",
          data: chartData.values,
          borderColor: "#4facfe",
          borderWidth: 4,
          pointBackgroundColor: "#fff",
          pointBorderColor: "#4facfe",
          pointRadius: 6,
          tension: 0.4,
          fill: true,
          backgroundColor: gradient,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: "rgba(0,0,0,0.03)" } },
        x: { grid: { display: false } },
      },
    },
  });
});
