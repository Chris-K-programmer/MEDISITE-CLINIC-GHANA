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
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    invoice_count = fields.Integer(compute='_compute_invoice_count')

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = 1 if rec.invoice_id else 0

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
                if not line.batch_id or not line.location_id:
                    raise UserError(f"Please specify Batch and Location to dispense {line.product_id.name}.")

                stock = self.env['med.pharmacy.stock'].search([
                    ('product_id', '=', line.product_id.id),
                    ('batch_id', '=', line.batch_id.id),
                    ('location_id', '=', line.location_id.id)
                ], limit=1)

                if not stock or stock.quantity < line.quantity:
                    raise UserError(f"Insufficient stock for {line.product_id.name} in the selected Batch/Location.")

                stock.quantity -= line.quantity

                # Log movement
                self.env['med.pharmacy.stock.move'].create({
                    'product_id': line.product_id.id,
                    'batch_id': line.batch_id.id,
                    'source_location_id': line.location_id.id,
                    'order_id': order.id,
                    'patient_id': order.patient_id.id,
                    'quantity': line.quantity,
                    'move_type': 'out',
                })

            pharmacist = self.env['med.staff'].search(
                [('user_id', '=', self.env.user.id)],
                limit=1
            )
            order.write({
                'state': 'dispensed',
                'pharmacist_id': pharmacist.id if pharmacist else False,
            })
            
            # Notify Patient/Nurse that Prescription is ready
            group_nurse = self.env.ref('medisite_clinic.group_med_nurse')
            self.env['bus.bus']._sendone(group_nurse, 'medisite_notification', {
                'role': 'pharmacy',
                'patient_name': order.patient_id.name,
                'message': f"Prescription for {order.patient_id.name} has been dispensed and is ready for collection."
            })

    def action_mark_paid(self):
        for order in self:
            if order.state != 'dispensed':
                raise UserError("Only dispensed orders can be marked paid.")
            if order.invoice_id and order.invoice_id.payment_state != 'paid':
                raise UserError("Please register payment on the linked invoice first.")
            order.state = 'paid'

    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            return self.action_view_invoice()

        if not self.patient_id.partner_id:
            self.patient_id._ensure_partner()

        invoice_line_vals = []
        for line in self.line_ids:
            invoice_line_vals.append((0, 0, {
                'name': f"{line.product_id.name} (Batch: {line.batch_id.name if line.batch_id else 'N/A'})",
                'quantity': line.quantity,
                'price_unit': line.unit_price,
            }))

        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.patient_id.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': invoice_line_vals,
        }
        invoice = self.env['account.move'].create(invoice_vals)
        self.with_context(skip_lock=True).invoice_id = invoice.id
        return self.action_view_invoice()

    def action_view_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'target': 'current',
        }


    def write(self, vals):
        # Allow state changes and invoice linking even on locked records
        if any(field in vals for field in ('state', 'invoice_id')):
            return super().write(vals)

        for order in self:
            if order.state in ('dispensed', 'paid') and not self._context.get('skip_lock'):
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
    batch_id = fields.Many2one('med.pharmacy.batch', string='Batch', domain="[('product_id', '=', product_id)]")
    location_id = fields.Many2one('med.pharmacy.location', string='Storage Location')
    
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
