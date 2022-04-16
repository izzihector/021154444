SELECT name, id, sum(balance) as balance, code
                FROM (

                       WITH accounts_expression AS (
                            SELECT DISTINCT expression, AA.id
                                     FROM slm_group_total_mapping SGTM
                                            JOIN slm_group_mapping_slm_group_total_mapping_rel SGMSGTMR
                                              ON (SGTM.id = SGMSGTMR.slm_group_total_mapping_id)
                                            JOIN slm_group_mapping SGM ON (SGM.id = SGMSGTMR.slm_group_mapping_id)
                                            JOIN slm_group_mapping_line SGML ON (SGML.slm_group_mapping_id = SGM.id)
                                            JOIN account_account AA ON (AA.code LIKE CONCAT(SGML.expression, '%'))
                                     WHERE SGM.id = 1
                                       AND SGML.expression IS NOT NULL
                      )

            SELECT SGM.name,
                 SGM.id,
                 balance * (EML.encryption / 100) /
                 (
                    CASE
                        WHEN AML.company_currency_id = 2
                            THEN 1
                    ELSE RCR.rate
                         END
                 ) AS balance,
                   AA.code

            FROM slm_group_total_mapping SGTM
                 JOIN slm_group_mapping_slm_group_total_mapping_rel SGMSGTMR ON (SGTM.id = SGMSGTMR.slm_group_total_mapping_id)
                 JOIN slm_group_mapping SGM ON (SGM.id = SGMSGTMR.slm_group_mapping_id)
                 JOIN slm_group_mapping_line SGML ON (SGM.id = SGML.slm_group_mapping_id)
                 JOIN slm_group_report_layout SGRL ON (SGRL.slm_group_total_mapping_id = SGTM.id AND SGML.group = SGRL.group)
                 JOIN slm_group_group SGG ON (SGML.group = SGG.id)

                    JOIN account_account AA_ID ON SGML.account_id = AA_ID.id
                    JOIN account_account AA ON (AA.code = AA_ID.code)

             JOIN account_move_line AML ON (AA.id = AML.account_id AND
                                            AML.company_id IN (2, 3, 4, 5, 6, 7) AND AML.date >= '2019-04-01' AND
                                            AML.date <= '2019-04-30')
             JOIN account_move AM ON (AM.id = AML.move_id)
             LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                   AND RCR.name = date_trunc('month', AML.date) :: date)
             JOIN encryption_mapping_line EML ON (EML.analytical_account_id = AML.analytic_account_id)
             JOIN account_analytic_account AAA_SGM ON (AAA_SGM.id = SGM.profit_center)
             JOIN account_analytic_account AAA_EM ON (
                                            AAA_EM.id = EML.cost_center
                                            AND AAA_EM.code =
                                            ('7' || Substring(AAA_SGM.code FROM 2 FOR CHAR_LENGTH(AAA_SGM.code) - 1)))
             JOIN encryption_mapping EM ON (EM.id = EML.encryption_mapping_id)
             JOIN account_fiscal_year AFY ON (AFY.id = EM.fiscal_year)

            WHERE SGTM.id = 1
                AND AA.code SIMILAR TO '(4|8|9)%'
                AND AA.code != '999999'
                AND AM.state = 'posted'
                AND AFY.date_from <= '2019-04-30'
                AND AFY.date_to >= '2019-04-30'
         UNION ALL
            SELECT SGM.name,
                 SGM.id,
                 balance * (EML.encryption / 100) /
                 (
                    CASE
                        WHEN AML.company_currency_id = 2
                            THEN 1
                    ELSE RCR.rate
                         END
                 ) AS balance,
                   AA.code

            FROM slm_group_total_mapping SGTM
                 JOIN slm_group_mapping_slm_group_total_mapping_rel SGMSGTMR ON (SGTM.id = SGMSGTMR.slm_group_total_mapping_id)
                 JOIN slm_group_mapping SGM ON (SGM.id = SGMSGTMR.slm_group_mapping_id)
                 JOIN slm_group_mapping_line SGML ON (SGM.id = SGML.slm_group_mapping_id)
                 JOIN slm_group_report_layout SGRL ON (SGRL.slm_group_total_mapping_id = SGTM.id AND SGML.group = SGRL.group)
                 JOIN slm_group_group SGG ON (SGML.group = SGG.id)

                    JOIN account_account_account_tag AAAT ON (AAAT.account_account_tag_id = SGML.tag_id)
                    JOIN account_account AA ON (AAAT.account_account_id = AA.id)

             JOIN account_move_line AML ON (AA.id = AML.account_id AND
                                            AML.company_id IN (2, 3, 4, 5, 6, 7) AND AML.date >= '2019-04-01' AND
                                            AML.date <= '2019-04-30')
             JOIN account_move AM ON (AM.id = AML.move_id)
             LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                   AND RCR.name = date_trunc('month', AML.date) :: date)
             JOIN encryption_mapping_line EML ON (EML.analytical_account_id = AML.analytic_account_id)
             JOIN account_analytic_account AAA_SGM ON (AAA_SGM.id = SGM.profit_center)
             JOIN account_analytic_account AAA_EM ON (
                                            AAA_EM.id = EML.cost_center
                                            AND AAA_EM.code =
                                            ('7' || Substring(AAA_SGM.code FROM 2 FOR CHAR_LENGTH(AAA_SGM.code) - 1)))
             JOIN encryption_mapping EM ON (EM.id = EML.encryption_mapping_id)
             JOIN account_fiscal_year AFY ON (AFY.id = EM.fiscal_year)

            WHERE SGTM.id = 1
                AND AA.code SIMILAR TO '(4|8|9)%'
                AND AA.code != '999999'
                AND AM.state = 'posted'
                AND AFY.date_from <= '2019-04-30'
                AND AFY.date_to >= '2019-04-30'
         UNION ALL
            SELECT SGM.name,
                 SGM.id,
                 balance * (EML.encryption / 100) /
                 (
                    CASE
                        WHEN AML.company_currency_id = 2
                            THEN 1
                    ELSE RCR.rate
                         END
                 ) AS balance,
                   AA.code

            FROM slm_group_total_mapping SGTM
                 JOIN slm_group_mapping_slm_group_total_mapping_rel SGMSGTMR ON (SGTM.id = SGMSGTMR.slm_group_total_mapping_id)
                 JOIN slm_group_mapping SGM ON (SGM.id = SGMSGTMR.slm_group_mapping_id)
                 JOIN slm_group_mapping_line SGML ON (SGM.id = SGML.slm_group_mapping_id)
                 JOIN slm_group_report_layout SGRL ON (SGRL.slm_group_total_mapping_id = SGTM.id AND SGML.group = SGRL.group)
                 JOIN slm_group_group SGG ON (SGML.group = SGG.id)

                    JOIN account_account AA ON (AA.group_id = SGML.group_id)

             JOIN account_move_line AML ON (AA.id = AML.account_id AND
                                            AML.company_id IN (2, 3, 4, 5, 6, 7) AND AML.date >= '2019-04-01' AND
                                            AML.date <= '2019-04-30')
             JOIN account_move AM ON (AM.id = AML.move_id)
             LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                   AND RCR.name = date_trunc('month', AML.date) :: date)
             JOIN encryption_mapping_line EML ON (EML.analytical_account_id = AML.analytic_account_id)
             JOIN account_analytic_account AAA_SGM ON (AAA_SGM.id = SGM.profit_center)
             JOIN account_analytic_account AAA_EM ON (
                                            AAA_EM.id = EML.cost_center
                                            AND AAA_EM.code =
                                            ('7' || Substring(AAA_SGM.code FROM 2 FOR CHAR_LENGTH(AAA_SGM.code) - 1)))
             JOIN encryption_mapping EM ON (EM.id = EML.encryption_mapping_id)
             JOIN account_fiscal_year AFY ON (AFY.id = EM.fiscal_year)

            WHERE SGTM.id = 1
                AND AA.code SIMILAR TO '(4|8|9)%'
                AND AA.code != '999999'
                AND AM.state = 'posted'
                AND AFY.date_from <= '2019-04-30'
                AND AFY.date_to >= '2019-04-30'
         UNION ALL
            SELECT SGM.name,
                 SGM.id,
                 balance * (EML.encryption / 100) /
                 (
                    CASE
                        WHEN AML.company_currency_id = 2
                            THEN 1
                    ELSE RCR.rate
                         END
                 ) AS balance,
                   AA.code

            FROM slm_group_total_mapping SGTM
                 JOIN slm_group_mapping_slm_group_total_mapping_rel SGMSGTMR ON (SGTM.id = SGMSGTMR.slm_group_total_mapping_id)
                 JOIN slm_group_mapping SGM ON (SGM.id = SGMSGTMR.slm_group_mapping_id)
                 JOIN slm_group_mapping_line SGML ON (SGM.id = SGML.slm_group_mapping_id)
                 JOIN slm_group_report_layout SGRL ON (SGRL.slm_group_total_mapping_id = SGTM.id AND SGML.group = SGRL.group)
                 JOIN slm_group_group SGG ON (SGML.group = SGG.id)

                    JOIN accounts_expression ON (accounts_expression.expression = SGML.expression)
                    JOIN account_account AA ON (accounts_expression.id = AA.id)

             JOIN account_move_line AML ON (AA.id = AML.account_id AND
                                            AML.company_id IN (2, 3, 4, 5, 6, 7) AND AML.date >= '2019-04-01' AND
                                            AML.date <= '2019-04-30')
             JOIN account_move AM ON (AM.id = AML.move_id)
             LEFT JOIN res_currency_rate RCR ON (AML.company_currency_id = RCR.currency_id
                                                   AND RCR.name = date_trunc('month', AML.date) :: date)
             JOIN encryption_mapping_line EML ON (EML.analytical_account_id = AML.analytic_account_id)
             JOIN account_analytic_account AAA_SGM ON (AAA_SGM.id = SGM.profit_center)
             JOIN account_analytic_account AAA_EM ON (
                                            AAA_EM.id = EML.cost_center
                                            AND AAA_EM.code =
                                            ('7' || Substring(AAA_SGM.code FROM 2 FOR CHAR_LENGTH(AAA_SGM.code) - 1)))
             JOIN encryption_mapping EM ON (EM.id = EML.encryption_mapping_id)
             JOIN account_fiscal_year AFY ON (AFY.id = EM.fiscal_year)

            WHERE SGTM.id = 1
                AND AA.code SIMILAR TO '(4|8|9)%'
                AND AA.code != '999999'
                AND AM.state = 'posted'
                AND AFY.date_from <= '2019-04-30'
                AND AFY.date_to >= '2019-04-30'

            ) AS A
            WHERE id = 5
            GROUP BY name, id, code
            ORDER BY code::INTEGER
