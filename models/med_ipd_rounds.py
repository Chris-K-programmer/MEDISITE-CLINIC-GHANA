from odoo import models, fields

class MedIPDNurseNote(models.Model):
    _name = 'med.ipd.note'
    _description = 'IPD Nurse Note'
    _order = 'date desc'

    ipd_id = fields.Many2one('med.ipd', required=True, ondelete='cascade')
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    nurse_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    note = fields.Text(required=True)


class MedIPDWardRound(models.Model):
    _name = 'med.ipd.round'
    _description = 'IPD Doctor Ward Round'
    _order = 'date desc'

    ipd_id = fields.Many2one('med.ipd', required=True, ondelete='cascade')
    date = fields.Datetime(default=fields.Datetime.now, required=True)
    doctor_id = fields.Many2one('med.staff')
    assessment = fields.Text()
    plan = fields.Text()
    instructions = fields.Text()
