from odoo import models, fields

class MedPharmacyAdjustWizard(models.TransientModel):
    _name = 'med.pharmacy.adjust.wizard'
    _description = 'Stock Adjustment Wizard'

    product_id = fields.Many2one('med.pharmacy.product', required=True)
    batch_id = fields.Many2one('med.pharmacy.batch', required=True)
    location_id = fields.Many2one('med.pharmacy.location', required=True)

    quantity = fields.Float(required=True)
    note = fields.Char()

    def action_adjust(self):
        Stock = self.env['med.pharmacy.stock']
        Move = self.env['med.pharmacy.move']

        stock = Stock.search([
            ('product_id','=',self.product_id.id),
            ('batch_id','=',self.batch_id.id),
            ('location_id','=',self.location_id.id)
        ], limit=1)

        if not stock:
            stock = Stock.create({
                'product_id': self.product_id.id,
                'batch_id': self.batch_id.id,
                'location_id': self.location_id.id,
                'quantity': 0,
            })

        stock.quantity += self.quantity

        Move.create({
            'product_id': self.product_id.id,
            'batch_id': self.batch_id.id,
            'dest_location_id': self.location_id.id,
            'quantity': self.quantity,
            'move_type': 'adjust',
            'note': self.note,
        })
        return {'type': 'ir.actions.act_window_close'}

