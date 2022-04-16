INSERT INTO account_budget_post (name, company_id, create_uid, create_date, write_uid, write_date)
SELECT DISTINCT CONCAT(AA.code, ' ', AA.name), 2, 2, now(), 2, now()
FROM costs_budget I
       JOIN account_account AA ON (I.account = AA.code AND AA.company_id = 2)
       LEFT JOIN account_budget_post ABP ON (CONCAT(AA.code, ' ', AA.name) = ABP.name)
WHERE ABP.id ISNULL;


INSERT INTO account_budget_rel (budget_id, account_id)
SELECT ABP.id, AA.id
FROM account_budget_post ABP
       JOIN account_account AA ON (ABP.name = CONCAT(AA.code, ' ', AA.name)
                                     AND AA.company_id = 2)
       LEFT JOIN account_budget_rel ABR on (AA.id = ABR.account_id)
WHERE ABR.account_id ISNULL;


INSERT INTO crossovered_budget_lines (crossovered_budget_id,
                                      analytic_account_id,
                                      general_budget_id,
                                      date_from,
                                      date_to,
                                      planned_amount,
                                      company_id,
                                      crossovered_budget_state,
                                      create_uid,
                                      create_date,
                                      write_uid,
                                      write_date)
SELECT 23,
       AAA.id,
       ABP.id,
       CONCAT(year_from, month_from, '01') :: DATE AS date_from,
       (date_trunc('month', CONCAT(year_from, month_from, '01') :: DATE :: date) + interval '1 month' -
        interval '1 day') :: DATE,
       balance,
       2,
       'draft',
       2,
       now(),
       2,
       now()
FROM import('cargo_budget') AS I
       JOIN account_analytic_account AAA ON (AAA.code = I.analytic_code)
       JOIN account_account AA ON (AA.code = I.code AND AA.company_id = 2)
       JOIN account_budget_post ABP ON (ABP.name = CONCAT(AA.code, ' ', AA.name));


SELECT * FROM crossovered_budget_lines where crossovered_budget_id=9;
DELETE FROM crossovered_budget_lines where crossovered_budget_id=9;

SELECT account FROM import_budget IB LEFT JOIN account_account AA ON AA.code = IB.account
WHERE AA.code
400042
400043
400044
400045
400046
460000


select code from account_account where code = '460000';

select * from account_budget_post where name like '400042';