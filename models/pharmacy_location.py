from odoo import models, fields

class MedPharmacyLocation(models.Model):
    _name = 'med.pharmacy.location'
    _description = 'Pharmacy Storage Location'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)
