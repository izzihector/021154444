SELECT SIF.id, SIF.grootb, kstnpl, pnr, omschr, bedrag, bedrusd FROM slm_import_file SIF
LEFT JOIN account_account AA ON (SIF.grootb = AA.code AND AA.company_id = 2)
WHERE SIF.name= 'MARGO 08-2020MARGO 08-2020'
AND AA.id ISNULL
ORDER BY  SIF.id;



SELECT DISTINCT SIF.grootb FROM slm_import_file SIF
LEFT JOIN account_account AA ON (SIF.grootb = AA.code AND AA.company_id = 2)
WHERE SIF.name= 'MARGO 08-2020'
AND AA.id ISNULL;


SELECT * FROM account_account where code = '225005'