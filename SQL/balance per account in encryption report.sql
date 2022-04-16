SELECT account,
--        profit_center,
       sum(balance) as balance
FROM (SELECT AA.code     AS account,
             AA.name     AS account_name,
             AAA.code    AS analytic_account,
             AAA.name    AS analytic_account_name,
             AAA_EM.id   AS profit_center,
             AAA_EM.name AS profit_center_name,
             AAA_EM.code AS profit_center_code,
             SUM(
               EML.encryption / 100 *
               balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)
                 )       AS balance,
             AAT.name    AS tag
      FROM encryption_mapping_line EML
             JOIN encryption_mapping EM ON (EML.encryption_mapping_id = EM.id)
             JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)
             JOIN account_analytic_account AAA_EM ON (AAA_EM.id = EML.cost_center)
             JOIN account_move_line AML ON (AML.analytic_account_id = EML.analytical_account_id)
             JOIN account_account AA ON (AML.account_id = AA.id)
             JOIN account_analytic_account AAA ON (AAA.id = AML.analytic_account_id)
             JOIN account_move AM ON (AM.id = AML.move_id)
             JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AML.account_id)
             JOIN account_account_tag AAT ON (AAAT.account_account_tag_id = AAT.id)
             LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                   AND RCR.name = date_trunc('month', AML.date) :: date)
      WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
        AND AML.date <= '2019-04-30'
        AND AML.date >= '2019-04-01'
        AND AM.state = 'posted'
        AND AA.code SIMILAR TO '(4|8|9)%'
        AND AA.code != '999999'
        AND AFY.date_to >= '2019-09-30'
        AND AFY.date_from <= '2019-04-30'
        AND AAA_EM.code like '6%'
      GROUP BY AA.code, AAA.code, AAA.name, AA.name, AAT.name, AAA_EM.name, AAA_EM.id, AAA_EM.code
        ) AS A
GROUP BY account
--          profit_center
ORDER BY account :: INTEGER;




SELECT      AML.id, EML.encryption
             SUM(
               EML.encryption / 100 *
               balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)
                 )       AS balance
      FROM encryption_mapping_line EML
             JOIN encryption_mapping EM ON (EML.encryption_mapping_id = EM.id)
             JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)
             JOIN account_analytic_account AAA_EM ON (AAA_EM.id = EML.cost_center)
             JOIN account_move_line AML ON (AML.analytic_account_id = EML.analytical_account_id)
             JOIN account_account AA ON (AML.account_id = AA.id)
             JOIN account_analytic_account AAA ON (AAA.id = AML.analytic_account_id)
             JOIN account_move AM ON (AM.id = AML.move_id)
             JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AML.account_id)
             JOIN account_account_tag AAT ON (AAAT.account_account_tag_id = AAT.id)
             LEFT JOIN res_currency_rate RCR ON (AM/sortBy:featuredL.company_currency_id = RCR.currency_id
                                                   AND RCR.name = date_trunc('month', AML.date) :: date)
      WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
        AND AML.date <= '2019-09-30'
        AND AML.date >= '2019-04-01'
        AND AM.state = 'posted'
        AND AA.code SIMILAR TO '(4|8|9)%'
        AND AA.code != '999999'
        AND AFY.date_to >= '2019-09-30'
        AND AFY.date_from <= '2019-04-30'
        AND AAA_EM.code like '6%'
        AND AAA.code = '53300'
group by AML.id, EML.encryption
ORDER BY AML.id
