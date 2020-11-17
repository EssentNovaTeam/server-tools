# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, api
from ..base_suspend_security import BaseSuspendSecurityUid, SUSPEND_METHOD


def check_access_rule(self, cr, uid, ids, operation, context=None):
    """ Grant access on transient models in the case of suspended security.
    Otherwise, the ORM will try to compare the suspended security uid with
    the integer create_uids from the records in the database
    """
    if self.is_transient() and isinstance(uid, BaseSuspendSecurityUid):
        return True
    return self.check_access_rule_before_suspend_security(
        cr, uid, ids, operation, context=context)


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def domain_get(self, model_name, mode='read'):
        if isinstance(self.env.uid, BaseSuspendSecurityUid):
            return [], [], ['"%s"' % self.pool[model_name]._table]
        return super(IrRule, self).domain_get(model_name, mode=mode)

    def _register_hook(self, cr):
        if not hasattr(models.BaseModel, SUSPEND_METHOD):
            setattr(models.BaseModel, SUSPEND_METHOD,
                    lambda self: self.sudo(
                        user=BaseSuspendSecurityUid(self.env.uid)))
            models.BaseModel.check_access_rule_before_suspend_security = (
                models.BaseModel.check_access_rule)
            models.BaseModel.check_access_rule = check_access_rule
        return super(IrRule, self)._register_hook(cr)
