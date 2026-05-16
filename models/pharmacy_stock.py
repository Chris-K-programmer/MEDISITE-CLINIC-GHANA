from odoo import models, fields, api

class MedPharmacyStock(models.Model):
    _name = 'med.pharmacy.stock'
    _description = 'Pharmacy Stock Ledger'
    _rec_name = 'product_id'

    product_id = fields.Many2one('med.pharmacy.product', required=True)
    batch_id = fields.Many2one('med.pharmacy.batch', required=True)
    location_id = fields.Many2one('med.pharmacy.location', required=True)

    quantity = fields.Float(default=0)

    _sql_constraints = [
        ('unique_stock', 'unique(product_id, batch_id, location_id)', 'Duplicate stock line detected')
    ]
