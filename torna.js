/* Pulsante «Sito»: se la pagina è stata aperta in una scheda nuova prova a chiuderla (si torna così alla scheda del sito),
   altrimenti porta al sito nella stessa scheda. Si usa con  <a href="../" data-torna>Sito</a>. Autore: Danilo D'Auria · MIT */
(function () {
  document.addEventListener("click", function (e) {
    var a = e.target.closest ? e.target.closest("[data-torna]") : null; if (!a) return;
    e.preventDefault();
    var dove = a.getAttribute("href") || "/";
    try { if (window.history.length <= 2) window.close(); } catch (x) {}
    setTimeout(function () { location.href = dove; }, 250);
  }, true);
})();
