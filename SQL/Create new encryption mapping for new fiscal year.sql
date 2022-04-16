-- First create a new encryption mapping with the new fiscal year and replace the encryption_mapping_id with the new one
insert into encryption_mapping_line(encryption_mapping_id, analytical_account_id,cost_center,encryption,create_uid,create_date,write_uid,write_date)
 select 3, analytical_account_id, cost_center, encryption, 2, now(), 2, now()
    from encryption_mapping_line
    where encryption_mapping_id = 1;