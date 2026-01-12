from odoo import models, fields

class MedPharmacyStockMove(models.Model):
    _name = 'med.pharmacy.stock.move'
    _description = 'Pharmacy Stock Movement'
    _order = 'date desc'


    product_id = fields.Many2one(
        'med.pharmacy.product',
        string='Drug',
        required=True
    )

    order_id = fields.Many2one(
        'med.pharmacy.order',
        string='Pharmacy Order',
        ondelete='cascade'
    )

    patient_id = fields.Many2one(
        'med.patient',
        string='Patient'
    )

    quantity = fields.Float(
        string='Quantity',
        required=True
    )

    move_type = fields.Selection([
        ('out', 'Dispensed'),
        ('in', 'Restock'),
    ], default='out', required=True)

    user_id = fields.Many2one(
        'res.users',
        string='Performed By',
        default=lambda self: self.env.user,
        readonly=True
    )

    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        readonly=True
    )

    def unlink(self):
        for move in self:
            # Only Admin can delete stock movement records
            if not self.env.user.has_group('medisite_clinic.group_med_admin'):
                raise UserError(
                    "Only Admin users can delete pharmacy stock movement records."
                )
        return super(MedPharmacyStockMove, self).unlink()

