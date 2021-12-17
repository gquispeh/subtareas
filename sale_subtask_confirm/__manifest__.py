# -*- encoding: utf-8 -*-
{
	'name': 'Sale Subtask',
	'category': 'Sale',
	'author': 'DT DATA',
	'depends': ['base','sale','project','sale_project'],
	'version': '1.0.0',
	'description': """
	- Generacion de Subtask segun el cambio del modelo de lineas de venta
	""",
	'data':[
		'views/views.xml',
		'security/ir.model.access.csv',
	],
	'installable': True
}
