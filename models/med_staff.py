from odoo import models, fields, api
from odoo.exceptions import UserError


class MedStaff(models.Model):
    _name = 'med.staff'
    _description = 'Medical Staff'

    name = fields.Char(required=True)
    employee_id = fields.Char()
    job_title = fields.Char()
    department = fields.Char()

    user_id = fields.Many2one('res.users', string="System User")

    phone = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    address = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state')
    country_id = fields.Many2one('res.country')

    dob = fields.Date()
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ])

    hire_date = fields.Date()
    qualification = fields.Text()
    license_number = fields.Char()
    emergency_contact = fields.Char()

    role = fields.Selection([
        ('nurse', 'Nurse'),
        ('doctor', 'Doctor'),
        ('lab_tech', 'Lab Technician'),
        ('admin', 'Administrator'),
        ('reception', 'Reception'),
    ], default='nurse')

    active = fields.Boolean(default=True)
    image = fields.Binary()

    # ---------------------------------------------------------
    # CREATE LOGIN ACTION
    # ---------------------------------------------------------
    def action_create_user(self):
        self.ensure_one()

        if self.user_id:
            raise UserError("This staff already has a login.")

        if not self.email:
            raise UserError("Staff must have an email to create login.")

        group_map = {
            'nurse': 'medisite_clinic.group_med_nurse',
            'doctor': 'medisite_clinic.group_med_doctor',
            'lab_tech': 'medisite_clinic.group_med_lab',
            'admin': 'medisite_clinic.group_med_admin',
        }

        user = self.env['res.users'].sudo().create({
            'name': self.name,
            'login': self.email,
            'email': self.email,
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref(group_map[self.role]).id,
            ])],
        })

        self.user_id = user.id
