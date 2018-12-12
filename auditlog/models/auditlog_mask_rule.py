# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class AuditlogMaskRule(models.Model):
    _name = 'auditlog.rule.mask'
    _description = 'Auditlog field value masking rule.'
    _rec_name = 'field_id'

    active = fields.Boolean(default=True)
    model_id = fields.Many2one(
        comodel_name='ir.model',
        string="Model")
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string="Field",
        required=True,
    )
    regex = fields.Char(
        string="Regular Expression",
        help="Specify a regular expression to replace text with.")

    _sql_constraints = [(
        'Unique model and field combination',
        'UNIQUE(model_id, field_id)',
        'There can only one masking rule per model field.'
    )]

    @api.model
    def create(self, vals):
        """ Refresh the mask cache when a new masking rule is defined. """
        res = super(AuditlogMaskRule, self).create(vals)
        self._build_mask_field_cache()
        return res

    @api.multi
    def write(self, vals):
        """ Refresh the mask cache when altering a rule. """
        res = super(AuditlogMaskRule, self).write(vals)
        self._build_mask_field_cache()
        return res

    @api.multi
    def unlink(self):
        """ Refresh the mask cache when clearing a rule. """
        res = super(AuditlogMaskRule, self).unlink()
        self._build_mask_field_cache()
        return res

    @api.model
    def _build_mask_field_cache(self):
        """ Construct a cache to mask auditlog log line entry values. """
        _logger.info("Clearing auditlog rule mask cache.")
        mask_rules = self.env['auditlog.rule.mask'].search([])
        mask_map = {}
        for mask in mask_rules:
            model = mask.field_id.model_id
            # add model as key
            mask_map.setdefault(model.model, {})
            mask_map[model.model].update(
                {mask.field_id.name: mask.regex or None})
        _logger.info(str(mask_map))
        self.env.registry._auditlog_mask_cache = mask_map

    @api.onchange('model_id')
    def _onchange_model_id(self):
        """ Ensure the user specifies the model so we can filter out double
        field names. """
        if not self.model_id:
            return
        return {'domain': {'field_id': [('model_id', '=', self.model_id.id)]}}
