from odoo import models, fields, api

class MedPharmacyProduct(models.Model):
    _inherit = 'med.pharmacy.product'

    # -----------------------------------
    # DYNAMIC STOCK CALCULATION
    # -----------------------------------
    qty_available = fields.Float(
        string='Quantity On Hand',
        compute='_compute_qty_available',
        store=True,
    )

    @api.depends('stock_ids.quantity')
    def _compute_qty_available(self):
        for product in self:
            product.qty_available = sum(product.stock_ids.mapped('quantity'))

    # -----------------------------------
    # STOCK CLASSIFICATION
    # -----------------------------------
    is_consumable = fields.Boolean(
        string="Consumable",
        help="Tick if this is a non-returnable medical consumable (gloves, syringes, gauze, etc)"
    )

    # -----------------------------------
    # STOCK CONTROL LEVELS
    # -----------------------------------
    min_stock = fields.Float(
        string="Minimum Stock Level",
        help="When stock falls below this level, it is considered critical"
    )

    max_stock = fields.Float(
        string="Maximum Stock Level",
        help="Maximum quantity allowed in storage"
    )

    reorder_level = fields.Float(
        string="Reorder Level",
        help="System should suggest reordering when stock goes below this level"
    )

    is_low_stock = fields.Boolean(
        string="Is Low Stock",
        compute="_compute_stock_status",
        store=True,
    )

    needs_reorder = fields.Boolean(
        string="Needs Reorder",
        compute="_compute_stock_status",
        store=True,
    )

    @api.depends('qty_available', 'min_stock', 'reorder_level')
    def _compute_stock_status(self):
        for product in self:
            product.is_low_stock = product.qty_available <= product.min_stock if product.min_stock > 0 else False
            product.needs_reorder = product.qty_available <= product.reorder_level if product.reorder_level > 0 else False

    # -----------------------------------
    # BATCH TRACKING
    # -----------------------------------
    batch_ids = fields.One2many(
        'med.pharmacy.batch',
        'product_id',
        string="Batches"
    )

    # -----------------------------------
    # MULTI-LOCATION STOCK
    # -----------------------------------
    stock_ids = fields.One2many(
        'med.pharmacy.stock',
        'product_id',
        string="Stock By Location"
    )
