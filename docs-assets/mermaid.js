function renderMermaid() {
  if (typeof mermaid === "undefined") return;
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "loose",
    theme: document.body.getAttribute("data-md-color-scheme") === "slate" ? "dark" : "default",
  });
  mermaid.run({ querySelector: ".mermaid" });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(renderMermaid);
} else if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", renderMermaid);
} else {
  renderMermaid();
}
