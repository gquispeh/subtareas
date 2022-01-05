{
    'name' : 'Sale Subtask',
    'version': '1.0',
    'depends' : ['base','sale','project','sale_project'],
    'data': [
        'views.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'sale_subtask_search/static/src/**/*',
        ],
    },
    'license': 'LGPL-3',
}
