from odoo import models, fields

class MedPharmacyProduct(models.Model):
    _name = 'med.pharmacy.product'
    _description = 'Pharmacy Drug Master'
    _rec_name = 'name'

    name = fields.Char(required=True)
    strength = fields.Char()
    form = fields.Selection([
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('other', 'Other'),
    ])

    unit_price = fields.Float(required=True)
    qty_available = fields.Float(
        string='Quantity On Hand',
        default=0.0
    )
    active = fields.Boolean(default=True)

    notes = fields.Text()
