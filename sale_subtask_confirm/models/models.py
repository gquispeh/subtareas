from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger("info")


class SaleOrderLineSubtask(models.Model):
    _name = "sale.order.line.subtask"
    name = fields.Char(string='Tarea')
    line_id = fields.Many2one('sale.order.line', string="Linea")
    state = fields.Selection([
        ('0', 'borrador'),
        ('1', 'activo')], string='Estado', default='0')


class SaleOrderLineTask(models.Model):
    _inherit = "sale.order.line"
    subtask_ids = fields.One2many(
        'sale.order.line.subtask', 'line_id', string='Sub Tareas')


class SaleOrderTaskWizard(models.TransientModel):
    _name = "sale.order.wizard"

    order_line = fields.Many2one('sale.order', string='Presupuesto')
    line_ids = fields.Many2many('sale.order.line',
                                readonly=True,
                                string='Linea de Venta',
                                compute="compute_sutask_lines",
                                store=True)
    # cambia las tareas asignadas a la linea

    @api.depends('order_line')
    def compute_sutask_lines(self):
        for rec in self:
            # lines = self.env["sale.order.line"].search(
            #    [("order_id", "=", rec.order_line.id), ("product_id.type", "=", "service")]).ids
            #rec.line_ids = lines
            rec.line_ids = rec.order_line.order_line.ids

    def added_task(self):
        self.order_line.write({'sale_task_status': '1'})
        '''for line in self.order_line.line_ids:
            for task in line.subtask_ids:
                values = {"name": line.name,
                          "sale_line_id": line.id,
                          "sale_order_id": self.order_line.id,
                          "partner_id": self.order_line.partner_id.id,
                          "project_id": parent_task.project_id.id,
                          "kanban_state": 'normal',
                          "company_id": self.order_line.company_id.id}
                #parent_task.write({'child_ids': [(0, 0, values)]})
                tarea = self.env['project.task'].create(values)
            #subtask.write({'state': '1'})'''


class SaleOrderLineTaskWizard(models.Model):
    _name = "sale.order.line.wizard"
    line_id = fields.Many2one('sale.order.line', string='Linea de veta')
    subtask_ids = fields.Many2many('sale.order.line.subtask',
                                   readonly=False,
                                   string='Sub Tareas')


class SaleOrderSubTask(models.Model):
    _inherit = "sale.order"

    sale_task_status = fields.Selection([
        ('0', 'wizard'),
        ('1', 'redaccion'),
    ], default='0', string='Sale Task Status')

    def _action_confirm(self):
        """ On SO confirmation, some lines should generate a task or a project. """
        result = super()._action_confirm()
        if len(self.company_id) == 1:
            # All orders are in the same company
            self.order_line.sudo().with_company(
                self.company_id)._timesheet_service_generation()
        else:
            # Orders from different companies are confirmed together
            for order in self:
                order.order_line.sudo().with_company(
                    order.company_id)._timesheet_service_generation()
        self.subtask_task()
        return result

    def subtask_task(self):
        for line in self.order_line:
            product_type = line.product_id.type
            if product_type == 'service':
                line_ids = self.env["sale.order.line.subtask"].sudo().search(
                    [("line_id", "=", line.id)])
                parent_task = self.env["project.task"].sudo().search(
                    [("sale_line_id", "=", line.id)])
                if line_ids:
                    for subtask in line_ids:
                        values = {"name": subtask.name,
                                  "sale_line_id": line.id,
                                  "sale_order_id": self.id,
                                  "partner_id": self.partner_id.id,
                                  "parent_id": parent_task.id,
                                  "project_id": parent_task.project_id.id,
                                  "kanban_state": 'normal',
                                  "company_id": self.company_id.id}
                        parent_task.write({'child_ids': [(0, 0, values)]})
                        subtask.write({'state': '1'})

    def action_view_task_description(self):
        if self.sale_task_status == '0':
            return {
                "type": "ir.actions.act_window",
                'target': 'new',
                'res_model': 'sale.order.wizard',
                "view_id": self.env.ref('sale_subtask_confirm.sale_order_line_task').id,
                'view_mode': 'form',
                'name': u'Sub Tareas',
                'context': {'default_order_line': self.id,
                            },
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_model': 'project.task',
                "view_id": self.env.ref('sale_subtask_search.project_task_view_tree').id,
                'view_mode': 'tree',
                'name': u'Descripcion de Tareas',
                "domain": [["sale_order_id", "=", self.id]],
                'context': {},
            }
