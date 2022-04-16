SELECT SIF.id, grootb, curcd, bedrag, bedrsrd, bedrusd, omschr,vlnr, kstnpl, AAM.id,
      string_agg(AAA_MANDATORY.code, ',') as "Mandatory analytic accounts"
FROM slm_import_file SIF
JOIN account_account AA ON (AA.code = SIF.grootb)
JOIN account_analytic_account AAA ON (AAA.code = SIF.kstnpl)
JOIN account_analytic_mandatory AAM ON (AA.id = AAM.account_id)
JOIN account_analytic_account_account_analytic_mandatory_rel AAAAAMR ON (AAM.id = AAAAAMR.account_analytic_mandatory_id)
JOIN account_analytic_account AAA_MANDATORY ON (AAA_MANDATORY.id = AAAAAMR.account_analytic_account_id)
WHERE SIF.name = 'PASSAGE 08-2020'
AND AAA.id NOT IN (SELECT account_analytic_account_id FROM account_analytic_account_account_analytic_mandatory_rel WHERE account_analytic_mandatory_id = AAM.id)
GROUP BY grootb, vlnr, kstnpl, AAM.id, SIF.id;






SELECT DISTINCT SIF.id, grootb, curcd, bedrag, bedrsrd, bedrusd, omschr,vlnr, kstnpl, AAM.id
FROM slm_import_file SIF
JOIN account_account AA ON (AA.code = SIF.grootb)
JOIN account_analytic_account AAA ON (AAA.code = SIF.kstnpl)
JOIN account_analytic_mandatory AAM ON (AA.id = AAM.account_id)
JOIN account_analytic_account_account_analytic_mandatory_vlnr_rel AAAAAMVR ON (AAM.id = AAAAAMVR.account_analytic_mandatory_id)
WHERE SIF.name = 'PASSAGE 08-2020'
AND SIF.vlnr ISNULL ;


select count( *) from slm_import_file where name = 'EDGAR 09-2019'

select count(*) from account_move_line where name = 'EDGAR 09-2019'


SELECT DISTINCT AML.id, AA.code, curcd, bedrag,omschr, vlnr, AAA.code
FROM account_move_line AML
JOIN account_account AA  ON  (AML.account_id = AA.id)
JOIN account_analytic_account AAA ON (AML.analytic_account_id = AAA.id)
JOIN account_analytic_mandatory AAM ON (AA.id = AAM.account_id)
-- JOIN account_analytic_account_account_analytic_mandatory_vlnr_rel AAAAAMVR ON (AAM.id = AAAAAMVR.account_analytic_mandatory_id)
WHERE AML.name = 'EDGAR 09-2019'
-- AND AML.vlnr ISNULL ;


