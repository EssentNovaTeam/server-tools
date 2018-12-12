# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp.tests import SavepointCase


class TestMask(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestMask, cls).setUpClass()

        cls.field = cls.env['ir.model.fields'].search([
            ('model_id.model', '=', 'res.partner'),
            ('name', '=', 'email')
        ])

        # Create a mask rule
        cls.mask = cls.env['auditlog.mask.rule'].create({
            'model_id': cls.field.model_id.id,
            'field_id': cls.field.id,
            'regex': False,
        })

    def test_01_auditlog_mask(self):
        """ A masking rule will mask the value changes in the log lines. """
        customer = self.env['res.partner'].create({
            'name': 'Test Partner',
            'customer': True,
            'email': "email@adress.com"
        })

        log = self.env['auditlog.log'].search([
            ('model_id', '=', self.field.model_id.id),
            ('method', '=', 'create'),
            ('res_id', '=', customer.id)])
        self.assertTrue(log)

        email_entry = log.line_ids.filtered(lambda x: x.field_name == 'email')
        self.assertEqual(email_entry.new_value, "****************")
        self.assertEqual(email_entry.new_value_text, "****************")

        customer.write({'email': "test@me.com"})

        log = self.env['auditlog.log'].search([
            ('model_id', '=', self.field.model_id.id),
            ('method', '=', 'write'),
            ('res_id', '=', customer.id)])
        self.assertTrue(log)

        email_entry = log.line_ids.filtered(lambda x: x.field_name == 'email')
        self.assertEqual(email_entry.old_value, "****************")
        self.assertEqual(email_entry.old_value_text, "****************")
        self.assertEqual(email_entry.new_value, "***********")
        self.assertEqual(email_entry.new_value_text, "***********")

        customer.unlink()

        log = self.env['auditlog.log'].search([
            ('model_id', '=', self.field.model_id.id),
            ('method', '=', 'unlink'),
            ('res_id', '=', customer.id)])
        self.assertTrue(log)

        email_entry = log.line_ids.filtered(lambda x: x.field_name == 'email')
        self.assertEqual(email_entry.old_value, "***********")
        self.assertEqual(email_entry.old_value_text, "***********")