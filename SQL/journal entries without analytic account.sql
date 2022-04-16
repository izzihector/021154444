SELECT aml.id,
      am.name,
       aml.name,
       aml.ref,
      aa.code,
      aml.date,
      balance  /
                 (
                    CASE
                        WHEN AML.company_currency_id = 2
                            THEN 1
                    ELSE RCR.rate
                         END
                 ) AS balance
from account_move_line aml
join account_account aa on aml.account_id = aa.id
join account_move am on aml.move_id = am.id
LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                   AND RCR.name = date_trunc('month', AML.date))
where analytic_account_id is NULL
 AND AA.code SIMILAR TO '(4|8|9)%'
                AND AA.code != '999999'
                AND AM.state = 'posted'
order by date;


drop table fix;

CREATE TEMPORARY TABLE fix(id integer, code varchar);

COPY fix(id, code) FROM '/tmp/a.csv' DELIMITER ';';

UPDATE account_move_line SET analytic_account_id = AAA.id
    FROM fix
        JOIN account_analytic_account AAA ON fix.code = aaa.code
        WHERE fix.id = account_move_line.id