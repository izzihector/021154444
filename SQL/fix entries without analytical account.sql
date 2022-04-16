UPDATE account_move_line
SET analytic_account_id = account_analytic_account.id
FROM account_analytic_account JOIN aml ON (account_analytic_account.code = aml.code)
WHERE aml.id::INT = account_move_line.id