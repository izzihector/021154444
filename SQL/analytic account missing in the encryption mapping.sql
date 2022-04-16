SELECT AAA.code, AAA.name, AML.id, AML.name, AML.date,
       balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END) balance
FROM account_move_line AML
JOIN account_analytic_account AAA ON AML.analytic_account_id = AAA.id
JOIN account_account AA on AML.account_id = AA.id
LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                           AND RCR.name = date_trunc('month', AML.date)::date)
LEFT JOIN encryption_mapping_line l on AAA.id = l.analytical_account_id
WHERE AA.code similar to '(4|8|9)%'
AND AA.code != '999999'
AND l.analytical_account_id isnull