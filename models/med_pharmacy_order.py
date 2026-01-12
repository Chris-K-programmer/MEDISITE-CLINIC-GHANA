from odoo import models, fields, api
from odoo.exceptions import UserError


class MedPharmacyOrder(models.Model):
    _name = 'med.pharmacy.order'
    _description = 'Pharmacy Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Order Reference', required=True, copy=False,
                       default=lambda self: self.env['ir.sequence'].next_by_code('med.pharmacy.order'))
    consultation_id = fields.Many2one('med.consultation', string='Consultation', required=True)
    patient_id = fields.Many2one('med.patient', string='Patient', related='consultation_id.patient_id', store=True)
    pharmacist_id = fields.Many2one('med.staff', string='Pharmacist')
    line_ids = fields.One2many('med.pharmacy.order.line', 'order_id', string='Order Lines', copy=True)
    amount_total = fields.Monetary(string='Total Amount', compute='_compute_amount_total', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('dispensed', 'Dispensed'),
        ('paid', 'Paid'),
    ], default='draft', tracking=True)

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(line.subtotal for line in order.line_ids)

    # ---------------- Workflow ----------------
    # 1
    def action_dispense(self):
        for order in self:
            if order.state != 'draft':
                raise UserError("Only draft orders can be dispensed.")

            if not order.line_ids:
                raise UserError("Add at least one product to dispense.")

            for line in order.line_ids:
                product = line.product_id
                if product.qty_available < line.quantity:
                    raise UserError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.qty_available}"
                    )

            # Deduct stock + log movement
            for line in order.line_ids:
                product = line.product_id

                # Deduct
                product.qty_available -= line.quantity

                # Log movement
                self.env['med.pharmacy.stock.move'].create({
                    'product_id': product.id,
                    'order_id': order.id,
                    'patient_id': order.patient_id.id,
                    'quantity': line.quantity,
                    'move_type': 'out',
                })

            order.state = 'dispensed'
            order.pharmacist_id = self.env['med.staff'].search(
                [('user_id', '=', self.env.user.id)],
                limit=1
            )

    def action_mark_paid(self):
        for order in self:
            if order.state != 'dispensed':
                raise UserError("Only dispensed orders can be marked paid.")
            order.state = 'paid'


    def write(self, vals):
        for order in self:
            if order.state in ('dispensed', 'paid'):
                forbidden_fields = {
                    'consultation_id',
                    'line_ids',
                    'patient_id',
                    'pharmacist_id',
                }
                if forbidden_fields.intersection(vals):
                    raise UserError(
                        "Dispensed pharmacy orders are locked and cannot be modified."
                    )
        return super().write(vals)

    def unlink(self):
        for order in self:
            # Lock dispensed/paid orders
            if order.state in ('dispensed', 'paid'):
                raise UserError(
                    "Dispensed or paid pharmacy orders cannot be deleted."
                )
            # Only Admin can delete draft orders
            if not self.env.user.has_group('medisite_clinic.group_med_admin'):
                raise UserError(
                    "Only Admin users can delete pharmacy orders."
                )
        return super(MedPharmacyOrder, self).unlink()



class MedPharmacyOrderLine(models.Model):
    _name = 'med.pharmacy.order.line'
    _description = 'Pharmacy Order Line'

    order_id = fields.Many2one('med.pharmacy.order', string='Order', required=True, ondelete='cascade')
    product_id = fields.Many2one('med.pharmacy.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', required=True, default=1.0)
    unit_price = fields.Float(string='Unit Price', related='product_id.unit_price', store=True, readonly=True)
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)

    def write(self, vals):
        for line in self:
            if line.order_id.state in ('dispensed', 'paid'):
                raise UserError(
                    "You cannot modify order lines after the order has been dispensed."
                )
        return super().write(vals)

    def unlink(self):
        for line in self:
            if line.order_id.state in ('dispensed', 'paid'):
                raise UserError(
                    "Cannot delete order lines from a dispensed order."
                )
            if not self.env.user.has_group('medisite_clinic.group_med_admin'):
                raise UserError(
                    "Only Admin users can delete pharmacy order lines."
                )
        return super(MedPharmacyOrderLine, self).unlink()

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price
