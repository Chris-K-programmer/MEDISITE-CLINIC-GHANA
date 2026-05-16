from odoo import models, fields
from odoo.exceptions import UserError

class MedPharmacyTransferWizard(models.TransientModel):
    _name = 'med.pharmacy.transfer.wizard'
    _description = 'Stock Transfer Wizard'

    product_id = fields.Many2one('med.pharmacy.product', required=True)
    batch_id = fields.Many2one('med.pharmacy.batch', required=True)

    source_location_id = fields.Many2one('med.pharmacy.location', required=True)
    dest_location_id = fields.Many2one('med.pharmacy.location', required=True)

    quantity = fields.Float(required=True)

    def action_transfer(self):
        Stock = self.env['med.pharmacy.stock']
        Move = self.env['med.pharmacy.move']

        src = Stock.search([
            ('product_id','=',self.product_id.id),
            ('batch_id','=',self.batch_id.id),
            ('location_id','=',self.source_location_id.id)
        ], limit=1)

        if not src or src.quantity < self.quantity:
            raise UserError("Insufficient stock.")

        dest = Stock.search([
            ('product_id','=',self.product_id.id),
            ('batch_id','=',self.batch_id.id),
            ('location_id','=',self.dest_location_id.id)
        ], limit=1)

        if not dest:
            dest = Stock.create({
                'product_id': self.product_id.id,
                'batch_id': self.batch_id.id,
                'location_id': self.dest_location_id.id,
                'quantity': 0,
            })

        src.quantity -= self.quantity
        dest.quantity += self.quantity

        Move.create({
            'product_id': self.product_id.id,
            'batch_id': self.batch_id.id,
            'source_location_id': self.source_location_id.id,
            'dest_location_id': self.dest_location_id.id,
            'quantity': self.quantity,
            'move_type': 'transfer',
        })
        return {'type': 'ir.actions.act_window_close'}

