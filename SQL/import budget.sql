create table import (
  code          varchar,
  analytic_code varchar,
  date          date,
  balance       float
);
copy import from '/tmp/import.csv' delimiter ';' CSV;

SELECT CONCAT(AA.code, ' ', AA.name), 2, 2, now(), 2, now()
FROM import I
       JOIN account_account AA ON (I.code = AA.code AND AA.company_id = 2);


INSERT INTO account_budget_post (name, company_id, create_uid, create_date, write_uid, write_date)
SELECT DISTINCT CONCAT(AA.code, ' ', AA.name), 2, 2, now(), 2, now()
FROM import I
       JOIN account_account AA ON (I.code = AA.code AND AA.company_id = 2 AND I.date = '2019-04-01')
      LEFT JOIN account_budget_post ABP ON (CONCAT(AA.code, ' ', AA.name) = ABP.name)
WHERE ABP.id ISNULL ;

delete
from account_budget_post;

SELECT *
FROM account_budget_post;

select code
from import
group by code;

select *
from crossovered_budget;

select *
from crossovered_budget_lines
where crossovered_budget_id = 6;
delete
from crossovered_budget_lines;


INSERT INTO account_budget_rel (budget_id, account_id)
SELECT ABP.id, AA.id
FROM account_budget_post ABP
       JOIN account_account AA ON (ABP.name = CONCAT(AA.code, ' ', AA.name)
                                     AND AA.company_id = 2)
--       JOIN account_budget_rel ABR ON (AA.id = ABR.account_id)

ORDER BY ABP.id;

select * from account_budget_rel;
        print(sql % params)

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
SELECT 8,
       AAA.id,
       ABP.id,
       I.date,
       (date_trunc('month', I.date :: date) + interval '1 month' - interval '1 day') :: date,
       balance,
       2,
       'draft',
       2,
       now(),
       2,
       now()
FROM import I
       JOIN account_analytic_account AAA ON (AAA.code = I.analytic_code)
       JOIN account_account AA ON (AA.code = I.code AND AA.company_id = 2)
       JOIN account_budget_post ABP ON (ABP.name = CONCAT(AA.code, ' ', AA.name));



