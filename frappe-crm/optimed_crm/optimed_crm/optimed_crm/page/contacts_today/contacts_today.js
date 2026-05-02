// Copyright (c) 2026, Optimed Toplița
// Pagina interactivă "Contacte de făcut azi"

frappe.pages['contacts-today'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Contacte de făcut azi',
		single_column: true
	});

	new ContactsToday(page);
};


class ContactsToday {
	constructor(page) {
		this.page = page;
		this.wrapper = $(page.body);
		this.data = null;
		this.setup_page();
		this.refresh_data();
	}

	setup_page() {
		// Buton refresh
		this.page.set_primary_action('Reîmprospătează', () => {
			this.refresh_data();
		}, 'refresh');

		// Buton "Vezi istoric contactări"
		this.page.add_menu_item('Istoric contactări', () => {
			frappe.set_route('query-report', 'Istoric contactări');
		});

		// Container principal
		this.wrapper.html(`
			<div class="contacts-today-container" style="padding: 20px;">
				<div class="loading-state" style="text-align: center; padding: 40px; color: #888;">
					<i class="fa fa-spinner fa-spin" style="font-size: 24px;"></i>
					<p style="margin-top: 15px;">Se încarcă contactele...</p>
				</div>
				<div class="content-area" style="display: none;"></div>
			</div>
		`);
	}

	async refresh_data() {
		this.wrapper.find('.loading-state').show();
		this.wrapper.find('.content-area').hide();

		try {
			const response = await frappe.call({
				method: 'optimed_crm.api.contacts_today.get_contacts_for_today',
			});
			this.data = response.message;
			this.render();
		} catch (error) {
			frappe.msgprint({
				title: 'Eroare',
				message: 'Nu am putut încărca contactele: ' + error.message,
				indicator: 'red'
			});
		}
	}

	render() {
		const contentArea = this.wrapper.find('.content-area');
		this.wrapper.find('.loading-state').hide();
		contentArea.show();

		// Header sumar
		const total = this.data.total;
		const dateFormatted = frappe.datetime.str_to_user(this.data.today);

		let html = `
			<div class="summary-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
				<h2 style="margin: 0; color: white; font-weight: 600;">📞 Contacte de făcut azi</h2>
				<p style="margin: 5px 0 0; opacity: 0.9;">${dateFormatted}</p>
				<div style="display: flex; align-items: baseline; margin-top: 15px;">
					<span style="font-size: 48px; font-weight: 700;">${total}</span>
					<span style="font-size: 16px; margin-left: 10px; opacity: 0.9;">pacienți de contactat</span>
				</div>
			</div>
		`;

		if (total === 0) {
			html += `
				<div style="text-align: center; padding: 60px; background: #f8f9fa; border-radius: 8px;">
					<div style="font-size: 64px; margin-bottom: 20px;">🎉</div>
					<h3 style="color: #28a745;">Nu sunt contactări de făcut astăzi!</h3>
					<p style="color: #6c757d;">Toți pacienții care îndeplinesc criteriile au fost deja contactați.</p>
				</div>
			`;
		} else {
			// Renderează fiecare categorie
			this.data.categories.forEach(cat => {
				html += this.render_category(cat);
			});
		}

		contentArea.html(html);

		// Atașează event handlers după render
		this.attach_handlers();
	}

	render_category(category) {
		if (category.count === 0) {
			return `
				<div class="category-section" style="margin-bottom: 30px; opacity: 0.5;">
					<h3 style="border-left: 4px solid ${category.color}; padding-left: 12px; margin-bottom: 5px;">
						${category.icon} ${category.label}
					</h3>
					<p style="color: #888; padding-left: 16px;">Niciun pacient pentru această categorie.</p>
				</div>
			`;
		}

		let html = `
			<div class="category-section" data-category="${category.key}" style="margin-bottom: 30px;">
				<div style="border-left: 4px solid ${category.color}; padding-left: 12px; margin-bottom: 12px;">
					<h3 style="margin: 0;">${category.icon} ${category.label} <span style="font-size: 14px; color: #888; font-weight: normal;">— ${category.count} pacienți</span></h3>
					<p style="margin: 4px 0 0; color: #6c757d; font-size: 13px;">${frappe.utils.escape_html(category.action_description)}</p>
				</div>
				<table class="table table-hover" style="background: white; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden;">
					<thead style="background: #f8f9fa;">
						<tr>
							<th style="padding: 10px; font-size: 12px; text-transform: uppercase;">Pacient</th>
							<th style="padding: 10px; font-size: 12px; text-transform: uppercase;">Telefon</th>
							<th style="padding: 10px; font-size: 12px; text-transform: uppercase;">Ultima ridicare</th>
							<th style="padding: 10px; font-size: 12px; text-transform: uppercase;">Operator</th>
							<th style="padding: 10px; font-size: 12px; text-transform: uppercase; text-align: right;">Acțiuni</th>
						</tr>
					</thead>
					<tbody>
		`;

		category.patients.forEach(patient => {
			const pickupDate = patient.last_pickup_date ?
				frappe.datetime.str_to_user(patient.last_pickup_date) : '-';
			const phone = patient.phone || '-';
			const phoneHtml = patient.phone ?
				`<a href="tel:${patient.phone.replace(/\\s/g, '')}" style="color: #007bff; text-decoration: none;">${phone}</a>` :
				'<span style="color: #aaa;">-</span>';

			html += `
				<tr data-patient="${patient.patient_id}" data-contact-type="${frappe.utils.escape_html(category.contact_type)}" data-deal="${patient.last_deal || ''}">
					<td style="padding: 12px; vertical-align: middle;">
						<a href="/app/patient/${patient.patient_id}" style="font-weight: 500;">${frappe.utils.escape_html(patient.patient_name)}</a>
						<br><small style="color: #888;">${patient.patient_id}</small>
					</td>
					<td style="padding: 12px; vertical-align: middle;">${phoneHtml}</td>
					<td style="padding: 12px; vertical-align: middle;">
						${pickupDate}
						<br><small style="color: #888;">acum ${patient.days_since_pickup} zile</small>
					</td>
					<td style="padding: 12px; vertical-align: middle;">${patient.last_operator || '-'}</td>
					<td style="padding: 12px; text-align: right; vertical-align: middle;">
						<button class="btn btn-sm btn-primary btn-mark-contacted" style="margin-right: 5px;">
							✓ Marchează
						</button>
						<button class="btn btn-sm btn-default btn-do-not-contact" title="Marchează ca NU contacta">
							🚫
						</button>
					</td>
				</tr>
			`;
		});

		html += `
					</tbody>
				</table>
			</div>
		`;
		return html;
	}

	attach_handlers() {
		const me = this;

		// Marchează ca sunat
		this.wrapper.find('.btn-mark-contacted').on('click', function() {
			const row = $(this).closest('tr');
			const patientId = row.data('patient');
			const contactType = row.data('contact-type');
			const dealId = row.data('deal');
			me.show_mark_contacted_dialog(patientId, contactType, dealId, row);
		});

		// Marchează ca NU contacta
		this.wrapper.find('.btn-do-not-contact').on('click', function() {
			const row = $(this).closest('tr');
			const patientId = row.data('patient');
			me.show_do_not_contact_dialog(patientId, row);
		});
	}

	show_mark_contacted_dialog(patientId, contactType, dealId, row) {
		const me = this;

		const dialog = new frappe.ui.Dialog({
			title: `Înregistrează contactare — ${patientId}`,
			fields: [
				{
					fieldname: 'contact_status',
					fieldtype: 'Select',
					label: 'Status contactare',
					options: '\nSunat — răspuns OK\nSunat — nu răspunde\nSunat — refuz\nMesaj WhatsApp/SMS trimis\nEmail trimis\nProgramat pentru revenire\nAlt status',
					reqd: 1,
				},
				{
					fieldname: 'notes',
					fieldtype: 'Small Text',
					label: 'Note (opțional)',
				},
				{
					fieldname: 'follow_up_required',
					fieldtype: 'Check',
					label: 'Necesită revenire',
				},
				{
					fieldname: 'follow_up_date',
					fieldtype: 'Date',
					label: 'Data revenire',
					depends_on: 'follow_up_required',
				},
			],
			primary_action_label: 'Salvează',
			primary_action: async (values) => {
				try {
					await frappe.call({
						method: 'optimed_crm.api.contacts_today.mark_as_contacted',
						args: {
							patient_id: patientId,
							contact_type: contactType,
							contact_status: values.contact_status,
							notes: values.notes,
							follow_up_required: values.follow_up_required ? 1 : 0,
							follow_up_date: values.follow_up_date,
							linked_deal: dealId,
						},
					});

					frappe.show_alert({
						message: `Contactare înregistrată pentru ${patientId}`,
						indicator: 'green',
					}, 3);

					// Animație de dispariție a rândului
					row.css({transition: 'opacity 0.3s, transform 0.3s'});
					row.css({opacity: 0, transform: 'translateX(20px)'});
					setTimeout(() => {
						me.refresh_data();
					}, 300);

					dialog.hide();
				} catch (error) {
					frappe.msgprint({
						title: 'Eroare',
						message: 'Nu am putut salva contactarea: ' + error.message,
						indicator: 'red',
					});
				}
			},
		});

		dialog.show();
	}

	show_do_not_contact_dialog(patientId, row) {
		const me = this;

		const dialog = new frappe.ui.Dialog({
			title: `Marchează "NU contacta" — ${patientId}`,
			fields: [
				{
					fieldname: 'warning_html',
					fieldtype: 'HTML',
					options: `
						<div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; border-radius: 4px; margin-bottom: 15px;">
							<strong>Atenție:</strong> Pacientul nu va mai apărea în nicio listă de contactare automată.
							Această acțiune se poate anula manual din fișa pacientului.
						</div>
					`,
				},
				{
					fieldname: 'reason',
					fieldtype: 'Small Text',
					label: 'Motiv',
					reqd: 1,
					description: 'Ex: A cerut explicit, decedat, cont închis, etc.',
				},
			],
			primary_action_label: 'Marchează',
			primary_action: async (values) => {
				try {
					await frappe.call({
						method: 'optimed_crm.api.contacts_today.mark_do_not_contact',
						args: {
							patient_id: patientId,
							reason: values.reason,
						},
					});

					frappe.show_alert({
						message: `Pacient marcat ca NU contacta`,
						indicator: 'orange',
					}, 3);

					row.css({transition: 'opacity 0.3s'});
					row.css({opacity: 0});
					setTimeout(() => {
						me.refresh_data();
					}, 300);

					dialog.hide();
				} catch (error) {
					frappe.msgprint({
						title: 'Eroare',
						message: 'Nu am putut marca pacientul: ' + error.message,
						indicator: 'red',
					});
				}
			},
		});

		dialog.show();
	}
}
