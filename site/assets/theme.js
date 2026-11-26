/* Darstellung umschalten: auto → hell → dunkel.
   Speichert nichts im Browser. Die Wahl steht nur als ?theme=… in der Adresse
   und wird an die Links innerhalb dieser Website weitergegeben. */
(function () {
  var MODES = ["auto", "light", "dark"];
  var NAME = { auto: "auto (wie das System)", light: "hell", dark: "dunkel" };
  var ICON = {
    auto: '<circle cx="8" cy="8" r="6"/><path d="M8 2a6 6 0 0 1 0 12z" fill="currentColor" stroke="none"/>',
    light: '<circle cx="8" cy="8" r="2.8"/><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.4 1.4M11.6 11.6L13 13M3 13l1.4-1.4M11.6 4.4L13 3"/>',
    dark: '<path d="M13.5 10A6 6 0 0 1 6 2.5 6 6 0 1 0 13.5 10z"/>'
  };
  var root = document.documentElement;
  var mode = new URLSearchParams(location.search).get("theme");
  if (MODES.indexOf(mode) < 0) mode = "auto";

  function apply() {
    if (mode === "auto") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", mode);
  }
  apply();

  function withMode(href) {
    var u = new URL(href, location.href);
    if (u.protocol !== location.protocol || u.host !== location.host) return null;
    if (mode === "auto") u.searchParams.delete("theme");
    else u.searchParams.set("theme", mode);
    return u.href;
  }

  function relink() {
    var links = document.querySelectorAll("a[href]");
    for (var i = 0; i < links.length; i++) {
      var a = links[i], h = a.getAttribute("href");
      if (!h || h.charAt(0) === "#" || /^(mailto|tel|javascript):/i.test(h)) continue;
      var n = withMode(a.href);
      if (n) a.href = n;
    }
    var here = withMode(location.href);
    if (here && here !== location.href) try { history.replaceState(null, "", here); } catch (e) {}
  }

  function init() {
    var host = document.querySelector("header.vlb > div") || document.querySelector("header.top .wrap");
    if (!host) return;
    var b = document.createElement("button");
    b.type = "button";
    b.className = "tgl";
    function show() {
      var next = MODES[(MODES.indexOf(mode) + 1) % MODES.length];
      b.innerHTML = '<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true">' + ICON[mode] + "</svg>";
      b.title = "Darstellung: " + NAME[mode] + ", weiter mit " + NAME[next];
      b.setAttribute("aria-label", b.title);
    }
    b.addEventListener("click", function () {
      mode = MODES[(MODES.indexOf(mode) + 1) % MODES.length];
      apply();
      show();
      relink();
    });
    show();
    host.appendChild(b);
    relink();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
