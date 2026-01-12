from odoo import models, fields


class MedConsultationAudit(models.Model):
    _name = 'med.consultation.audit'
    _description = 'Consultation Audit Trail'
    _order = 'create_date desc'
    _rec_name = 'action'

    consultation_id = fields.Many2one(
        'med.consultation',
        required=True,
        ondelete='cascade',
        index=True
    )

    user_id = fields.Many2one(
        'res.users',
        required=True,
        default=lambda self: self.env.user,
        readonly=True
    )

    role = fields.Selection([
        ('nurse', 'Nurse'),
        ('doctor', 'Doctor'),
        ('lab', 'Lab Technician'),
        ('admin', 'Administrator'),
        ('system', 'System'),
    ], required=True, readonly=True)

    action = fields.Char(required=True, readonly=True)

    field_name = fields.Char(readonly=True)
    old_value = fields.Text(readonly=True)
    new_value = fields.Text(readonly=True)

    note = fields.Text(readonly=True)

    create_date = fields.Datetime(readonly=True)
