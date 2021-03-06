# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Deltatech All Rights Reserved
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




from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp import models, fields, api, _
from openerp.tools.translate import _
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp


class deltatech_expenses_deduction(models.Model):
    _name = 'deltatech.expenses.deduction'  
    _inherit = ['mail.thread']
    _description = 'Expenses Deduction'    
    _order = "date_expense desc, id desc"
    _rec_name = "number"

 

    def _get_journal(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        res = journal_pool.search(cr, uid, [('type', '=', 'cash')], limit=1)
        return res and res[0] or False



    def _get_account_diem(self, cr, uid, context=None):
        account_pool = self.pool.get('account.account')
        try:
            account_id  = account_pool.search(cr, uid, [('code','ilike','625')], limit=1)[0]   ## Cheltuieli cu deplasari
        except (orm.except_orm, ValueError):
            try:
                account_id = account_pool.search(cr, uid, [('user_type.report_type','=','expense'), ('type','!=','view')], limit=1)[0]
            except (orm.except_orm, ValueError):
                account_id = False
        return   account_id 
   
    """
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if context is None: context = {}
        return [(r['id'], (r['number'] + str("%.2f" % r['amount']) or '')) 
                for r in self.read(cr, uid, ids, ['number','amount'], context, load='_classic_write')]
    """
    

       
    number = fields.Char(string='Number', size=32, readonly=True,)
    state = fields.Selection([
            ('draft','Draft'),
            ('done','Done'),
            ('cancel','Cancelled'),
            ],string='Status', select=True, readonly=True, track_visibility='onchange', default='draft',
            help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed expenses deduction. \
            \n* The \'Done\' status is set automatically when the expenses deduction is confirm.  \
            \n* The \'Cancelled\' status is used when user cancel expenses deduction.')     
    date_expense = fields.Date(string='Expense Date',  readonly=True, states={'draft':[('readonly',False)]}, select=True)
    date_advance = fields.Date(string='Advance Date',  readonly=True, states={'draft':[('readonly',False)]}, )
    travel_order = fields.Char(string='Travel Order', readonly=True, states={'draft':[('readonly',False)]})
        
    company_id = fields.Many2one('res.company', string='Company', required=True)
    employee_id = fields.Many2one('res.partner', string="Employee", required=True, readonly=True, states={'draft':[('readonly',False)]}, domain=[('is_company','=',False)])
#        'expenses_line_ids':fields.one2many('deltatech.expenses.deduction.line','expenses_deduction_id','Vouchers'),
    line_ids = fields.One2many('account.voucher','expenses_deduction_id',string='Vouchers',
                                      domain=[('type','=','purchase')], context={'default_type':'purchase'}, readonly=True, states={'draft':[('readonly',False)]})  
    payment_ids = fields.One2many('account.voucher','expenses_deduction_id',string='Payments',
                                       domain=[('type','=','payment')], context={'default_type':'payment'}, readonly=True) 
    note = fields.Text(string='Note')
    amount = fields.Float(  string='Total Amount', digits=dp.get_precision('Account'),compute="_compute_amount") 
    amount_vouchers = fields.Float(  string='Vouchers Amount', digits=dp.get_precision('Account'),compute="_compute_amount")     
    advance = fields.Float(string='Advance', digits=dp.get_precision('Account'),  readonly=True, states={'draft':[('readonly',False)]}  )
    difference = fields.Float( string='Difference', digits=dp.get_precision('Account'),compute="_compute_amount") 
    
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, required=True, compute="_compute_currency") 
     
    journal_id =fields.Many2one('account.journal', string='Journal', required=True, readonly=True, states={'draft':[('readonly',False)]})
    journal_payment_id = fields.Many2one('account.journal', string='Journal payment', required=True) # readonly=True, states={'draft':[('readonly',False)]}),
       # 'account_id':fields.many2one('account.account','Account', required=True, readonly=True, states={'draft':[('readonly',False)]}), 
    account_diem_id  = fields.Many2one('account.account',string='Account', required=True, readonly=True, states={'draft':[('readonly',False)]}) 
    move_id = fields.Many2one('account.move', string='Account Entry',readonly=True )
    
    move_ids = fields.One2many('account.move.line', related='move_id.line_id',  string='Journal Items', readonly=True)
    
    diem = fields.Float(string='Diem', digits_compute=dp.get_precision('Account'),  readonly=True, states={'draft':[('readonly',False)]}, default=42.5  )
    days = fields.Integer(string='Days', readonly=True, states={'draft':[('readonly',False)]}  ) 
    
    total_diem = fields.Float( string='Total Diem', digits=dp.get_precision('Account'),compute="_compute_amount") 
    

    _defaults = { 
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
        #'date_advance': fields.date.context_today,
        #'date_expense': fields.date.context_today,
        #'state': 'draft',
        'journal_id':_get_journal,
        'account_diem_id':_get_account_diem,
        #'employee_id': lambda cr, uid, id, c={}: id,
        'currency_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, context=c).company_id.currency_id.id,
        #'diem': 42.5,
    }

    """
    def default_get(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        account_obj = self.pool.get('account.account')
        values = super(deltatech_expenses_deduction, self).default_get(cr, uid, fields_list, context=context)
        if 'account_id' in fields_list:
            try:
                account_id  = account_obj.search(cr, uid, [('code','ilike','542')])[0]
            except (orm.except_orm, ValueError):
                account_id = False
            values.update({'account_id': account_id})     
        return values   
    """
    
    @api.one
    @api.onchange('date_advance')
    def onchange_date_advance(self):
        if self.date_advance > self.date_expense:
            self.date_expense = self.date_advance
    
    
    @api.multi
    @api.depends('line_ids','days','diem','advance')
    def _compute_amount(self):
        for expense in self:
            total = 0.0
            for line in expense.line_ids:
                total += line.amount
            
            expense.amount_vouchers =   total
            expense.total_diem  =    expense.days * expense.diem 
            expense.amount = expense.amount_vouchers + expense.total_diem
            
            expense.difference = expense.amount - expense.advance 
            

    @api.multi
    def _compute_currency(self):
        for expense in self:
            expense.currency_id = expense.company_id.currency_id.id
             
    
    def unlink(self, cr, uid, ids, context=None):
        for t in self.read(cr, uid, ids, ['state'], context=context):
            if t['state'] not in ('draft', 'cancel'):
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete Expenses Deduction(s) which are already done.'))
        return super(deltatech_expenses_deduction, self).unlink(cr, uid, ids, context=context) 
 
    @api.multi
    def invalidate_expenses(self):
        
        moves = self.env['account.move']
        for expenses in self:
            if expenses.move_id:
                moves += expenses.move_id

         
        self.write({'state': 'draft', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        
        # anulare plati inregistrate
        for expenses in self:    
            expenses.payment_ids.cancel_voucher() 
            expenses.payment_ids.action_cancel_draft()
            statement_lines = self.env['account.bank.statement.line'].search([('voucher_id','in',expenses.payment_ids.ids)])
            if statement_lines:
                statement_lines.unlink() 
            expenses.payment_ids.unlink() 
        
        # anulare postare chitante.
        for expenses in self: 
            expenses.line_ids.cancel_voucher()
            expenses.line_ids.action_cancel_draft() 
        
        statement_lines = self.env['account.bank.statement.line'].search([('expenses_deduction_id','=',expenses.id)])
        if statement_lines:
                statement_lines.unlink() 
        
        return True 
 
    def validate_expenses(self, cr, uid, ids, context=None):
        voucher_pool = self.pool.get('account.voucher')
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        seq_pool = self.pool.get('ir.sequence')
        payment_id = False
        #poate ar fi bine daca  bonurile fiscale de la acelasi furnizor sa fie unuite intr-o singura chitanta.
        for expenses in self.browse(cr, uid, ids, context=context):
            voucher_ids = []
            for voucher in expenses.line_ids:
                if voucher.state == 'draft':
                    voucher_ids.append(voucher.id)
            voucher_pool.proforma_voucher(cr,uid,voucher_ids, context=context)
            for voucher in expenses.line_ids: 
                if not voucher.paid: 
                    partner_id = self.pool.get('res.partner')._find_accounting_partner(voucher.partner_id).id 
                    line_dr_ids = []
                    line_cr_ids = []
                    for line in voucher.move_ids: # de regula este o singura linie
                        if line.state == 'valid' and line.account_id.type == 'payable' and not line.reconcile_id:
                            amount_unreconciled = abs(line.amount_residual_currency)
                            rs = {
                                'name':line.move_id.name,
                                'type': line.credit and 'dr' or 'cr',
                                'move_line_id':line.id,
                                'account_id':line.account_id.id,
                                'amount_original': abs(line.amount_currency),
                                'amount': amount_unreconciled,
                                'date_original':line.date,
                                'date_due':line.date_maturity,
                                'amount_unreconciled': amount_unreconciled,
                                'currency_id': voucher.currency_id.id,
                                'reconcile':True
                            }
                            if rs['type'] == 'cr':
                                line_cr_ids.append([0,False,rs])
                            else:
                                line_dr_ids.append([0,False,rs])                          
                    
                    payment_id = voucher_pool.create(cr, uid, {
                                                           'journal_id':expenses.journal_payment_id.id, 
                                                           'account_id':expenses.journal_payment_id.default_credit_account_id.id, 
                                                           'type':'payment', 
                                                           # care este data platii ?????/
                                                           'date':        voucher.date,
                                                           'partner_id': voucher.partner_id.id, 
                                                           'reference':voucher.reference,
                                                           'amount':voucher.amount,
                                                           'line_dr_ids':line_dr_ids,
                                                           'line_cr_ids':line_cr_ids,
                                                           'expenses_deduction_id':expenses.id
                                                           }, 
                                                context = {'default_type':'payment',
                                                           'type':'payment',
                                                           'default_partner_id': partner_id ,
                                                           'default_partner_id': voucher.partner_id.id, 
                                                           'default_amount': voucher.amount,
                                                           'partner_id': voucher.partner_id.id, 
                                                           'default_reference':voucher.reference}) 
                    
                    voucher_pool.proforma_voucher(cr,uid,payment_id, context=context)
 
                    
            # TODO: de adaugat platile ca refeninta de decont
            if not expenses.number:
                name = seq_pool.next_by_id(cr, uid, expenses.journal_id.sequence_id.id, context=context)
            else:
                name = expenses.number
            # Create the account move record.
            line_ids = []
            # nota contabila prin care banii au iesit din casa 
            if  expenses.advance:
                move_line_dr = {
                    'name':  name or '/',
                    'debit': expenses.advance,
                    'credit': 0.0,
                    'account_id': expenses.journal_payment_id.default_debit_account_id.id,  #542
                    'journal_id': expenses.journal_id.id,
                    'partner_id': expenses.employee_id.id, 
                    'date': expenses.date_advance,
                    'date_maturity': expenses.date_advance
                }
                move_line_cr = {
                    'name': name or '/',
                    'debit': 0.0,
                    'credit': expenses.advance,
                    'account_id': expenses.journal_id.default_credit_account_id.id,   #512
                    'journal_id': expenses.journal_id.id,
                    'partner_id': expenses.employee_id.id, 
                    'date': expenses.date_advance,
                    'date_maturity': expenses.date_advance
                }    
                line_ids.append([0,False,move_line_dr])   
                line_ids.append([0,False,move_line_cr])
                
                # si acum scriu in registrul de casa valoarea   
            # avansul trebuie trecut si in jurnalul de casa!
            
            if expenses.difference < 0:  
                move_line_cr = {
                    'name':  name or '/',
                    'debit': 0.0,
                    'credit':  abs(expenses.difference),
                    'account_id': expenses.journal_payment_id.default_credit_account_id.id,
                    'journal_id': expenses.journal_id.id,
                    'partner_id': expenses.employee_id.id, 
                    'date': expenses.date_expense,
                    'date_maturity': expenses.date_expense
                }
                move_line_dr = {
                    'name': name or '/',
                    'debit': abs(expenses.difference),
                    'credit': 0.0,
                    'account_id': expenses.journal_id.default_debit_account_id.id,
                    'journal_id': expenses.journal_id.id,
                    'partner_id': expenses.employee_id.id, 
                    'date': expenses.date_expense,
                    'date_maturity': expenses.date_expense
                }                  
                line_ids.append([0,False,move_line_dr])   
                line_ids.append([0,False,move_line_cr]) 

            if expenses.difference > 0:  
                move_line_dr = {
                    'name':  name or '/',
                    'debit': expenses.difference,
                    'credit': 0.0,
                    'account_id': expenses.journal_payment_id.default_debit_account_id.id,  #542
                    'journal_id': expenses.journal_id.id,
                    'partner_id': expenses.employee_id.id, 
                    'date': expenses.date_expense,
                    'date_maturity': expenses.date_expense
                }
                move_line_cr = {
                    'name': name or '/',
                    'debit': 0.0,
                    'credit': expenses.difference,
                    'account_id': expenses.journal_id.default_credit_account_id.id,   #512
                    'journal_id': expenses.journal_id.id,
                    'partner_id': expenses.employee_id.id, 
                    'date': expenses.date_expense,
                    'date_maturity': expenses.date_expense
                }                 
                line_ids.append([0,False,move_line_dr])   
                line_ids.append([0,False,move_line_cr]) 

            if expenses.total_diem:
                move_line_dr = {
                    'name':  name or '/',
                    'debit': expenses.total_diem,
                    'credit': 0.0,
                    'account_id': expenses.account_diem_id.id, 
                    'journal_id': expenses.journal_id.id,
                    'partner_id': expenses.employee_id.id, 
                    'date': expenses.date_expense,
                    'date_maturity': expenses.date_expense
                }
                move_line_cr = {
                    'name': name or '/',
                    'debit': 0.0,
                    'credit': expenses.total_diem,
                    'account_id': expenses.journal_payment_id.default_credit_account_id.id,  #542
                    'journal_id': expenses.journal_id.id,
                    'partner_id': expenses.employee_id.id, 
                    'date': expenses.date_expense,
                    'date_maturity': expenses.date_expense
                }                 
                line_ids.append([0,False,move_line_dr])   
                line_ids.append([0,False,move_line_cr])                 

                             
            # si e corect ca un element sa contina note contabile cu date diferite ????    
            move_id = move_pool.create(cr, uid, {
                                        'name': name or '/',
                                        'journal_id': expenses.journal_id.id,
                                        'date': expenses.date_expense,
                                        'ref': name or '',
                                        'line_id':line_ids,
                                    }, context=context)
            name = move_pool.browse(cr, uid, move_id, context=context).name
            if payment_id:
                voucher_pool.write(cr,uid, [payment_id],{'state':'posted'})
            self.write(cr, uid, [expenses.id], {'state':'done','move_id':move_id,'number': name})
        
        self.write_to_statement_line(cr, uid, ids, context)   
        return True  

    @api.multi
    def write_to_statement_line(self):
        
        def get_statement(journal_id, date ):
            statement  = self.env['account.bank.statement'].search( [('journal_id', '=', journal_id.id), 
                                                                     ('date', '=', date)])
            if not statement:
                vals = {
                    'journal_id': journal_id.id,
                    'state': 'draft',
                    'date': date,
                }
                statement  = self.env['account.bank.statement'].create( vals)
                statement.onchange_journal_id(   journal_id.id )
                statement.button_open()
            else:
                statement = statement[0]
            
            if statement.state != 'open':
                raise osv.except_osv(_('Error!'), _('The cash statement of journal %s from date is not in open state, please open it \n'
                                                    'to create the line in  it "%s".') % (journal_id.name, date))
            return statement
            
            
        for expenses in self:
            if expenses.journal_id.type == 'cash':
                if expenses.advance:
                    statement  = get_statement(expenses.journal_id,expenses.date_advance)
                    args = {
                        'amount': - expenses.advance,
                        'date':  expenses.date_advance,
                        'name': _("Decont cheltuieli"),
                        'account_id': False,
                        'partner_id': expenses.employee_id.id,
                        'statement_id': statement.id,
                        'journal_id': expenses.journal_id.id,
                        'ref': str(expenses.number),
                        #'voucher_id': voucher.id,
                        'journal_entry_id': expenses.move_id.id,
                        'expenses_deduction_id':expenses.id
                    }
                    self.env['account.bank.statement.line'].create(  args )
                if expenses.difference:
                    statement  = get_statement(expenses.journal_id,expenses.date_expense)
                    args = {
                        'amount': - expenses.difference,
                        'date':  expenses.date_expense,
                        'name': _("Decont cheltuieli"),
                        'account_id': False,
                        'partner_id': expenses.employee_id.id,
                        'statement_id': statement.id,
                        'journal_id': expenses.journal_id.id,
                        'ref': str(expenses.number),
                        #'voucher_id': voucher.id,
                        'journal_entry_id': expenses.move_id.id,
                        'expenses_deduction_id':expenses.id
                    }
                    self.env['account.bank.statement.line'].create(  args )  
                          
        return True

    @api.multi
    def cancel_expenses(self): 
        self.write(  {'state':'cancel'} ) 
        return True  

    
deltatech_expenses_deduction()    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: