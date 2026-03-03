{
    'name': 'Repair MRP Workorders',
    'version': '16.0.1.0.0',
    'summary': 'Workorders for Repair using MRP Workcenters',
    'category': 'Servicos/Reparo',
    'author': 'Paulo Moretto',
    'depends': ['repair', 'mrp', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_order_views.xml',
        'views/repair_workorder_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'repair_mrp_workorder/static/src/js/timer.js',
        ],
    },
    'installable': True,
    'application': False,
}
