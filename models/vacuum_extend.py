from odoo import models, api, fields
from datetime import timedelta

class AutoVacuumExtend(models.AbstractModel):
    _name = 'autovacuum.extend'
    _description = 'Custom Transient Auto Vacuum'

    @api.model
    def _clean_transient_batch(self, model_name, days=1, batch=1000):
        limit_date = fields.Datetime.now() - timedelta(days=days)
        Model = self.env[model_name]
        while True:
            recs = Model.search([('create_date', '<', limit_date)], limit=batch)
            if not recs:
                break
            recs.unlink()
            self._cr.commit()

    @api.model
    def cron_clean_transients(self):
        models = [
            'mail.compose.message',
            'ir.attachment',
            'mail.wizard.invite',
            'some.custom.transient.model',
        ]
        for model in models:
            try:
                self._clean_transient_batch(model)
            except Exception as e:
                _logger = self.env['ir.logging']
                _logger.sudo().create({
                    'name': 'autovacuum.extend',
                    'type': 'server',
                    'level': 'ERROR',
                    'message': f'Error cleaning {model}: {str(e)}',
                    'path': 'autovacuum_extend',
                    'func': 'cron_clean_transients',
                    'line': 0,
                })
