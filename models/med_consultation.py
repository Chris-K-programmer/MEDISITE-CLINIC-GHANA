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

    pharmacy_order_id = fields.Many2one(
        'med.pharmacy.order',
        string='Pharmacy Order',
        readonly=True,
        copy=False
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
    malaria_rdt = fields.Selection([('pos', 'Positive'), ('neg', 'Negative')])
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

    myoglobin = fields.Selection([('pos', 'Positive'), ('neg', 'Negative')])
    ck_mb = fields.Selection([('pos', 'Positive'), ('neg', 'Negative')])
    troponin = fields.Selection([('pos', 'Positive'), ('neg', 'Negative')])

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
    # WORKFLOW STATE
    # ---------------------------------------------------------
    state = fields.Selection([
        ('nurse', 'Nurse'),
        ('doctor', 'Doctor'),
        ('lab', 'Lab Technician'),
        ('done', 'Completed'),
    ], default='nurse', tracking=True)

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

            if rec.pharmacy_order_id and rec.pharmacy_order_id.state != 'paid':
                raise UserError("Pharmacy payment must be completed before closing consultation.")

            rec.signature_user = self.env.user
            rec.date_signed = fields.Datetime.now()
            rec._change_state('done', 'Consultation completed and signed')

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

        lines = self._prepare_pharmacy_lines_from_medication()
        if lines:
            order_vals['line_ids'] = lines

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
