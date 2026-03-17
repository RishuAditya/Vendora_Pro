// Confirmation for sensitive actions
function confirmAction(message) {
  return confirm(message);
}

// Auto-hide Flash Messages after 3 seconds
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 3000);
  });
});

// Real-time Cart Total Calculation (Example logic)
console.log("Vendora Pro JS Loaded! 🚀");
