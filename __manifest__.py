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
    'depends': ['base', 'web', 'mail', 'account', 'bus'],
    'assets': {
        'web.assets_backend': [
            'medisite_clinic/static/src/css/patient_list.css',
            'medisite_clinic/static/src/css/ipd_kanban.css',
            'medisite_clinic/static/src/css/consultation_premium.css',
            'medisite_clinic/static/src/js/notification_service.js',
        ],
    },

    'data': [
        'security/med_security.xml',
        'security/ir.model.access.csv',
        'data/med_pharmacy_sequence.xml',
        'data/med_ipd_sequence.xml',
        
        # Reports (Must load before views that reference them)
        'reports/prescription_report.xml',
        'reports/patient_history_report.xml',
        
        # Actions
        'views/med_pharmacy_actions.xml',
        
        # Menus (Root menus must load before sub-menus in other files)
        'views/menu.xml',

        # Views
        'views/med_staff_views.xml',
        'views/med_patient_views.xml',
        'views/med_consultation_views.xml',
        'views/med_icd10_views.xml',
        'views/med_consultation_audit_views.xml',
        'views/med_pharmacy_product_views.xml',
        'views/med_pharmacy_order_views.xml',
        'views/med_pharmacy_batch_views.xml',
        'views/med_pharmacy_stock_move_views.xml',
        'views/med_ipd_views.xml',
        'views/med_reports.xml',
        'views/homepage_template.xml',
        
        'data/company_logo_data.xml',
    ],
    'installable': True,
    'application': True,
}
