from odoo import models, fields

class MedPharmacyMove(models.Model):
    _name = 'med.pharmacy.move'
    _description = 'Pharmacy Stock Movement'
    _order = 'create_date desc'

    product_id = fields.Many2one('med.pharmacy.product', required=True)
    batch_id = fields.Many2one('med.pharmacy.batch', required=True)

    source_location_id = fields.Many2one('med.pharmacy.location')
    dest_location_id = fields.Many2one('med.pharmacy.location')

    quantity = fields.Float(required=True)

    move_type = fields.Selection([
        ('adjust', 'Adjustment'),
        ('transfer', 'Transfer'),
    ], required=True)

    note = fields.Char()
