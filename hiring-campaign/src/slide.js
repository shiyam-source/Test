// Shared slide runtime: fits headline lines to a target width.
window.slideReady = (async () => {
  await document.fonts.ready;
  await Promise.all([...document.images].map((img) => img.decode().catch(() => {})));

  for (const el of document.querySelectorAll("[data-fit]")) {
    const target = Number(el.dataset.fit);
    let size = 200;
    el.style.fontSize = size + "px";
    el.style.width = "max-content";
    size = size * target / el.getBoundingClientRect().width;
    el.style.width = "";
    el.style.fontSize = size.toFixed(1) + "px";
  }
  return true;
})();
