--  balance negativo

INSERT INTO account_move_line (name, quantity, product_uom_id, product_id, debit, credit, balance, debit_cash_basis,
                               credit_cash_basis, balance_cash_basis, amount_currency, company_currency_id, currency_id,
                               amount_residual, amount_residual_currency, tax_base_amount, account_id, move_id, ref,
                               payment_id, statement_line_id, statement_id, reconciled, full_reconcile_id, journal_id,
                               blocked, date_maturity, date, tax_line_id, analytic_account_id, company_id, invoice_id,
                               partner_id, user_type_id, tax_exigible, create_uid, create_date, write_uid, write_date,
                               expense_id, expected_pay_date, internal_note, next_action_date, followup_line_id,
                               followup_date, branch_id, bedrsrd_moved0, bedrusd_moved0, opercde, vlnr_moved0,
                               gallon_moved0, plcde, handl_moved0, maalt_moved0, pax_moved0, mandgn_moved0,
                               sdatum_moved0, kstnpl6_moved0, kstnpl7_moved0, persnr_moved0, ponr, galprijs_moved0,
                               betrekdg, betrekmd, betrekjr, factdg, factmd, factjr, vltype, vltreg, faktnr, omschr,
                               controlle, bedrsrd, bedrusd, gallon, handl, maalt, pax, mandgn, sdatum, kstnpl6, kstnpl7,
                               persnr, galprijs, pnr, regnr, vlnr)
                                VALUES ('Unbalance adjustment', NULL, NULL, NULL, 0.00233333333333413333, 0.0,
                                        0.00233333333333413333, 0.00, 0.0, 0.0, 0.0, 2, NULL, 0.00, 0.0, 0.00, 8166,
                                        156608, 'AUA_BANK 05-2020', NULL, NULL, NULL, false, NULL, 20, false,
                                        '2020-05-01', '2020-03-01', NULL, 253, 2, NULL, NULL, 17, true, 33,
                                        '2020-05-18 23:14:29.059839', 33, '2020-05-18 23:14:29.059839', NULL, NULL,
                                        NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2', NULL, NULL, NULL, NULL, NULL,
                                        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '1', '5', '2020', NULL, NULL,
                                        NULL, NULL, 'False', NULL, 'Unbalance adjustment', NULL, '0.0', '0.0', '0.00',
                                        NULL, '0', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- balance positivo

INSERT INTO account_move_line (name, quantity, product_uom_id, product_id, debit, credit, balance, debit_cash_basis,
                               credit_cash_basis, balance_cash_basis, amount_currency, company_currency_id, currency_id,
                               amount_residual, amount_residual_currency, tax_base_amount, account_id, move_id, ref,
                               payment_id, statement_line_id, statement_id, reconciled, full_reconcile_id, journal_id,
                               blocked, date_maturity, date, tax_line_id, analytic_account_id, company_id, invoice_id,
                               partner_id, user_type_id, tax_exigible, create_uid, create_date, write_uid, write_date,
                               expense_id, expected_pay_date, internal_note, next_action_date, followup_line_id,
                               followup_date, branch_id, bedrsrd_moved0, bedrusd_moved0, opercde, vlnr_moved0,
                               gallon_moved0, plcde, handl_moved0, maalt_moved0, pax_moved0, mandgn_moved0,
                               sdatum_moved0, kstnpl6_moved0, kstnpl7_moved0, persnr_moved0, ponr, galprijs_moved0,
                               betrekdg, betrekmd, betrekjr, factdg, factmd, factjr, vltype, vltreg, faktnr, omschr,
                               controlle, bedrsrd, bedrusd, gallon, handl, maalt, pax, mandgn, sdatum, kstnpl6, kstnpl7,
                               persnr, galprijs, pnr, regnr, vlnr)
                               VALUES ('Unbalance adjustment', NULL, NULL, NULL, 0.0, 0.00059065873217098321, -0.00059065873217098321, 0.0, 0.0, 0.0,
                                       0.0, 2, NULL, 0.00, 0.0, 0.00, 8166, 146034, 'GSA_POS 03-2020', NULL, NULL, NULL,
                                       false, NULL, 20, false, '2020-03-01', '2020-03-01', NULL, 253, 2, NULL, NULL, 17,
                                       true, 33, '2020-05-18 23:14:29.059839', 33, '2020-05-18 23:14:29.059839', NULL,
                                       NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2', NULL, NULL, NULL, NULL,
                                       NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '1', '3', '2020', NULL,
                                       NULL, NULL, NULL, 'False', NULL, 'Unbalance adjustment', NULL, '0.0', '0.0',
                                       '0.00', NULL, '0', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);