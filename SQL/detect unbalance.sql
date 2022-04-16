SELECT line.move_id, sum(debit) - sum(credit)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            WHERE move.ref = 'VOORCALCULATIES 04-2020' group by(line.move_id);