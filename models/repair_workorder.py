# -*- coding: utf-8 -*-
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
        """
        Verifica se o workcenter já está em uso por outra ordem de reparo.
        Correção: evita erro ao criar registro novo (NewId não é inteiro).
        """
        for rec in self:
            domain = [
                ('workcenter_id', '=', rec.workcenter_id.id),
                ('state', '=', 'progress'),
            ]
            # Só exclui o próprio registro se ele já tiver ID inteiro (já salvo no banco)
            if rec.id and isinstance(rec.id, int):
                domain.append(('id', '!=', rec.id))
            
            in_use = self.search(domain)
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
