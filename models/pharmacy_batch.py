from odoo import models, fields, api
from datetime import timedelta

class MedPharmacyBatch(models.Model):
    _name = 'med.pharmacy.batch'
    _description = 'Drug Batch'

    name = fields.Char(string="Batch Number", required=True)
    product_id = fields.Many2one('med.pharmacy.product', required=True)
    expiry_date = fields.Date(required=True)
    cost_price = fields.Float()
    active = fields.Boolean(default=True)

    is_expired = fields.Boolean(compute='_compute_expiry_status', store=True)
    is_expiring_soon = fields.Boolean(compute='_compute_expiry_status', store=True)

    @api.depends('expiry_date')
    def _compute_expiry_status(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.expiry_date:
                rec.is_expired = rec.expiry_date <= today
                rec.is_expiring_soon = today < rec.expiry_date <= (today + timedelta(days=60))
            else:
                rec.is_expired = False
                rec.is_expiring_soon = False
