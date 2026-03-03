from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class RepairWorkorder(models.Model):
    _name = 'repair.workorder'
    _description = 'Repair Workorder'
    _order = 'id desc'

    name = fields.Char(string='Operação', required=True)
    repair_id = fields.Many2one('repair.order', required=True, ondelete='cascade')

    workcenter_id = fields.Many2one(
        'mrp.workcenter',
        string='Centro de Trabalho',
        required=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Operador',
        required=True
    )

    state = fields.Selection([
        ('ready', 'Pronto'),
        ('progress', 'Em Execução'),
        ('blocked', 'Bloqueado'),
        ('done', 'Finalizado')
    ], default='ready', tracking=True)

    date_start = fields.Datetime()
    date_finished = fields.Datetime()

    duration = fields.Float(
        string="Duração (min)",
        compute="_compute_duration",
        store=True
    )

    machine_in_use = fields.Boolean(
        compute="_compute_machine_in_use"
    )

    @api.depends('date_start', 'date_finished')
    def _compute_duration(self):
        for rec in self:
            if rec.date_start:
                end = rec.date_finished or fields.Datetime.now()
                rec.duration = (end - rec.date_start).total_seconds() / 60
            else:
                rec.duration = 0

    @api.depends('workcenter_id', 'state')
    def _compute_machine_in_use(self):
        for rec in self:
            in_use = self.search([
                ('workcenter_id', '=', rec.workcenter_id.id),
                ('state', '=', 'progress'),
                ('id', '!=', rec.id)
            ])
            rec.machine_in_use = bool(in_use)

    def action_start(self):
        for rec in self:
            if rec.repair_id.state != 'confirmed':
                raise UserError("O Repair precisa estar confirmado.")
            if rec.machine_in_use:
                raise UserError("Máquina já está em uso.")
            rec.state = 'progress'
            rec.date_start = fields.Datetime.now()

    def action_block(self):
        self.state = 'blocked'

    def action_done(self):
        self.state = 'done'
        self.date_finished = fields.Datetime.now()
