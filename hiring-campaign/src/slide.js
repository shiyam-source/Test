// Shared slide runtime: fits headline lines to a target width and
// swaps the text wordmark for assets/logo.svg when that file exists.
window.slideReady = (async () => {
  await document.fonts.ready;

  for (const el of document.querySelectorAll("[data-fit]")) {
    const target = Number(el.dataset.fit);
    let size = 200;
    el.style.fontSize = size + "px";
    el.style.width = "max-content";
    size = size * target / el.getBoundingClientRect().width;
    el.style.width = "";
    el.style.fontSize = size.toFixed(1) + "px";
  }

  const logo = document.querySelector(".logo");
  if (logo) {
    const img = new Image();
    const loaded = new Promise((res) => { img.onload = () => res(true); img.onerror = () => res(false); });
    img.src = "assets/logo" + (logo.classList.contains("on-dark") ? "-white" : "") + ".svg";
    if (await loaded) logo.replaceChildren(img);
  }
  return true;
})();
