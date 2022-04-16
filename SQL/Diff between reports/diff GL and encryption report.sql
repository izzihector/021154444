--- GL PL
SELECT
--        AML.ID,
--        AA.code,
--        balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END) AS balance
       SUM(balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)) AS balance
FROM account_move_line AML
       JOIN account_move AM ON (AM.id = AML.move_id)
       JOIN account_account AA ON (AML.account_id = AA.id)
       LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                             AND RCR.name = date_trunc('month', AML.date) :: date)
WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
  AND AML.date <= '2019-12-31'
  AND AML.date >= '2019-04-01'
  AND AM.state = 'posted'
  AND AA.code SIMILAR TO '(4|8|9)%'
  AND AA.code != '999999'
-- GROUP BY AA.code
-- ORDER BY AA.code :: INTEGER;
-- ORDER BY AML.id;


--- GL Balance
SELECT
       SUM(balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)) AS balance
FROM account_move_line AML
       JOIN account_move AM ON (AM.id = AML.move_id)
       JOIN account_account AA ON (AML.account_id = AA.id)
       LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                             AND RCR.name = date_trunc('month', AML.date) :: date)
WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
  AND AML.date <= '2019-12-31'
  AND AML.date >= '2019-04-01'
  AND AM.state = 'posted'
  AND (AA.code NOT SIMILAR TO '(4|8|9)%' OR AA.code = '999999');

-- Encryption
SELECT
--        AML.id,
       AA.code AS account,
       SUM(
         EML.encryption / 100 *
         balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)
           )   AS balance
FROM encryption_mapping_line EML
       JOIN encryption_mapping EM ON (EML.encryption_mapping_id = EM.id)
       JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)
       JOIN account_analytic_account AAA_EM ON (AAA_EM.id = EML.cost_center)
       JOIN account_move_line AML ON (AML.analytic_account_id = EML.analytical_account_id)
       JOIN account_account AA ON (AML.account_id = AA.id)
       JOIN account_analytic_account AAA ON (AAA.id = AML.analytic_account_id)
       JOIN account_move AM ON (AM.id = AML.move_id)
--        JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AML.account_id)
--        JOIN account_account_tag AAT ON (AAAT.account_account_tag_id = AAT.id)
       LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                             AND RCR.name = date_trunc('month', AML.date) :: date)
WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
  AND AML.date <= '2019-09-30'
  AND AML.date >= '2019-04-01'
  AND AM.state = 'posted'
  AND AA.code SIMILAR TO '(4|8|9)%'
  AND AA.code != '999999'
  AND AFY.date_to >= '2019-12-31'
  AND AFY.date_from <= '2019-12-31'
  AND AAA_EM.id IN (247, 248, 249, 250, 251, 252, 253)
-- AND AA.code = '420007'
GROUP BY AA.code
ORDER BY AA.code :: INTEGER;
-- GROUP BY AML.id
-- ORDER BY AML.id;


SELECT * from account_move_line WHERE id=1077638



SELECT
       AML.ID,
       AM.name,
       AML.name,
       AML.ref,
       AA.code,
       balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END) AS balance,
       AML.date,
       AML.analytic_account_id
FROM account_move_line AML
       JOIN account_move AM ON (AM.id = AML.move_id)
       JOIN account_account AA ON (AML.account_id = AA.id)
       LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                             AND RCR.name = date_trunc('month', AML.date) :: date)
WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
  AND AML.date <= '2020-03-30'
  AND AML.date >= '2019-04-01'
  AND AM.state = 'posted'
  AND AA.code SIMILAR TO '(4|8|9)%'
  AND AA.code != '999999'
AND AML.analytic_account_id ISNULL
ORDER BY AML.id;









-- Encryption by account
SELECT
       AML.id,
--        AA.code AS account,
       SUM(
         EML.encryption / 100 *
         balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)
           )   AS balance
FROM encryption_mapping_line EML
       JOIN encryption_mapping EM ON (EML.encryption_mapping_id = EM.id)
       JOIN account_fiscal_year AFY ON (EM.fiscal_year = AFY.id)
       JOIN account_analytic_account AAA_EM ON (AAA_EM.id = EML.cost_center)
       JOIN account_move_line AML ON (AML.analytic_account_id = EML.analytical_account_id)
       JOIN account_account AA ON (AML.account_id = AA.id)
       JOIN account_analytic_account AAA ON (AAA.id = AML.analytic_account_id)
       JOIN account_move AM ON (AM.id = AML.move_id)
--        JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AML.account_id)
--        JOIN account_account_tag AAT ON (AAAT.account_account_tag_id = AAT.id)
       LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                             AND RCR.name = date_trunc('month', AML.date) :: date)
WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
  AND AML.date <= '2019-09-30'
  AND AML.date >= '2019-04-01'
  AND AM.state = 'posted'
  AND AA.code SIMILAR TO '(4|8|9)%'
  AND AA.code != '999999'
  AND AFY.date_to >= '2019-12-31'
  AND AFY.date_from <= '2019-12-31'
  AND AAA_EM.id IN (247, 248, 249, 250, 251, 252, 253)
AND AA.code = '801102'
GROUP BY AML.id
ORDER BY AML.id;