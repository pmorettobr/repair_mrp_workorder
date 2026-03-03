from odoo import models, fields

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    workorder_ids = fields.One2many(
        'repair.workorder',
        'repair_id',
        string='Ordens de Trabalho'
    )
