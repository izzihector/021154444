
select aml.id, f.new_analytic_account, aaa.id, f.name, f.communication
                from fix f
                       JOIN account_move am on (am.name = f.name)
                       join account_move_line aml on (aml.move_id = am.id
                                                        and aml.name like (
                        regexp_replace(
                          split_part(f.communication, ' - ', 1), E'[\\n\\r]+', ' ', 'g'
                            ) || '%'
                        )
                        and TO_DATE(f.date, 'MM/DD/YYYY') = aml.date)
                       join account_account aa on (aml.account_id = aa.id and aa.code = f.account)
join account_analytic_account aaa on f.new_analytic_account = aaa.code;

update account_move_line
set analytic_account_id = aaa.id
from fix f
       JOIN account_move am on (am.name = f.name)
       join account_move_line aml on (aml.move_id = am.id
                                        and aml.name like (
        regexp_replace(
          split_part(f.communication, ' - ', 1), E'[\\n\\r]+', ' ', 'g'
            ) || '%'
        )
                                        and TO_DATE(f.date, 'MM/DD/YYYY') = aml.date)
       join account_account aa on (aml.account_id = aa.id and aa.code = f.account)
       join account_analytic_account aaa on f.new_analytic_account = aaa.code
where account_move_line.id  = aml.id

select aml.name from account_move_line aml join account_move am on am.id = aml.move_id where am.name = 'PBMMEM/2019/000561'

select id, name from account_move_line where name like '%SEDNEY%'



select aml.id, aml.date, aml.name, aml.ref,balance, a.code, aml.omschr, a3.code
from account_move am
       join account_move_line aml on am.id = aml.move_id
join account_analytic_account a on aml.analytic_account_id = a.id
join account_account a3 on aml.account_id = a3.id
where am.name = 'PBMLF/2019/003828' and a3.code = '409010'

CREATE TEMP TABLE aaa (id INT, code VARCHAR);

COPY aaa from '/tmp/aaa.csv';