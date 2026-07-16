from odoo import models, fields, api
from odoo.exceptions import UserError


class MedICD10(models.Model):
    _name = 'med.icd10'
    _description = 'ICD-10 Diagnosis Codes'

    code = fields.Char(string='ICD-10 Code', required=True)
    name = fields.Char(string='Diagnosis', required=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'ICD-10 code must be unique!')
    ]
class MedConsultationMedicationLine(models.Model):
    _name = 'med.consultation.medication.line'
    _description = 'Consultation Medication Line'

    consultation_id = fields.Many2one('med.consultation', required=True, ondelete='cascade')
    product_id = fields.Many2one('med.pharmacy.product', required=True, string='Drug/Product', domain="[('active', '=', True)]")
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    dosage = fields.Char(string='Dosage')
    route = fields.Selection([
        ('oral', 'Oral'),
        ('iv', 'IV'),
        ('im', 'IM'),
        ('sc', 'SC'),
        ('topical', 'Topical'),
        ('inhalation', 'Inhalation'),
    ], string='Route', default='oral')
    frequency = fields.Char(string='Frequency')
    dosage_instructions = fields.Char(string='Dosage / Instructions')



class MedConsultation(models.Model):
    _name = 'med.consultation'
    _description = 'Medical Consultation'
    _rec_name = 'patient_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ---------------------------------------------------------
    # PATIENT LINK
    # ---------------------------------------------------------
    patient_id = fields.Many2one('med.patient', required=True)
    file_number = fields.Char(related='patient_id.file_number', store=True)
    patient_name = fields.Char(related='patient_id.name', store=True)
    patient_image = fields.Binary(related='patient_id.photo', string='Patient Photo', readonly=True)
    gender = fields.Selection(related='patient_id.gender', string='Gender', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True)

    pharmacy_order_id = fields.Many2one(
        'med.pharmacy.order',
        string='Pharmacy Order',
        readonly=True,
        copy=False
    )

    medication_line_ids = fields.One2many(
        'med.consultation.medication.line',
        'consultation_id',
        string='Prescription Lines'
    )

    external_document_ids = fields.Many2many(
        'ir.attachment',
        'med_consultation_attachment_rel',
        'consultation_id',
        'attachment_id',
        string='External Hospital Documents',
        domain="[('res_model', '=', 'med.consultation')]"
    )

    previous_consultation_ids = fields.One2many(
        'med.consultation',
        compute='_compute_previous_consultations',
        string='Previous Consultations',
        readonly=True
    )

    audit_ids = fields.One2many(
        'med.consultation.audit',
        'consultation_id',
        string='Audit Trail',
        readonly=True
    )

    ipd_id = fields.Many2one('med.ipd', string="IPD Admission")

    # ---------------------------------------------------------
    # NURSE HEADER
    # ---------------------------------------------------------
    date = fields.Datetime(default=fields.Datetime.now)
    time = fields.Datetime(default=fields.Datetime.now)
    nationality = fields.Char()
    occupation = fields.Char()
    employer = fields.Char()
    company_name = fields.Char(string='Company Name')
    department = fields.Char(string='Department')

    # ---------------------------------------------------------
    # HISTORY (NURSE)
    # ---------------------------------------------------------
    main_complaint = fields.Text()
    new_episode = fields.Boolean()
    recurrent_episode = fields.Boolean()
    history_details = fields.Text()

    female_pregnant = fields.Boolean()
    grav = fields.Char()
    para = fields.Char()
    lmp_date = fields.Date()
    oral_contraception = fields.Boolean()

    past_medical_history = fields.Text()
    allergies = fields.Text()
    family_history = fields.Text()
    travel_vacc_history = fields.Text()

    # ---------------------------------------------------------
    # VITAL SIGNS (NURSE)
    # ---------------------------------------------------------
    weight = fields.Float()
    height = fields.Float()
    bp = fields.Char()
    hr = fields.Integer()
    temp = fields.Float()
    rr = fields.Integer()
    spo2 = fields.Float()
    triage_note = fields.Text(string="Triage Note", help="Notes taken by nurses during triage")

    # ---------------------------------------------------------
    # LAB / SIDE ROOM (LAB TECH)
    # ---------------------------------------------------------
    malaria_rdt = fields.Selection([
        ('positive', 'Positive'), 
        ('negative', 'Negative'),
        ('pos', 'Positive'), 
        ('neg', 'Negative')
    ], string="Malaria RDT")
    malaria_strain = fields.Selection([('pf', 'P. falciparum'), ('pan', 'Pan'), ('other', 'Other')])
    blood_glucose = fields.Float()

    urinalysis_sg = fields.Char()
    urinalysis_ph = fields.Char()
    urinalysis_leu = fields.Char()
    urinalysis_nit = fields.Char()
    urinalysis_pro = fields.Char()
    urinalysis_glu = fields.Char()
    urinalysis_ket = fields.Char()
    urinalysis_ubg = fields.Char()
    urinalysis_bil = fields.Char()
    urinalysis_ery = fields.Char()

    myoglobin = fields.Selection([('positive', 'Positive'), ('negative', 'Negative'), ('pos', 'Positive'), ('neg', 'Negative')])
    ck_mb = fields.Selection([('positive', 'Positive'), ('negative', 'Negative'), ('pos', 'Positive'), ('neg', 'Negative')])
    troponin = fields.Selection([('positive', 'Positive'), ('negative', 'Negative'), ('pos', 'Positive'), ('neg', 'Negative')])

    ecg = fields.Text()
    other_side_room = fields.Text()

    # ---------------------------------------------------------
    # DOCTOR EXAMINATION
    # ---------------------------------------------------------
    sys_cns = fields.Text()
    sys_eyes = fields.Text()
    sys_ent = fields.Text()
    sys_cardio = fields.Text()
    sys_resp = fields.Text()
    sys_gastro = fields.Text()
    sys_uro = fields.Text()
    sys_musculo = fields.Text()
    sys_derm = fields.Text()
    sys_other = fields.Text()

    # ---------------------------------------------------------
    # SOAP / CLINICAL NOTES (Doctor)
    # ---------------------------------------------------------
    soap_subjective = fields.Text(
        string='Subjective',
        help='Patient-reported symptoms, concerns, and history of present illness'
    )
    soap_objective = fields.Text(
        string='Objective',
        help='Clinician observations, examination findings, vitals, lab results'
    )
    soap_assessment = fields.Text(
        string='Assessment',
        help='Clinical assessment, differential diagnosis, and clinical impression'
    )
    soap_plan = fields.Text(
        string='Plan',
        help='Treatment plan, medications, referrals, and follow-up instructions'
    )
    soap_education = fields.Text(
        string='Education',
        help='Patient education about condition, medication, lifestyle changes'
    )
    soap_follow_up = fields.Text(
        string='Follow-Up Consultation',
        help='Follow-up notes, expected outcomes, and next visit plan'
    )

    working_diagnosis = fields.Text()
    icd10_id = fields.Many2one(
        'med.icd10',
        string='ICD-10 Diagnosis',
        help='Select the ICD-10 code corresponding to the diagnosis'
    )
    treatment_plan = fields.Text()
    referral_facility = fields.Char()
    xray_requested = fields.Boolean()
    investigations = fields.Text()
    medication = fields.Text()
    other_treatment = fields.Text()

    edu_about_condition = fields.Text()
    edu_about_medication = fields.Text()

    sick_leave_from = fields.Date()
    sick_leave_to = fields.Date()
    sick_leave_days = fields.Integer()

    follow_up_date = fields.Date()
    follow_up_results = fields.Text()

    case_escalation = fields.Text()

    # ---------------------------------------------------------
    # SIGNATURE & TRACKING
    # ---------------------------------------------------------
    treating_hcp_id = fields.Many2one('med.staff')
    signature = fields.Binary()
    signature_user = fields.Many2one('res.users')
    date_signed = fields.Datetime()

    created_by = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    last_updated_by = fields.Many2one('res.users', readonly=True)

    # ---------------------------------------------------------
    # BILLING & CORPORATE SPONSORSHIP (GHS)
    # ---------------------------------------------------------
    currency_id = fields.Many2one('res.currency', string='Currency', compute='_compute_currency_id', store=True, readonly=False)
    bill_to = fields.Selection([
        ('individual', 'Individual Patient'),
        ('company', 'Corporate Company / Employer')
    ], string='Bill To', default='individual', tracking=True)
    sponsor_company_id = fields.Many2one('res.partner', string='Company to Bill', domain="[('is_company', '=', True)]", tracking=True)
    consultation_fee = fields.Monetary(string='Consultation Fee', currency_field='currency_id', default=100.0)
    bill_status = fields.Selection([
        ('draft', 'Not Billed'),
        ('billed', 'Billed'),
    ], string='Billing Status', default='draft', compute='_compute_bill_status', store=True)
    invoice_id = fields.Many2one('account.move', string='Generated Invoice', readonly=True, copy=False)

    @api.depends('patient_id')
    def _compute_currency_id(self):
        ghs = self.env['res.currency'].search([('name', '=', 'GHS')], limit=1)
        for rec in self:
            rec.currency_id = ghs.id if ghs else self.env.user.company_id.currency_id.id

    @api.depends('invoice_id', 'invoice_id.state')
    def _compute_bill_status(self):
        for rec in self:
            if rec.invoice_id:
                rec.bill_status = 'billed'
            else:
                rec.bill_status = 'draft'

    def action_create_company_bill(self):
        self.ensure_one()
        if self.invoice_id:
            return self.action_view_company_bill()

        # Determine billing partner
        if self.bill_to == 'company':
            if not self.sponsor_company_id:
                raise UserError("Please specify the Company to Bill.")
            partner = self.sponsor_company_id
        else:
            if not self.patient_id.partner_id:
                self.patient_id._ensure_partner()
            partner = self.patient_id.partner_id

        # Prepare invoice lines
        invoice_line_vals = []
        
        # 1. Consultation Fee
        if self.consultation_fee > 0:
            invoice_line_vals.append((0, 0, {
                'name': f"Consultation Fee - {self.patient_name} (File No: {self.file_number or 'N/A'})",
                'quantity': 1.0,
                'price_unit': self.consultation_fee,
            }))

        # 2. Add Medication lines if they exist
        for line in self.medication_line_ids:
            invoice_line_vals.append((0, 0, {
                'name': f"Prescription: {line.product_id.name} - Qty: {line.quantity} ({line.dosage or ''})",
                'quantity': line.quantity,
                'price_unit': line.product_id.unit_price or 0.0,
            }))

        if not invoice_line_vals:
            raise UserError("Cannot generate a bill with 0 lines (both consultation fee and prescription lines are empty).")

        # Make sure Ghana Cedis (GHS) currency is active and set
        ghs = self.env['res.currency'].search([('name', '=', 'GHS')], limit=1)
        currency = ghs if ghs else self.env.user.company_id.currency_id

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'currency_id': currency.id,
            'invoice_origin': self.patient_name or '',
            'invoice_line_ids': invoice_line_vals,
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        return self.action_view_company_bill()

    def action_view_company_bill(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Consultation Bill/Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }

    # ---------------------------------------------------------
    # WORKFLOW STATE
    # ---------------------------------------------------------
    state = fields.Selection([
        ('nurse', 'Nurse'),
        ('doctor', 'Doctor'),
        ('lab', 'Lab Technician'),
        ('done', 'Completed'),
    ], default='nurse', tracking=True)

    # ---------------------------------------------------------
    # ONCHANGE
    # ---------------------------------------------------------
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """Auto-populate demographic fields from the selected patient."""
        if self.patient_id:
            self.nationality = self.patient_id.nationality
            self.occupation = self.patient_id.occupation
            self.employer = self.patient_id.employer
            self.company_name = self.patient_id.company_name
            self.department = self.patient_id.department
            self.patient_image = self.patient_id.photo
            self.gender = self.patient_id.gender
            self.age = self.patient_id.age
            if self.patient_id.company_name or self.patient_id.employer:
                self.bill_to = 'company'
                search_name = self.patient_id.company_name or self.patient_id.employer
                company_partner = self.env['res.partner'].search([
                    ('name', '=ilike', search_name),
                    ('is_company', '=', True)
                ], limit=1)
                if company_partner:
                    self.sponsor_company_id = company_partner.id
                else:
                    self.sponsor_company_id = False
            else:
                self.bill_to = 'individual'
                self.sponsor_company_id = False
        else:
            self.nationality = False
            self.occupation = False
            self.employer = False
            self.company_name = False
            self.department = False
            self.patient_image = False
            self.gender = False
            self.age = 0
            self.bill_to = 'individual'
            self.sponsor_company_id = False

    # ---------------------------------------------------------
    # CREATE / WRITE OVERRIDES
    # ---------------------------------------------------------
    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.last_updated_by = self.env.user
        return record

    def write(self, vals):
        nurse_fields = {
            'date', 'time', 'nationality', 'occupation', 'employer',
            'main_complaint', 'new_episode', 'recurrent_episode',
            'history_details', 'female_pregnant', 'grav', 'para',
            'lmp_date', 'oral_contraception',
            'weight', 'height', 'bp', 'hr', 'temp', 'rr', 'spo2'
        }

        tracked_fields = {
            'working_diagnosis', 'treatment_plan', 'medication',
            'investigations', 'malaria_rdt', 'blood_glucose',
            'bp', 'temp', 'icd10_id'
        }

        for rec in self:
            if rec.state != 'nurse' and nurse_fields.intersection(vals):
                if not self.env.user.has_group('medisite_clinic.group_med_admin'):
                    raise UserError("Nurse-entered data is locked once sent to the doctor.")

            for field in tracked_fields:
                if field in vals:
                    rec._log_audit(
                        action='Field Updated',
                        field_name=field,
                        old=str(getattr(rec, field)),
                        new=str(vals[field]),
                        note='Clinical data modified'
                    )

        vals['last_updated_by'] = self.env.user.id
        return super().write(vals)

    # ---------------------------------------------------------
    # WORKFLOW ACTIONS
    # ---------------------------------------------------------
    def action_search_icd(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Search ICD-10',
            'res_model': 'med.icd10',
            'view_mode': 'list',
            'target': 'new',
        }

    def action_add_medicine(self):
        return True

    def action_send_to_doctor(self):
        for rec in self:
            if rec.state != 'nurse':
                raise UserError("Only Nurse stage allowed.")
            rec._change_state('doctor', 'Nurse sent consultation to Doctor')

    def action_send_to_lab(self):
        for rec in self:
            if rec.state != 'doctor':
                raise UserError("Only Doctor stage allowed.")
            rec._change_state('lab', 'Doctor requested lab investigation')

    def action_send_to_doctor_from_lab(self):
        for rec in self:
            if rec.state != 'lab':
                raise UserError("Only Lab stage allowed.")
            rec._change_state('doctor', 'Lab returned results to Doctor')

    def action_done(self):
        for rec in self:
            if rec.state != 'doctor':
                raise UserError("Only Doctor can complete consultation.")

            # Auto-link the treating HCP (staff) based on logged-in user
            staff = self.env['med.staff'].search([('user_id', '=', self.env.user.id)], limit=1)
            if staff:
                rec.treating_hcp_id = staff.id

            rec.signature_user = self.env.user
            rec.date_signed = fields.Datetime.now()
            rec._change_state('done', 'Consultation completed and signed')

            # Auto-create pharmacy order on completion if medications are prescribed
            if not rec.pharmacy_order_id:
                rec._create_pharmacy_order_automatically()

    def _create_pharmacy_order_automatically(self):
        self.ensure_one()
        order_vals = {
            'consultation_id': self.id,
            'patient_id': self.patient_id.id,
        }
        order_lines = []
        
        # 1. Populate from tabular medication lines if available
        if self.medication_line_ids:
            for line in self.medication_line_ids:
                order_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'unit_price': line.product_id.unit_price,
                }))
        
        # 2. Fall back to raw text medications split-line parser
        if not order_lines and self.medication:
            parsed = self._prepare_pharmacy_lines_from_medication()
            if parsed:
                order_lines = parsed

        if order_lines:
            order_vals['line_ids'] = order_lines
            order = self.env['med.pharmacy.order'].create(order_vals)
            self.pharmacy_order_id = order.id

    def action_send_to_pharmacy(self):
        self.ensure_one()
        if self.state != 'done':
            raise UserError("Consultation must be completed before sending to pharmacy.")

        if self.pharmacy_order_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'med.pharmacy.order',
                'view_mode': 'form',
                'res_id': self.pharmacy_order_id.id,
                'target': 'current',
            }

        order_vals = {
            'consultation_id': self.id,
            'patient_id': self.patient_id.id,
        }

        # Use same dual population logic
        order_lines = []
        if self.medication_line_ids:
            for line in self.medication_line_ids:
                order_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'unit_price': line.product_id.unit_price,
                }))
        if not order_lines and self.medication:
            parsed = self._prepare_pharmacy_lines_from_medication()
            if parsed:
                order_lines = parsed

        if order_lines:
            order_vals['line_ids'] = order_lines

        order = self.env['med.pharmacy.order'].create(order_vals)
        self.pharmacy_order_id = order.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'med.pharmacy.order',
            'view_mode': 'form',
            'res_id': order.id,
            'target': 'current',
        }

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------
    def _prepare_pharmacy_lines_from_medication(self):
        lines = []
        Product = self.env['med.pharmacy.product']
        if not self.medication:
            return lines

        for raw_line in self.medication.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            tokens = line.split()
            drug_name = tokens[0]

            product = Product.search([('name', 'ilike', drug_name)], limit=1)
            if not product:
                continue

            lines.append((0, 0, {
                'product_id': product.id,
                'quantity': 1,
                'unit_price': product.unit_price,
            }))

        return lines

    def _change_state(self, new_state, note):
        old_state = self.state
        self.state = new_state
        self._log_audit(
            action='Workflow Transition',
            field_name='state',
            old=old_state,
            new=new_state,
            note=note
        )
        # ── Bus notification → triggers frontend TTS & sound alert ──────────
        patient_name = self.patient_name or 'Patient'
        notification_map = {
            'doctor': {
                'group_ref': 'medisite_clinic.group_med_doctor',
                'role': 'doctor',
                'message': f"Attention Doctor. Patient {patient_name} is ready for your consultation.",
            },
            'lab': {
                'group_ref': 'medisite_clinic.group_med_lab',
                'role': 'lab',
                'message': f"Lab alert. Results are required for patient {patient_name}. Please proceed.",
            },
            'nurse': {
                'group_ref': 'medisite_clinic.group_med_nurse',
                'role': 'nurse',
                'message': f"Nurse station. Patient {patient_name} has been returned from the lab. Doctor review pending.",
            },
            'done': {
                'group_ref': 'medisite_clinic.group_med_nurse',
                'role': 'nurse',
                'message': f"Consultation for patient {patient_name} is now complete.",
            },
        }
        notif = notification_map.get(new_state)
        if notif:
            try:
                target_group = self.env.ref(notif['group_ref'])
                self.env['bus.bus']._sendone(target_group, 'medisite_notification', {
                    'role': notif['role'],
                    'patient_name': patient_name,
                    'message': notif['message'],
                })
            except Exception:
                pass  # Never block a clinical state change due to notification failure

    def _get_user_role(self):
        user = self.env.user
        if user.has_group('medisite_clinic.group_med_admin'):
            return 'admin'
        if user.has_group('medisite_clinic.group_med_doctor'):
            return 'doctor'
        if user.has_group('medisite_clinic.group_med_lab'):
            return 'lab'
        if user.has_group('medisite_clinic.group_med_nurse'):
            return 'nurse'
        return 'system'

    def _log_audit(self, action, field_name=None, old=None, new=None, note=None):
        self.env['med.consultation.audit'].create({
            'consultation_id': self.id,
            'user_id': self.env.user.id,
            'role': self._get_user_role(),
            'action': action,
            'field_name': field_name,
            'old_value': old,
            'new_value': new,
            'note': note,
        })

    def _compute_previous_consultations(self):
        for rec in self:
            if not rec.patient_id:
                rec.previous_consultation_ids = False
                continue

            rec.previous_consultation_ids = self.env['med.consultation'].search([
                ('patient_id', '=', rec.patient_id.id),
                ('id', '!=', rec.id),
                ('state', 'in', ['doctor', 'lab', 'done']),
            ], order='date desc')

    def create_ipd(self):
        self.ensure_one()
        ipd = self.env['med.ipd'].create({
            'patient_id': self.patient_id.id,
            'consultation_id': self.id,
            'reason': 'Admitted via consultation',
        })
        self.ipd_id = ipd.id
