// Copyright (c) 2026, Optimed Toplița
// Pagina Dashboard Optimed — UI hibrid + grafic anual cu selector ani

frappe.pages['optimed-dashboard'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Dashboard Optimed',
		single_column: true
	});

	new OptimedDashboard(page);
};


const AUTO_REFRESH_INTERVAL_MS = 5 * 60 * 1000;  // 5 minute


// ============================================================================
// HELPER: Construirea URL-urilor cu filtre Frappe
// ============================================================================

function buildListUrl(doctype, filters) {
	const params = new URLSearchParams();
	for (const [key, value] of Object.entries(filters)) {
		if (Array.isArray(value)) {
			params.append(key, JSON.stringify(value));
		} else {
			params.append(key, value);
		}
	}
	const query = params.toString();
	const slug = doctype.toLowerCase().replace(/ /g, '-');
	return `/app/${slug}/view/list?${query}`;
}


class OptimedDashboard {
	constructor(page) {
		this.page = page;
		this.wrapper = $(page.body);
		this.data = null;
		this.refreshTimer = null;
		this.yearlyChart = null;
		this.selectedYear = null;  // anul curent selectat în grafic
		this.setup_page();
		this.refresh_data();
		this.start_auto_refresh();
	}

	setup_page() {
		this.wrapper.html(`
			<div class="optimed-dashboard">
				<div class="opt-loading">
					<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M21 12a9 9 0 11-6.219-8.56"/>
					</svg>
					<p>Se încarcă datele...</p>
				</div>
				<div class="opt-content" style="display: none;"></div>
			</div>
		`);
	}

	start_auto_refresh() {
		if (this.refreshTimer) clearInterval(this.refreshTimer);
		this.refreshTimer = setInterval(() => {
			this.refresh_data(true);
		}, AUTO_REFRESH_INTERVAL_MS);
	}

	async refresh_data(silent = false) {
		if (!silent) {
			this.wrapper.find('.opt-loading').show();
			this.wrapper.find('.opt-content').hide();
		}

		if (this.yearlyChart) {
			this.yearlyChart.destroy();
			this.yearlyChart = null;
		}

		try {
			const response = await frappe.call({
				method: 'optimed_crm.api.dashboard_stats.get_dashboard_data',
			});
			this.data = response.message;
			// La primul load, anul selectat = anul curent (din răspuns)
			if (this.data.yearly_chart && !this.selectedYear) {
				this.selectedYear = this.data.yearly_chart.year;
			}
			this.render();
		} catch (error) {
			frappe.msgprint({
				title: 'Eroare',
				message: 'Nu am putut încărca datele: ' + error.message,
				indicator: 'red'
			});
		}
	}

	async load_year_data(year) {
		// Apelat când userul schimbă anul din dropdown
		try {
			const response = await frappe.call({
				method: 'optimed_crm.api.dashboard_stats.get_yearly_chart_for_year',
				args: { year: year },
			});
			this.data.yearly_chart = response.message;
			this.selectedYear = year;
			this.rerender_yearly_chart();
		} catch (error) {
			frappe.msgprint({
				title: 'Eroare',
				message: 'Nu am putut încărca datele pentru anul ' + year,
				indicator: 'red'
			});
		}
	}

	rerender_yearly_chart() {
		// Re-randează DOAR secțiunea de grafic, fără să rebuilduiască restul Dashboard-ului
		if (this.yearlyChart) {
			this.yearlyChart.destroy();
			this.yearlyChart = null;
		}

		const chartSection = this.wrapper.find('.opt-yearly-chart-section');
		if (chartSection.length === 0) return;

		const newHtml = this.render_yearly_chart(this.data.yearly_chart);
		// Înlocuim doar conținutul secțiunii (păstrând <section> wrapper)
		chartSection.replaceWith(newHtml);

		this.attach_year_selector_handler();
		this.init_yearly_chart(this.data.yearly_chart);
	}

	render() {
		const data = this.data;
		const settings = data.settings || {};
		const display_name = data.user_display_name || 'Utilizator';

		const html = `
			${this.render_header(settings, display_name)}
			${this.render_shortcuts(data.operational)}
			${this.render_company_performance(data.company_stats, data.top_operator)}
			${data.operator_stats ? this.render_personal_performance(data.operator_stats) : ''}
			${this.render_commission_status(data.commission_status)}
			${this.render_patient_segments(data.patient_segments)}
			${data.totals ? this.render_totals(data.totals) : ''}
			${data.yearly_chart ? this.render_yearly_chart(data.yearly_chart) : ''}
		`;

		this.wrapper.find('.opt-loading').hide();
		this.wrapper.find('.opt-content').html(html).show();
		this.attach_handlers();

		if (data.yearly_chart) {
			this.attach_year_selector_handler();
			this.init_yearly_chart(data.yearly_chart);
		}
	}

	render_header(settings, display_name) {
		const company_name = settings.company_name || 'Optimed';
		const greeting_text = settings.greeting_text || 'Bună ziua';
		const today = new Date().toLocaleDateString('ro-RO', {
			day: 'numeric', month: 'long', year: 'numeric'
		});
		const logo_url = settings.logo_url;

		const logo_html = logo_url
			? `<img src="${logo_url}" alt="${company_name}" />`
			: `<span>${company_name.charAt(0)}</span>`;

		return `
			<div class="opt-dashboard-header">
				<div class="opt-dashboard-header-left">
					<div class="opt-logo-container">${logo_html}</div>
					<div>
						<p class="opt-greeting-text">${greeting_text}, ${display_name}</p>
						<h1 class="opt-greeting-title">Dashboard ${company_name}</h1>
					</div>
				</div>
				<div class="opt-dashboard-header-right">
					<span class="opt-date-label">${today}</span>
					<button class="opt-refresh-btn" id="opt-refresh-btn">
						<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M23 4v6h-6M1 20v-6h6"/>
							<path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
						</svg>
						Refresh
					</button>
				</div>
			</div>
		`;
	}

	render_shortcuts(op) {
		const todayStr = frappe.datetime.get_today();

		const programari_url = buildListUrl('Appointment', {
			'appointment_datetime': JSON.stringify(['>=', todayStr]),
			'is_cancelled': 0,
		});

		const deals_url = buildListUrl('Deal', {
			'pickup_date': JSON.stringify(['between', [op.month_start, op.month_end]]),
		});

		const cumparatori_url = buildListUrl('Patient', {
			'segment': 'Cumpărător nou',
			'is_active': 1,
		});

		const items = [
			{
				label: 'De contactat', sublabel: 'azi',
				value: op.to_contact_today,
				color: '#993c1d', bg: '#faece7',
				link: '/app/contacts-today',
				icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.13.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0122 16.92z"/></svg>'
			},
			{
				label: 'Programări', sublabel: 'viitoare',
				value: op.future_appointments,
				color: '#185fa5', bg: '#e6f1fb',
				link: programari_url,
				icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
			},
			{
				label: 'Deals', sublabel: 'luna curentă',
				value: op.deals_this_month,
				color: '#0f6e56', bg: '#e1f5ee',
				link: deals_url,
				icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9c2.39 0 4.68.94 6.36 2.64"/><path d="M22 4L12 14.01l-3-3"/></svg>'
			},
			{
				label: 'Cumpărători noi', sublabel: 'follow-up',
				value: op.new_buyers,
				color: '#3b6d11', bg: '#eaf3de',
				link: cumparatori_url,
				icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>'
			},
		];

		const cards = items.map(item => `
			<a href="${item.link}" class="opt-shortcut-card">
				<div class="opt-shortcut-header">
					<div class="opt-shortcut-icon" style="background: ${item.bg}; color: ${item.color};">
						${item.icon}
					</div>
					<span class="opt-shortcut-label" style="color: ${item.color};">${item.label}</span>
				</div>
				<div class="opt-shortcut-value">${this.fmt_number(item.value)}</div>
				<div class="opt-shortcut-sublabel">${item.sublabel}</div>
			</a>
		`).join('');

		return `<div class="opt-shortcuts-grid">${cards}</div>`;
	}

	render_personal_performance(stats) {
		return `
			<div class="opt-personal-section">
				<p class="opt-section-title">Performanța TA — luna curentă</p>
				<div class="opt-stats-grid opt-stats-grid-3">
					<div class="opt-stat-card opt-stat-card-personal">
						<p class="opt-stat-label">Venitul TĂU</p>
						<p class="opt-stat-value">${this.fmt_currency(stats.my_revenue)}</p>
						<p class="opt-stat-sublabel">RON · ${stats.my_deals_count} deal-uri</p>
					</div>
					<div class="opt-stat-card opt-stat-card-personal">
						<p class="opt-stat-label">Comisionul TĂU</p>
						<p class="opt-stat-value">${this.fmt_currency(stats.my_commission)}</p>
						<p class="opt-stat-sublabel">RON · provizoriu</p>
					</div>
					<div class="opt-stat-card opt-stat-card-personal">
						<p class="opt-stat-label">Manopera TA</p>
						<p class="opt-stat-value">${this.fmt_currency(stats.my_labor)}</p>
						<p class="opt-stat-sublabel">RON</p>
					</div>
				</div>
			</div>
		`;
	}

	render_company_performance(stats, top_operator) {
		const top_op_card = top_operator ? `
			<div class="opt-stat-card">
				<p class="opt-stat-label">Top operator</p>
				<p class="opt-stat-value">${top_operator.operator || '-'}</p>
				<p class="opt-stat-sublabel">${top_operator.deals_count} deal-uri</p>
			</div>
		` : '';

		return `
			<div class="opt-section">
				<p class="opt-section-title">Performanța firmei — luna curentă</p>
				<div class="opt-stats-grid ${top_operator ? 'opt-stats-grid-4' : 'opt-stats-grid-3'}">
					<div class="opt-stat-card">
						<p class="opt-stat-label">Venit luna</p>
						<p class="opt-stat-value">${this.fmt_currency(stats.total_revenue)}</p>
						<p class="opt-stat-sublabel">RON</p>
					</div>
					<div class="opt-stat-card">
						<p class="opt-stat-label">Comision operatori</p>
						<p class="opt-stat-value">${this.fmt_currency(stats.total_commission)}</p>
						<p class="opt-stat-sublabel">RON</p>
					</div>
					<div class="opt-stat-card">
						<p class="opt-stat-label">Manoperă totală</p>
						<p class="opt-stat-value">${this.fmt_currency(stats.total_labor)}</p>
						<p class="opt-stat-sublabel">RON</p>
					</div>
					${top_op_card}
				</div>
			</div>
		`;
	}

	render_commission_status(status) {
		const color_map = {
			'green': 'opt-status-green',
			'amber': 'opt-status-amber',
			'coral': 'opt-status-coral',
		};
		const css_class = color_map[status.color] || 'opt-status-amber';

		const icon = status.status === 'unlocked'
			? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>'
			: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>';

		const title = status.status === 'unlocked'
			? 'Status comision luna — DEBLOCAT'
			: 'Status comision luna';

		const pct_capped = Math.min(status.percentage, 100);

		return `
			<div class="opt-commission-banner ${css_class}">
				<div class="opt-commission-header">
					<div class="opt-commission-title">
						${icon}
						<span>${title}</span>
					</div>
					<span class="opt-commission-message">${status.message}</span>
				</div>
				<div class="opt-commission-progress-row">
					<span class="opt-commission-current">${this.fmt_currency(status.current)}</span>
					<span class="opt-commission-target">/ ${this.fmt_currency(status.threshold)} RON</span>
					<span class="opt-commission-pct">${status.percentage}%</span>
				</div>
				<div class="opt-progress-track">
					<div class="opt-progress-bar" style="width: ${pct_capped}%"></div>
				</div>
			</div>
		`;
	}

	render_patient_segments(seg) {
		const vip_url = buildListUrl('Patient', {'segment': 'VIP', 'is_active': 1});
		const loyal_url = buildListUrl('Patient', {'segment': 'Fidel', 'is_active': 1});
		const active_url = buildListUrl('Patient', {
			'is_active': 1,
			'days_since_last_activity': JSON.stringify(['<=', 365]),
		});
		const inactive_url = buildListUrl('Patient', {'segment': 'Inactiv', 'is_active': 1});
		const conversion_url = buildListUrl('Patient', {
			'is_active': 1,
			'total_purchases': JSON.stringify(['>', 0]),
		});

		return `
			<div class="opt-section">
				<p class="opt-section-title">Pacienți</p>
				<div class="opt-stats-grid opt-stats-grid-4">
					<a href="${vip_url}" class="opt-stat-card-link">
						<div class="opt-stat-card opt-stat-card-clickable">
							<p class="opt-stat-label">VIP</p>
							<p class="opt-stat-value">${this.fmt_number(seg.vip)}</p>
						</div>
					</a>
					<a href="${loyal_url}" class="opt-stat-card-link">
						<div class="opt-stat-card opt-stat-card-clickable">
							<p class="opt-stat-label">Pacienți Fideli</p>
							<p class="opt-stat-value">${this.fmt_number(seg.loyal)}</p>
						</div>
					</a>
					<a href="${active_url}" class="opt-stat-card-link">
						<div class="opt-stat-card opt-stat-card-clickable">
							<p class="opt-stat-label">Activi (sub 1 an)</p>
							<p class="opt-stat-value">${this.fmt_number(seg.active_under_year)}</p>
						</div>
					</a>
					<a href="${inactive_url}" class="opt-stat-card-link">
						<div class="opt-stat-card opt-stat-card-clickable">
							<p class="opt-stat-label">Inactivi</p>
							<p class="opt-stat-value">${this.fmt_number(seg.inactive)}</p>
						</div>
					</a>
				</div>
				<a href="${conversion_url}" class="opt-stat-card-link">
					<div class="opt-conversion-box opt-stat-card-clickable">
						<p class="opt-conversion-label">Conversie</p>
						<p class="opt-conversion-value">${seg.conversion_rate}%</p>
					</div>
				</a>
			</div>
		`;
	}

	render_totals(t) {
		return `
			<div class="opt-section">
				<p class="opt-section-title">Total</p>
				<div class="opt-stats-grid opt-stats-grid-3">
					<a href="/app/patient" class="opt-stat-card-link">
						<div class="opt-stat-card opt-stat-card-clickable">
							<p class="opt-stat-label">Total pacienți</p>
							<p class="opt-stat-value">${this.fmt_number(t.total_patients)}</p>
						</div>
					</a>
					<a href="/app/appointment" class="opt-stat-card-link">
						<div class="opt-stat-card opt-stat-card-clickable">
							<p class="opt-stat-label">Total programări</p>
							<p class="opt-stat-value">${this.fmt_number(t.total_appointments)}</p>
						</div>
					</a>
					<a href="/app/deal" class="opt-stat-card-link">
						<div class="opt-stat-card opt-stat-card-clickable">
							<p class="opt-stat-label">Total deals</p>
							<p class="opt-stat-value">${this.fmt_number(t.total_deals)}</p>
						</div>
					</a>
				</div>
				<div class="opt-stats-grid opt-stats-grid-3" style="margin-top: 12px;">
					<div class="opt-stat-card">
						<p class="opt-stat-label">Venit total</p>
						<p class="opt-stat-value">${this.fmt_currency(t.total_revenue)}</p>
						<p class="opt-stat-sublabel">RON</p>
					</div>
					<div class="opt-stat-card">
						<p class="opt-stat-label">Comision total operatori</p>
						<p class="opt-stat-value">${this.fmt_currency(t.total_commission)}</p>
						<p class="opt-stat-sublabel">RON</p>
					</div>
					<div class="opt-stat-card">
						<p class="opt-stat-label">Manoperă totală</p>
						<p class="opt-stat-value">${this.fmt_currency(t.total_labor)}</p>
						<p class="opt-stat-sublabel">RON</p>
					</div>
				</div>
			</div>
		`;
	}

	render_yearly_chart(chartData) {
		const stats = chartData.stats;
		const threshold_text = this.fmt_currency(chartData.threshold);
		const available_years = chartData.available_years || [chartData.year];

		// Construiește dropdown-ul cu ani disponibili
		const year_options = available_years.map(y => {
			const selected = (y === chartData.year) ? 'selected' : '';
			return `<option value="${y}" ${selected}>${y}</option>`;
		}).join('');

		return `
			<div class="opt-section opt-yearly-chart-section">
				<div class="opt-chart-header-row">
					<p class="opt-section-title" style="margin: 0;">Evoluție venituri</p>
					<div class="opt-year-selector-wrapper">
						<label class="opt-year-selector-label">An:</label>
						<select id="opt-year-selector" class="opt-year-selector">
							${year_options}
						</select>
					</div>
				</div>
				<div class="opt-chart-container">
					<div class="opt-chart-legend">
						<span class="opt-chart-legend-item">
							<span class="opt-chart-legend-color" style="background: #639922;"></span>
							Lună cu comision (≥ ${threshold_text} RON)
						</span>
						<span class="opt-chart-legend-item">
							<span class="opt-chart-legend-color" style="background: #185fa5;"></span>
							Lună sub prag
						</span>
						${chartData.is_current_year ? `
						<span class="opt-chart-legend-item">
							<span class="opt-chart-legend-color" style="background: #d3d1c7;"></span>
							Lună viitoare
						</span>` : ''}
						<span class="opt-chart-legend-item">
							<span class="opt-chart-legend-line"></span>
							Prag comision (${threshold_text})
						</span>
					</div>
					<div class="opt-chart-canvas-wrapper">
						<canvas id="opt-yearly-revenue-chart" role="img"
							aria-label="Grafic bare cu veniturile lunare ${chartData.year}, prag ${threshold_text} RON">
							Veniturile lunare pentru ${chartData.year}.
						</canvas>
					</div>
					<div class="opt-chart-stats">
						<div class="opt-chart-stat">
							<p class="opt-chart-stat-label">Total ${chartData.year}</p>
							<p class="opt-chart-stat-value">${this.fmt_currency(stats.total_year)}</p>
							<p class="opt-chart-stat-sublabel">RON</p>
						</div>
						<div class="opt-chart-stat">
							<p class="opt-chart-stat-label">Medie lunară</p>
							<p class="opt-chart-stat-value">${this.fmt_currency(stats.average_monthly)}</p>
							<p class="opt-chart-stat-sublabel">RON · ${stats.months_completed} luni</p>
						</div>
						<div class="opt-chart-stat">
							<p class="opt-chart-stat-label">Luni cu comision</p>
							<p class="opt-chart-stat-value">${stats.months_with_commission} / ${stats.months_completed}</p>
							<p class="opt-chart-stat-sublabel">${chartData.is_current_year ? 'din luni complete' : 'din 12 luni'}</p>
						</div>
						<div class="opt-chart-stat">
							<p class="opt-chart-stat-label">Luna cea mai bună</p>
							<p class="opt-chart-stat-value">${stats.best_month_name}</p>
							<p class="opt-chart-stat-sublabel">${this.fmt_currency(stats.best_month_revenue)} RON</p>
						</div>
					</div>
				</div>
			</div>
		`;
	}

	attach_year_selector_handler() {
		const me = this;
		this.wrapper.find('#opt-year-selector').off('change').on('change', function() {
			const newYear = parseInt($(this).val(), 10);
			if (newYear && newYear !== me.selectedYear) {
				me.load_year_data(newYear);
			}
		});
	}

	init_yearly_chart(chartData) {
		if (typeof Chart === 'undefined') {
			console.warn('Chart.js nu e disponibil — graficul nu va fi afișat');
			return;
		}

		const canvas = document.getElementById('opt-yearly-revenue-chart');
		if (!canvas) return;

		const months = chartData.months;
		const labels = months.map(m => m.name);
		const data = months.map(m => m.is_future ? null : m.revenue);
		const threshold = chartData.threshold;

		const colors = months.map(m => {
			if (m.is_future) return '#d3d1c7';
			if (m.revenue >= threshold) return '#639922';
			return '#185fa5';
		});

		const thresholdPlugin = {
			id: 'thresholdLineOptimed',
			afterDraw: (chart) => {
				const { ctx, chartArea, scales } = chart;
				if (!scales.y) return;
				const y = scales.y.getPixelForValue(threshold);
				if (y < chartArea.top || y > chartArea.bottom) return;
				ctx.save();
				ctx.strokeStyle = '#d85a30';
				ctx.lineWidth = 2;
				ctx.setLineDash([6, 4]);
				ctx.beginPath();
				ctx.moveTo(chartArea.left, y);
				ctx.lineTo(chartArea.right, y);
				ctx.stroke();
				ctx.restore();
			}
		};

		this.yearlyChart = new Chart(canvas, {
			type: 'bar',
			data: {
				labels: labels,
				datasets: [{
					label: 'Venit lunar (RON)',
					data: data,
					backgroundColor: colors,
					borderRadius: 4,
					borderSkipped: false,
				}]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				plugins: {
					legend: { display: false },
					tooltip: {
						callbacks: {
							title: (items) => {
								const idx = items[0].dataIndex;
								return months[idx].name_full + ' ' + chartData.year;
							},
							label: (item) => {
								if (item.parsed.y === null) return 'Lună viitoare';
								return Math.round(item.parsed.y).toLocaleString('ro-RO') + ' RON';
							}
						}
					}
				},
				scales: {
					x: {
						ticks: { autoSkip: false, font: { size: 11 } },
						grid: { display: false }
					},
					y: {
						beginAtZero: true,
						ticks: {
							callback: v => Math.round(v / 1000) + 'K',
							font: { size: 11 }
						},
						grid: { color: 'rgba(0,0,0,0.05)' }
					}
				}
			},
			plugins: [thresholdPlugin]
		});
	}

	attach_handlers() {
		const me = this;
		this.wrapper.find('#opt-refresh-btn').on('click', function() {
			me.refresh_data();
			frappe.show_alert({
				message: 'Datele au fost reîmprospătate',
				indicator: 'green'
			}, 2);
		});
	}

	// === Helpers de formatare ===

	fmt_number(n) {
		if (n === null || n === undefined) return '—';
		return Number(n).toLocaleString('ro-RO');
	}

	fmt_currency(n) {
		if (n === null || n === undefined) return '—';
		return Math.round(Number(n)).toLocaleString('ro-RO');
	}
}
