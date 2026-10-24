document.querySelectorAll(".codebox").forEach((box) => {
  const button = box.querySelector("button");
  const code = box.querySelector("pre");
  if (!button || !code) return;
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(code.innerText);
      button.textContent = "Copied";
    } catch {
      button.textContent = "Select + copy";
    }
    setTimeout(() => (button.textContent = "Copy"), 1600);
  });
});
