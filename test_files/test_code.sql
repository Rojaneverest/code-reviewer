
    select
      bill_payment_id,
      source_bill_payment_id,
      billing_entity_id,
      source_billing_entity_id,
      member_id,
      subscriber_id,
      sub_group_id,
      billing_due_date,
      billing_contract_id,
      receipt_create_datetime,
      receipt_id,
      receipt_amount,
      receipt_batch_id,
      receipt_received_date,
      c1.DDVV_DESCRIPTION as payment_in_out_code,
      billing_group_id,
      employer_group_id,
      c2.DDVV_DESCRIPTION as suspense_code,
      holding_account_type,
      payment_applicable_billing_due_date,
      allocated_receipt_id,
      c3.DDVV_DESCRIPTION as bill_payment_status,
      c4.DDVV_DESCRIPTION as billing_contract_payment_status,
      c5.DDVV_DESCRIPTION as manual_allocation_code,
      billing_process_id,
      alternate_funding_agreement_id,
      suppress_reports_code,
      c6.DDVV_DESCRIPTION as receipt_payment_type,
      holding_account,
      bank_id,
      payment_reference_number,
      associated_receipt_id,
      receipt_source,
      receipt_reason,
      receipt_payment_method,
      receipt_reversal_ind,
      receipt_payment_date_time,
      receipt_Input_billing_period,
      receipt_input_invoice_id,
      receipt_process_order,
      related_entity_sequence_number,
      financial_activity_payment_details,
      general_ledger_posting_details,
      alternate_funding_parameter_details,
      alternate_funding_payment_details,
      billing_payment_recovery_details,
      reference_ids,
      variable_fields,
      source_extension_record_id,
      original_source_value,
      abacus_entity_type,
      abacus_ingestion_id,
      abacus_record_id,
      abacus_consume_timestamp,
      abacus_logical_delete_ind,
      abacus_record_hash_id,
      abacus_scd_key,
      abacus_record_eff_ts,
      abacus_record_exp_ts,
      abacus_record_create_ts,
      abacus_record_modify_ts,
      abacus_record_is_active,
      abacus_record_changed_columns,
      abacus_ending_scd_event,
      source_name,
      source_id,
      source_authoritative_ind,
      source_timestamp,
      source_file_name,
      identifiers,
      additional_source_identifiers,
      extension_source_values,
      data_quality_result,
      abacus_archival_type
    from
      silver.facets_bill_payment b1
        LEFT JOIN BRONZE.cer_ddvv_valid_values c1
          ON UPPER(c1.DDTA_TABLE_NAME) = 'CMC_BLRC_BILL_RCPT'
          AND UPPER(c1.DDCO_COLUMN_NAME) = UPPER('BLRC_IN_OUT_IND')
          AND trim(UPPER(b1.payment_in_out_code)) = trim(UPPER(c1.DDVV_VALID_VALUE))
          AND upper(c1.DDTA_DATABASE_CD) = 'FA'
          AND c1.RELU_RELEASE_NUMBER = '2.21'
 
        LEFT JOIN BRONZE.cer_ddvv_valid_values c2
          ON UPPER(c2.DDTA_TABLE_NAME) = 'CMC_BLRC_BILL_RCPT'
          AND UPPER(c2.DDCO_COLUMN_NAME) = UPPER('BLRC_SUSPENSE_IND')
          AND trim(UPPER(b1.suspense_code)) = trim(UPPER(c2.DDVV_VALID_VALUE))
          AND upper(c2.DDTA_DATABASE_CD) = 'FA'
          AND c2.RELU_RELEASE_NUMBER = '2.21'
      
        LEFT JOIN BRONZE.cer_ddvv_valid_values c3
          ON UPPER(c3.DDTA_TABLE_NAME) = 'CMC_BLRC_BILL_RCPT'
          AND UPPER(c3.DDCO_COLUMN_NAME) = UPPER('BLRC_BLBL_PAID_STS')
          AND trim(UPPER(b1.bill_payment_status)) = trim(UPPER(c3.DDVV_VALID_VALUE))
          AND upper(c3.DDTA_DATABASE_CD) = 'FA'
          AND c3.RELU_RELEASE_NUMBER = '2.21'
 
        LEFT JOIN BRONZE.cer_ddvv_valid_values c4
          ON UPPER(c4.DDTA_TABLE_NAME) = 'CMC_BLRC_BILL_RCPT'
          AND UPPER(c4.DDCO_COLUMN_NAME) = UPPER('BLRC_BLCS_PAID_STS')
          AND trim(UPPER(b1.billing_contract_payment_status)) = trim(UPPER(c4.DDVV_VALID_VALUE))
          AND upper(c4.DDTA_DATABASE_CD) = 'FA'
          AND c4.RELU_RELEASE_NUMBER = '2.21'
 
        LEFT JOIN BRONZE.cer_ddvv_valid_values c5
          ON UPPER(c5.DDTA_TABLE_NAME) = 'CMC_BLRC_BILL_RCPT'
          AND UPPER(c5.DDCO_COLUMN_NAME) = UPPER('BLRC_MAN_ALLOC_IND')
          AND trim(UPPER(b1.manual_allocation_code)) = trim(UPPER(c5.DDVV_VALID_VALUE))
          AND upper(c5.DDTA_DATABASE_CD) = 'FA'
          AND c5.RELU_RELEASE_NUMBER = '2.21'
 
        LEFT JOIN BRONZE.cer_ddvv_valid_values c6
          ON UPPER(c6.DDTA_TABLE_NAME) = 'CMC_RCPT_RECEIPTS'
          AND UPPER(c6.DDCO_COLUMN_NAME) = UPPER('RCPT_RCPT_CD')
          AND trim(UPPER(b1.receipt_payment_type)) = trim(UPPER(c6.DDVV_VALID_VALUE))
          AND upper(c6.DDTA_DATABASE_CD) = 'FA'
          AND c6.RELU_RELEASE_NUMBER = '2.21'

