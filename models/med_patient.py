from odoo import models, fields, api
from datetime import date

class MedPatient(models.Model):
    _name = 'med.patient'
    _description = 'Patient Registry'

    name = fields.Char(required=True)
    file_number = fields.Char(index=True)
    dob = fields.Date()
    age = fields.Integer(compute='_compute_age', store=True)
    gender = fields.Selection([('m','MALE'),('f','FEMALE'),])
    nationality = fields.Char()
    occupation = fields.Char()
    employer = fields.Char()
    partner_id = fields.Many2one('res.partner', string="Contact Record", ondelete='restrict')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('partner_id'):
                partner = self.env['res.partner'].create({
                    'name': vals.get('name'),
                    'customer_rank': 1,
                    # You could add phone/email mapping here if they existed on patient
                })
                vals['partner_id'] = partner.id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if 'name' in vals:
            for rec in self:
                if rec.partner_id:
                    rec.partner_id.name = vals['name']
        return res

    def _ensure_partner(self):
        """Ensures the patient has a linked res.partner (for legacy records)."""
        for rec in self:
            if not rec.partner_id:
                partner = self.env['res.partner'].create({
                    'name': rec.name,
                    'customer_rank': 1,
                })
                rec.partner_id = partner.id
        return True

    # --- New fields ---
    photo = fields.Binary(string="Photo")                  # Patient photo
    employee_id = fields.Char(string="Employee ID")        # Optional employee ID

    # UI Redesign fields (Placeholders)
    status = fields.Selection([('stable', 'STABLE'), ('serious', 'SERIOUS'), ('critical', 'CRITICAL')], default='stable', string="Status")
    inpatient_status = fields.Selection([('out_patient', 'OUT-PATIENT'), ('in_patient', 'IN-PATIENT')], default='in_patient', string="Inpatient Status")
    
    next_appointment_date = fields.Datetime(string="Next Appointment Date")
    next_appointment_type = fields.Char(string="Next Appointment Type")
    next_appointment_doctor = fields.Char(string="Next Appointment Doctor")

    blood_pressure = fields.Char(string="Blood Pressure", default="120/80")
    heart_rate = fields.Integer(string="Heart Rate", default=72)
    blood_oxygen = fields.Integer(string="Blood Oxygen", default=98)
    blood_glucose = fields.Integer(string="Blood Glucose", default=105)

    ipd_ids = fields.One2many('med.ipd', 'patient_id', string="IPD Admissions")

    consultation_ids = fields.One2many(
        'med.consultation',
        'patient_id',
        string='Consultations'
    )

    active = fields.Boolean(default=True)
    consultation_count = fields.Integer(compute='_compute_counts')
    ipd_count = fields.Integer(compute='_compute_counts')
    invoice_count = fields.Integer(compute='_compute_counts')
    invoice_ids = fields.One2many('account.move', 'partner_id', string="Invoices", compute='_compute_invoices')

    def _compute_invoices(self):
        for rec in self:
            rec.invoice_ids = self.env['account.move'].search([('partner_id', '=', rec.partner_id.id)])

    def _compute_counts(self):
        for rec in self:
            rec.consultation_count = len(rec.consultation_ids)
            rec.ipd_count = len(rec.ipd_ids)
            rec.invoice_count = len(rec.invoice_ids)

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Invoices',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {'default_move_type': 'out_invoice', 'default_partner_id': self.partner_id.id},
        }

    def action_view_consultations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Consultations',
            'res_model': 'med.consultation',
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    def action_view_ipd(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'IPD Admissions',
            'res_model': 'med.ipd',
            'view_mode': 'kanban,list,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            if rec.dob:
                today = date.today()
                rec.age = today.year - rec.dob.year - (
                    (today.month, today.day) < (rec.dob.month, rec.dob.day)
                )
            else:
                rec.age = 0
