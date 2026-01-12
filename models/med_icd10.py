from odoo import models, fields

class MedICD10(models.Model):
    _name = 'med.icd10'
    _description = 'ICD-10 Diagnosis Code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Diagnosis Name', required=True)
    description = fields.Text(string='Description')
