// Optimed CRM — interceptează click pe Number Card "Pacienți de contactat azi"
// și redirecționează către pagina contacts-today (în loc de lista filtrată Patient).
//
// Frappe Number Cards merg by default la /app/{doctype} cu filtre,
// dar pentru acest card vrem o pagină custom de acțiune.

(function () {
	"use strict";

	const TARGET_LABEL = "Pacienți de contactat azi";
	const TARGET_ROUTE = "contacts-today";

	function attachInterceptor() {
		// Caută toate widget-urile de tip Number Card
		document.querySelectorAll(".widget.number-widget-box, .widget.number-card").forEach(function (el) {
			if (el.dataset.optimedHookAttached === "1") return;

			// Detect label (titlul cardului)
			const labelEl = el.querySelector(".widget-title, .number-label, .widget-head-text");
			if (!labelEl) return;
			const label = labelEl.textContent.trim();

			if (label === TARGET_LABEL) {
				el.dataset.optimedHookAttached = "1";
				el.style.cursor = "pointer";
				el.addEventListener("click", function (ev) {
					ev.preventDefault();
					ev.stopImmediatePropagation();
					ev.stopPropagation();
					if (window.frappe && frappe.set_route) {
						frappe.set_route(TARGET_ROUTE);
					} else {
						window.location.href = "/app/" + TARGET_ROUTE;
					}
				}, true); // capture phase — rulează înaintea handler-ului default
			}
		});
	}

	// Atașează la pornirea aplicației + la fiecare schimbare de rută (workspace re-render)
	function init() {
		attachInterceptor();

		// Re-rulează la fiecare 2 sec (workspace-ul se poate re-render)
		setInterval(attachInterceptor, 2000);

		// Hook explicit pentru route changes
		if (window.frappe && frappe.router && frappe.router.on) {
			frappe.router.on("change", function () {
				setTimeout(attachInterceptor, 500);
			});
		}
	}

	// Așteaptă DOM ready + Frappe ready
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
