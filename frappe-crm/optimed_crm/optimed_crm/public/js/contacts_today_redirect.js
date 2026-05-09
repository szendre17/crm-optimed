// Optimed CRM — overrides UI:
// 1. Workspace /app/optimed-crm → redirect automat la /app/optimed-dashboard
// 2. Click pe Number Card "Pacienți de contactat azi" → /app/contacts-today

console.log("[Optimed] JS loaded at", new Date().toISOString());

// =========================================================
// PARTEA 1: Redirect workspace
// =========================================================

(function pollAndRedirect() {
	try {
		if (window.frappe && frappe.get_route) {
			const route = frappe.get_route();
			if (
				route &&
				route.length >= 2 &&
				(route[0] === "Workspaces" || route[0] === "workspace") &&
				(route[1] === "Optimed CRM" || route[1] === "optimed-crm")
			) {
				console.log("[Optimed] Workspace detected, redirecting to dashboard. Route was:", route);
				frappe.set_route("optimed-dashboard");
				return; // stop polling după redirect reușit
			}
		}
	} catch (e) {
		console.error("[Optimed] Redirect check error:", e);
	}
	// Polling continuu — capturăm și navigările ulterioare la workspace
	setTimeout(pollAndRedirect, 500);
})();

// =========================================================
// PARTEA 2: Override Number Card "Pacienți de contactat azi"
// =========================================================

(function () {
	"use strict";

	const TARGET_LABEL = "Pacienți de contactat azi";
	const TARGET_ROUTE = "contacts-today";

	function attachInterceptor() {
		document.querySelectorAll(".widget.number-widget-box, .widget.number-card").forEach(function (el) {
			if (el.dataset.optimedHookAttached === "1") return;
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
				}, true);
			}
		});
	}

	function init() {
		attachInterceptor();
		setInterval(attachInterceptor, 2000);
		if (window.frappe && frappe.router && frappe.router.on) {
			frappe.router.on("change", function () {
				setTimeout(attachInterceptor, 500);
			});
		}
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();
