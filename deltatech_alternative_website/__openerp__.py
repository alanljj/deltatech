# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
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
#
##############################################################################

{
    "name": "Deltatech Website alternative code",
    "version": "1.0",
    "author": "Dorin Hongu",
    "website": "www.terrabit.ro",

    "description": """

Functionalitati:
    - cautare produs dupa cod echivalent
    - afisare igagini produse in magazinul virtual cu watermark

    """,

    "category": "Website",
    "depends": ['deltatech', "website_sale", "deltatech_alternative", 'l10n_ro_invoice_report'],

    'data': ['product_view.xml', 'views/templates.xml'],

    "installable": True,
    'auto_install': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
