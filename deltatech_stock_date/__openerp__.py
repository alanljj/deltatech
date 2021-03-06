# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Deltatech All Rights Reserved
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
    "name" : "Deltatech Stock Date",
    "version" : "1.0",
    "author" : "Dorin Hongu",
    "website": "www.terrabit.ro",
    "description": """

Functionalitati:
- preluare data efectiva din trecut in documente 
 
    """,
    
    "category" : "Generic Modules/Other",
    "depends" : ["base", "stock"],


    "data" : [ 'wizard/stock_transfer_details_view.xml'
              
                ],
    'application': False,
    "active": False,
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

