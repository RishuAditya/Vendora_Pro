// --- VENDORA PRO MASTER JS ---

// 1. Variant Selection Logic (Product Detail Page)
// Isse 1kg, 2kg ya S, M, L select karne par button active dikhega
function setV(btn, val) {
  // Saare buttons se 'active' class hatao
  document
    .querySelectorAll(".v-btn")
    .forEach((x) => x.classList.remove("active"));
  // Clicked button pe 'active' class lagao
  btn.classList.add("active");
  // Hidden input ki value badlo taaki backend ko pata chale kya select hua hai
  const input = document.getElementById("v_in");
  if (input) input.value = val;
}

// 2. Multi-Tab Session Sync (Security Logic)
window.addEventListener("storage", (event) => {
  // Agar kisi ek tab mein logout hua, toh saare tabs auto-refresh honge
  if (event.key === "logout-event") {
    window.location.reload();
  }
});

// Logout click hone par signal bhejo
document.addEventListener("DOMContentLoaded", function () {
  const logoutBtn = document.querySelector(".text-danger");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      localStorage.setItem("logout-event", Date.now());
    });
  }

  // 3. Auto-hide Flash Messages (Toasts) after 3 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 3000);
  });
});

// 4. Confirmation for sensitive actions (Delete/Cancel)
function confirmAction(message) {
  return confirm(message);
}

// 5. Seller Card Toggle (Withdrawal Modal)
function toggleSellerCardForm() {
  const selector = document.getElementById("sellerCardSelector");
  const form = document.getElementById("sellerNewCardForm");
  if (selector && form) {
    form.style.display = selector.value === "new" ? "block" : "none";
  }
}

console.log("Vendora Pro Engine Active! 🚀");
