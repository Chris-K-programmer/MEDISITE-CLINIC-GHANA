from odoo import models, fields, api

class MedIPD(models.Model):
    _name = 'med.ipd'
    _description = 'In-Patient Department Admission'

    name = fields.Char(string="Admission Reference", required=True, copy=False, readonly=True,
                       default=lambda self: 'New')
    patient_id = fields.Many2one('med.patient', string="Patient", required=True)
    consultation_id = fields.Many2one('med.consultation', string="Related Consultation")
    admission_date = fields.Datetime(string="Admission Date", default=fields.Datetime.now, required=True)
    discharge_date = fields.Datetime(string="Discharge Date")
    room_number = fields.Char(string="Room Number")
    bed_number = fields.Char(string="Bed Number")
    reason = fields.Text(string="Reason for Admission")
    notes = fields.Text(string="Additional Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged')
    ], string="Status", default='draft')
    note_ids = fields.One2many('med.ipd.note', 'ipd_id', string="Nurse Notes")
    round_ids = fields.One2many('med.ipd.round', 'ipd_id', string="Doctor Ward Rounds")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('med.ipd') or 'New'
        return super(MedIPD, self).create(vals)

    def action_admit(self):
        self.state = 'admitted'

    def action_discharge(self):
        self.state = 'discharged'
