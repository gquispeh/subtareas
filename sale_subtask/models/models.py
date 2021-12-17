from odoo import models, fields, api

class Task(models.Model):
    _inherit="project.task"

    parent_id = fields.Many2one('project.task', string='Linea de Venta')

class Task(models.Model):
    _inherit="sale.order.line"

    child_ids = fields.One2many('project.task', 'parent_id', string='Tareas')
