/* Il sito funziona anche senza Internet. Strategia semplice e sicura:
   - pagine e dati del sito: prima la rete (sempre aggiornati), se manca Internet la copia salvata;
   - tutto il resto (GitHub, comparatori…): solo rete.
   Autore: Danilo D'Auria · licenza MIT */
var VERSIONE = "dd-2026-11-08b";
var BASE = [
  "./", "index.html", "fenice.svg", "manifest.webmanifest", "bandi.json", "offerte.json", "progetti.json", "casi.json", "novita.json", "prenota.json", "pdf/info.json",
  "icone/icona-192.png", "icone/icona-512.png", "icone/apple-touch-icon.png",
  "fonti/fonti.css", "fonti/atkinson-400.woff2", "fonti/atkinson-400-ext.woff2", "fonti/atkinson-700.woff2", "fonti/atkinson-700-ext.woff2", "fonti/atkinson-400i.woff2", "fonti/atkinson-400i-ext.woff2",
  "fonti/youngserif-400.woff2", "fonti/youngserif-400-ext.woff2", "fonti/jetbrains-400.woff2", "fonti/jetbrains-400-ext.woff2", "fonti/jetbrains-600.woff2", "fonti/jetbrains-600-ext.woff2",
  "guide/backup.html", "guide/truffe.html", "guide/vendere-donare.html", "guide/password.html", "guide/pc-veloce.html",
  "i18n/en.json", "i18n/fr.json", "i18n/es.json", "i18n/de.json", "i18n/ro.json",
  "scheda/", "pdf/leggi.html", "vista.html", "torna.js"
];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(VERSIONE).then(function (c) {
    return Promise.all(BASE.map(function (u) { return c.add(u).catch(function () {}); }));
  }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (k) {
    return Promise.all(k.filter(function (n) { return n !== VERSIONE; }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  var r = e.request; if (r.method !== "GET") return;
  var u = new URL(r.url);
  if (u.origin === location.origin) {
    e.respondWith(fetch(r).then(function (risp) {
      if (risp && risp.ok && !u.pathname.endsWith(".pdf") && !u.pathname.endsWith(".mp4")) {
        var copia = risp.clone(), chiave = u.search ? u.origin + u.pathname : r; caches.open(VERSIONE).then(function (c) { c.put(chiave, copia); });
      }
      return risp;
    }).catch(function () {
      return caches.match(r, { ignoreSearch: true }).then(function (m) {
        return m || (r.mode === "navigate" ? caches.match("./") : Response.error());
      });
    }));
  }
});
