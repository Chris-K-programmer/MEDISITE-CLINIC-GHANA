from odoo import models, fields, api
from datetime import date

class MedPatient(models.Model):
    _name = 'med.patient'
    _description = 'Patient Registry'

    name = fields.Char(required=True)
    file_number = fields.Char(index=True)
    dob = fields.Date()
    age = fields.Integer(compute='_compute_age', store=True)
    gender = fields.Selection([('m','MALE'),('f','FEMALE'),])
    nationality = fields.Char()
    occupation = fields.Char()
    employer = fields.Char()

    # --- New fields ---
    photo = fields.Binary(string="Photo")                  # Patient photo
    employee_id = fields.Char(string="Employee ID")        # Optional employee ID

    ipd_ids = fields.One2many('med.ipd', 'patient_id', string="IPD Admissions")

    consultation_ids = fields.One2many(
        'med.consultation',
        'patient_id',
        string='Consultations'
    )

    @api.depends('dob')
    def _compute_age(self):
        for rec in self:
            if rec.dob:
                today = date.today()
                rec.age = today.year - rec.dob.year - (
                    (today.month, today.day) < (rec.dob.month, rec.dob.day)
                )
            else:
                rec.age = 0
