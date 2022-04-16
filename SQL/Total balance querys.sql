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
--   AND AA.code = '420007'
-- GROUP BY AA.code
-- ORDER BY AA.code :: INTEGER;
-- ORDER BY AML.id;



SELECT
--        AML.ID,
--        AA.code,
--        balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END) AS balance
       SUM(balance / (CASE WHEN AML.company_currency_id = 2 THEN 1 ELSE RCR.rate END)) AS balance
FROM account_move_line AML
       JOIN account_move AM ON (AM.id = AML.move_id)
       JOIN account_account AA ON (AML.account_id = AA.id)
       JOIN account_account_account_tag AAAT ON (AAAT.account_account_id = AA.id)
       LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                             AND RCR.name = date_trunc('month', AML.date) :: date)
WHERE AML.company_id IN (2, 3, 4, 5, 6, 7)
  AND AML.date <= '2019-12-31'
  AND AML.date >= '2019-04-01'
  AND AM.state = 'posted'
  AND AA.code SIMILAR TO '(4|8|9)%'
  AND AA.code != '999999'
  AND AAAT.account_account_tag_id = 157;
--   AND AA.code = '420007'
--     GROUP BY AA.code
--     ORDER BY AA.code :: INTEGER;
-- ORDER BY AML.id;

select * from account_account_tag where name like 'Vloot%'