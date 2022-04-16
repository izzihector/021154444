-- This query will fix  account move lines (journal entry lines) with a date not in the same month as the account move (journal entry)
UPDATE account_move_line set date = T.date
FROM (SELECT aml.id, am.date
    FROM account_move_line aml
    JOIN account_move am on aml.move_id = am.id
    WHERE date_trunc('month', AML.date) != date_trunc('month', AM.date)
    AND am.state = 'posted') AS T
WHERE T.id = account_move_line.id;