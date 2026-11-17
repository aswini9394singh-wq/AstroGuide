// Light client-side help: show browser validation messages before submitting forms.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form").forEach(f => f.addEventListener("submit", e => {
    if (!f.checkValidity()) { e.preventDefault(); f.reportValidity(); }
  }));
});
