from odoo import models, fields, api

class MedIPD(models.Model):
    _name = 'med.ipd'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'In-Patient Department Admission'

    name = fields.Char(string="Admission Reference", required=True, copy=False, readonly=True,
                       default=lambda self: 'New', tracking=True)
    patient_id = fields.Many2one('med.patient', string="Patient", required=True, tracking=True)
    consultation_id = fields.Many2one('med.consultation', string="Related Consultation")
    admission_date = fields.Datetime(string="Admission Date", default=fields.Datetime.now, required=True, tracking=True)
    discharge_date = fields.Datetime(string="Discharge Date", tracking=True)
    room_number = fields.Char(string="Room Number", tracking=True)
    bed_number = fields.Char(string="Bed Number", tracking=True)
    reason = fields.Text(string="Reason for Admission")
    notes = fields.Text(string="Additional Notes")
    
    stay_duration = fields.Char(
        string="Stay Duration",
        compute="_compute_stay_duration"
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged')
    ], string="Status", default='draft', tracking=True)

    clinical_severity = fields.Selection([
        ('stable', 'Stable'),
        ('serious', 'Serious'),
        ('critical', 'Critical')
    ], string="Clinical Severity", default='stable', tracking=True)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'High'),
    ], string="Priority", default='0', tracking=True)

    @api.depends('admission_date', 'discharge_date', 'state')
    def _compute_stay_duration(self):
        from datetime import datetime
        for rec in self:
            start = rec.admission_date
            end = rec.discharge_date or datetime.now()
            if start:
                diff = end - start
                days = diff.days
                hours = diff.seconds // 3600
                if days > 0:
                    rec.stay_duration = f"{days}d {hours}h"
                else:
                    rec.stay_duration = f"{hours}h"
            else:
                rec.stay_duration = "N/A"
    note_ids = fields.One2many('med.ipd.note', 'ipd_id', string="Nurse Notes")
    round_ids = fields.One2many('med.ipd.round', 'ipd_id', string="Doctor Ward Rounds")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('med.ipd') or 'New'
        return super().create(vals_list)

    def action_admit(self):
        self.write({
            'state': 'admitted',
            'admission_date': fields.Datetime.now()
        })

    def action_discharge(self):
        self.write({
            'state': 'discharged',
            'discharge_date': fields.Datetime.now()
        })

    def action_view_patient(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'med.patient',
            'view_mode': 'form',
            'res_id': self.patient_id.id,
            'target': 'current',
        }
