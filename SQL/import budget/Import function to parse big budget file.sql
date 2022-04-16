~/bin/pgfutter_linux_amd64 --dbname slm --port 5432 --user odoo --pw odoo --table import_budget --schema public csv /home/fflores/Documentos/xetechs/surinam/imports/budget/budget.csv


DROP FUNCTION import;

CREATE OR REPLACE FUNCTION import (table_budget_name VARCHAR)
   RETURNS TABLE (
      month_from VARCHAR,
      year_from VARCHAR,
      code VARCHAR,
      analytic_code VARCHAR,
      balance NUMERIC,
      total_columns INTEGER
   )
AS $$
DECLARE
   budget RECORD;
   range record;
   counter INTEGER := 0 ;
   query_budget TEXT;
   month_number INTEGER;
   column_aa INTEGER;
   year_number INTEGER;
BEGIN
   total_columns := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = table_budget_name) - 1;
   FOR range IN (SELECT generate_series(1, total_columns) AS number)
   LOOP
      counter := counter + 1;
      IF (counter < 13) THEN
         IF (counter + 3 <= 12) THEN
            month_number := counter + 3;
            year_number := 2019;
         ELSE
            month_number := counter - 9;
            year_number := 2020;
         END IF;
         column_aa := range.number - counter + 13;
         query_budget := FORMAT('SELECT %s as balance, account, %s AS analytic_code FROM %s', '_' || range.number, '_' || column_aa, table_budget_name);
--          raise notice '%', query_budget;
         FOR budget IN EXECUTE query_budget
         LOOP
            month_from := LPAD(month_number::text, 2, '0');
            year_from := year_number;
            code := budget.account;
            analytic_code := budget.analytic_code;
            balance := budget.balance::NUMERIC;
            RETURN NEXT;
         END LOOP;
      ELSE
         counter := 0;
      END IF;
   END LOOP;
END ;
$$ LANGUAGE plpgsql;

select * from import('ma_budget');
