document.addEventListener("DOMContentLoaded", function () {
  const printButton = document.getElementById("printBtn");

  if (printButton) {
    printButton.addEventListener("click", function () {
      // Simply trigger the browser's print dialog
      window.print();
    });
  }

  console.log("Invoice Logic Loaded! 📄");
});
