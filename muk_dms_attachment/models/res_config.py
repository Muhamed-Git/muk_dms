## -*- coding: utf-8 -*-

###################################################################################
# 
#    MuK Document Management System
#
#    Copyright (C) 2018 MuK IT GmbH
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
###################################################################################

from ast import literal_eval

from odoo import api, fields, models
from odoo.exceptions import AccessDenied

class DocumentAttachmentSettings(models.TransientModel):
    
    _inherit = 'res.config.settings'
    
    attachment_location = fields.Selection(
        [
            ('db', 'Database'),
            ('file', 'File Storage'),
            ('lobject', 'PSQL Large Object'),
            ('documents', 'MuK Documents'),
        ],
        required=True,
        string='Storage Location',
        help="Attachment storage location.")
    
    attachment_directory = fields.Many2one(
        'muk_dms.directory',
        string="Default Directory",
        help="After a attachment is created, it will be automatically saved to the default directory.")
    
    @api.model
    def get_values(self):
        res = super(DocumentAttachmentSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        attachment_directory = literal_eval(get_param('muk_dms_attachment.attachment_directory', default='False'))
        if attachment_directory and not self.env['muk_dms.directory'].sudo().browse(attachment_directory).exists():
            attachment_directory = False
        res.update(
            attachment_location=get_param('ir_attachment.location', 'file'),
            attachment_directory=attachment_directory,
        )
        return res

    def set_values(self):
        config = self.env['ir.config_parameter']
        get_param = config.sudo().get_param
        set_param = config.sudo().set_param
        location = get_param('ir_attachment.location', None)
        if self.attachment_location and self.attachment_location != location:
            if not self.user_has_groups('muk_dms.group_dms_admin,base.group_erp_manager'):
                raise AccessDenied()
            set_param('ir_attachment.location', self.attachment_location or 'file')
        attachment_directory = get_param('muk_dms_attachment.attachment_directory', None)
        if self.attachment_directory and self.attachment_directory != attachment_directory:
            if not self.user_has_groups('muk_dms.group_dms_admin'):
                raise AccessDenied()
            set_param('muk_dms_attachment.attachment_directory', repr(self.attachment_directory.id))
        super(DocumentAttachmentSettings, self).set_values()

    def attachment_force_storage(self):
        self.env['ir.attachment'].force_storage()
