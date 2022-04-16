SELECT AML.id, AML.name, AML.date, AM.date
FROM account_move AM
       JOIN account_move_line AML ON (AM.id = AML.move_id)
WHERE AML.date < date_trunc('month', AM.date) :: date;


UPDATE account_move_line
SET date = date_trunc('month', AM.date) :: date
FROM account_move AM
WHERE account_move_line.date < date_trunc('month', AM.date) :: date
  AND account_move_line.move_id = AM.id