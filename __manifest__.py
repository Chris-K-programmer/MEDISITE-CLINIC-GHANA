{
    'name': 'MediSite Clinic',
    'version': '1.0.0',
    'category': 'Healthcare',
    'summary': 'Medical Center Management Application',
    'description': """
Medical center software including:
- Employee records
- Patient initial consultation
- Nurse, doctor, lab technician workflows
""",
    'author': 'MediSite Services Ghana',
    'depends': ['base', 'web', 'mail',
                ],
    'assets': {
        'web.assets_backend': [
            'medisite_clinic/static/src/css/patient_list.css',
            'medisite_clinic/static/src/css/ipd_kanban.css',
        ],
    },

    'data': [
        'security/med_security.xml',
        'security/ir.model.access.csv',
        'data/med_pharmacy_sequence.xml',
        'data/med_ipd_sequence.xml',
        'views/med_pharmacy_actions.xml',

        'views/med_staff_views.xml',
        'views/med_patient_views.xml',
        'views/med_consultation_views.xml',
        'views/med_icd10_views.xml',
        'views/med_consultation_audit_views.xml',
        'views/med_pharmacy_product_views.xml',
        'views/med_pharmacy_order_views.xml',
        'views/med_pharmacy_stock_move_views.xml',
        'views/med_ipd_views.xml',
        'views/menu.xml',

    ],
    'installable': True,
    'application': True,
}
