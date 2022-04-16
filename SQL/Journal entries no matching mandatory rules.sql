SELECT DISTINCT
                AML.id,
                RC.name,
                AML.name,
                AML.ref,
                AA.code,
                AAA.code,
                AML.balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)  AS balance
FROM account_move_line AML
JOIN account_account AA ON (AML.account_id = AA.id)
JOIN account_analytic_account AAA ON (AML.analytic_account_id = AAA.id)
JOIN res_company RC ON (AML.company_id = RC.id)
LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                           AND RCR.name = date_trunc('month', AML.date)::date)
JOIN account_analytic_mandatory AAM ON (AML.account_id = AAM.account_id)
JOIN account_analytic_account_account_analytic_mandatory_vlnr_rel AAAAAMVR
         ON (AML.analytic_account_id = AAAAAMVR.account_analytic_account_id)
WHERE AML.vlnr ISNULL;




SELECT DISTINCT AML.id, RC.name, AML.name, AML.ref, AA.code, AAA.code, AML.credit, AML.debit, AML.balance
FROM account_move_line AML
JOIN account_account AA ON (AML.account_id = AA.id)
JOIN account_analytic_account AAA ON (AML.analytic_account_id = AAA.id)
JOIN res_company RC ON (AML.company_id = RC.id)
JOIN account_analytic_mandatory AAM ON (AML.account_id = AAM.account_id)


