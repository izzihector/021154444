SELECT
       SFRDL.name,
       SUM(balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)) AS balance
FROM slm_financial_reports_define SFRD
       JOIN slm_financial_reports_define_lines SFRDL ON (SFRD.id = SFRDL.report_id)
       JOIN account_account_tag_slm_financial_reports_define_lines_rel AATSFRDLR
         ON (SFRDL.id = AATSFRDLR.slm_financial_reports_define_lines_id)
       JOIN account_account_account_tag AAAT ON (AAAT.account_account_tag_id = AATSFRDLR.account_account_tag_id)
       JOIN account_account AA ON (AAAT.account_account_id = AA.id)
       JOIN account_move_line AML ON (AA.id = AML.account_id)
       JOIN account_move AM ON (AML.move_id = AM.id)
       LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                             AND RCR.name = date_trunc('month', AML.date) :: date)
WHERE SFRD.id = 1
    AND AML.company_id IN (2, 3, 4, 5, 6, 7)
    AND AML.date <= '2019-12-31'
    AND AML.date >= '2019-04-01'
    AND AM.state = 'posted'
    GROUP BY SFRDL.name, SFRDL.sequence
ORDER BY SFRDL.sequence;