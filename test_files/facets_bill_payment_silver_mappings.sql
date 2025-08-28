create or replace global temp view v_BP_general_ledger as
select
  BLAC.BLEI_CK,
  BLAC.BLBL_DUE_DT,
  BLAC.BLCN_ID,
  BLAC.BLRC_SEQ_NO,
  BLAC.RCPT_ID,
  collect_list(
    struct(
      md5(
        concat(
          char(31),
          nvl(cast(BLAC.BLEI_CK as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(BLAC.BLBL_DUE_DT as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(BLAC.BLCN_ID as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(
            cast(BLAC.BLAC_CREATE_DTM as varchar(20)),
            char(0)
          )
        )
      ) as reference_id,
      cast(BLAC.BLAC_INVOICE_DTM as timestamp) as invoice_date_time,
      cast(BLAC.BLAC_POSTING_DT as timestamp) as posting_date,
      cast(BLAC.COCE_ID as string) as commission_entity_id,
      cast(BLAC.BLAC_YR1_IND as string) as first_year_code,
      cast(BLAC.BLAC_SOURCE as string) as activity_source,
      cast(BLAC.ACAD_GEN_LDGR_NO as string) as general_ledger_number,
      cast(BLAC.BLAC_DEBIT_AMT as decimal(20, 4)) as debit_amount,
      cast(BLAC.BLAC_CREDIT_AMT as decimal(20, 4)) as credit_amount,
      BLAC.ACGL_TYPE as general_ledger_account_type,
      BLAC.ACGL_ACTIVITY as general_ledger_account_activity,
      BLAC.BLAC_VAR_DATA_1 as gl_variable_data_1,
      BLAC.BLAC_VAR_DATA_2 as gl_variable_data_2,
      BLAC.BLAC_VAR_DATA_3 as gl_variable_data_3,
      BLAC.BLAC_JE_NO as journal_entry_number,
      BLAC.BLAC_OPTS as general_ledger_options,
      BLAC.RCPT_MCTR_HOLD as general_ledger_holding_account
    )
  ) as general_ledger_posting_details
from
  bronze.cmc_blac_bill_acct BLAC
  JOIN bronze.CMC_RCPT_RECEIPTS RCPT ON RCPT.RCPT_ID = BLAC.RCPT_ID
where
  TRIM(blac.RCPT_ID) <> ''
  AND blac.blac_type = 'R'
group by
  BLAC.BLEI_CK,
  BLAC.BLBL_DUE_DT,
  BLAC.BLCN_ID,
  BLAC.BLRC_SEQ_NO,
  BLAC.RCPT_ID;

CREATE OR REPLACE  global temp view V_BP_BLRH_RED_ARRAY
 AS
 SELECT BLRH.BLEI_CK,
 BLRH.BLRH_FNDG_FROM_DT,
 BLRH.BLRH_FNDG_THRU_DT,
  collect_list(STRUCT(
 md5(
    concat(
        char(31), nvl(cast(BLRH.MEME_CK as varchar(20)),char(0)), char(31), '_',
        char(31), nvl(cast(BLRH.BLEI_CK as varchar(20)),char(0)), char(31), '_',
        char(31), nvl(cast(BLRH.AFCP_PER_NO as varchar(20)),char(0)),char(31), '_',
        char(31), nvl(cast(BLRH.BLRH_FNDG_FROM_DT as varchar(20)),char(0)),char(31), '_',
        char(31), nvl(cast(BLRH.BLRH_SEQ_NO as varchar(20)),char(0))
        )
    ) as reference_id,
 cast(BLRH.BLRH_FNDG_FROM_DT as timestamp) as funding_eff_date,
 cast(BLRH.BLRH_FNDG_THRU_DT as timestamp) as funding_exp_date,
 BLRH.LOBD_ID as line_of_business_id,
 cast(BLRH.CSPI_ID as string) as plan_id,
 BLRH.PDPD_ID  as product_id,
 BLRH.ACRH_EVENT_TYPE  as recovery_event_type,
 BLRH.ACPR_REF_ID  as recovery_reference_id,
 BLRH.ACRH_SEQ_NO  as recovery_sequence_number,
 cast(BLRH.ACRH_CREATE_DT as timestamp) as recovery_record_create_date,
 cast(BLRH.ACRH_AMT as decimal(20,4))  as recovery_amount,
 BLRH.BLRH_ORIG_CLCL_ID  as original_claim_id,
  cast( BLRH.BLRH_SSL_AMT  as decimal(20,4)) as stop_loss_amount,
 cast( BLRH.BLRH_SSL_EXC_AMT  as decimal(20,4))  as excess_of_stop_loss_amount,
 cast(BLRH.BLRH_ASO_AMT  as decimal(20,4))  as aso_amount,
  cast(BLRH.BLRH_HSA_AMT as decimal(20,4))  as hra_amount
 )) as billing_payment_recovery_details
 FROM
 bronze.CMC_BLRH_RED_HIST BLRH
 GROUP BY BLRH.BLEI_CK,BLRH.BLRH_FNDG_FROM_DT,
 BLRH.BLRH_FNDG_THRU_DT;

create or replace global temp view V_BP_CDS_FNAC_FNCL_ACT as
select
  FNAC.BLEI_CK,
  FNAC.BLBL_DUE_DT,
  collect_list(
    STRUCT(
      md5(
        concat(
          char(31),
          nvl(cast(FNAC.BLEI_CK as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(
            cast(
              date_format(trim(FNAC.FNAC_ACTIVITY_DT), 'yyyy_MM_dd_HH_mm_ss_SSS') as varchar(20)
            ),
            char(0)
          ),
          char(31),
          '_',
          char(31),
          nvl(cast(FNAC.FNAC_TYPE_IND as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(FNAC.FNAC_SEQ_NO as varchar(20)), char(0))
        )
      ) as reference_id,
      FNAC.CSPI_ID as plan_id,
      FNAC.PLDS_DESC as plan_description,
      FNAC.PDPD_ID as product_id,
      FNAC.PDDS_DESC as product_description,
      FNAC.FNAC_ACTIVITY_DT as activity_date,
      FNAC.FNAC_TYPE_IND as activity_type,
      FNAC.FNAC_PREM_TYPE as premium_type,
      cast(FNAC.FNAC_PRIM_LOBD_IND as boolean) as primary_line_of_business_ind,
      FNAC.MCRE_CRCR_ID as related_entity_carrier_id,
      FNAC.MCRE_NAME as related_entity_carrier_name,
      FNAC.FNAC_ACCT_CAT as accounting_category,
      FNAC.PDDS_MCTR_BCAT as business_category,
      FNAC.BLCT_EXP_CAT as experience_category,
      FNAC.BLBL_DUE_DT as bill_due_date,
      FNAC.BLBL_END_DT as bill_end_date,
      cast(FNAC.BLBL_DAYS_BILLED as smallint) as billed_days_count,
      FNAC.PDBL_ID as billing_component_id,
      cast(FNAC.BLCT_VOL as decimal(20, 4)) as volume,
      FNAC.FNAC_MOD_LVS_SB as modal_subscriber_lives,
      FNAC.FNAC_MOD_LVS_DEP as modal_dependent_lives,
      FNAC.FNAC_RET_LVS_SB as retroactive_subscriber_lives,
      FNAC.FNAC_RET_LVS_DEP as retroactive_dependent_lives,
      CAST(FNAC.FNAC_TOT_PREM AS DECIMAL(20, 4)) AS total_billed_premium,
      CAST(FNAC.FNAC_TOT_YR1_PREM AS DECIMAL(20, 4)) AS total_first_year_premium,
      CAST(FNAC.FNAC_TOT_RNWL_PREM AS DECIMAL(20, 4)) AS total_renewal_premium,
      CAST(FNAC.FNAC_MOD_PREM AS DECIMAL(20, 4)) AS modal_premium,
      CAST(FNAC.FNAC_MOD_YR1_PREM AS DECIMAL(20, 4)) AS modal_first_year_premium,
      CAST(FNAC.FNAC_MOD_RNWL_PREM AS DECIMAL(20, 4)) AS modal_renewal_premium,
      CAST(FNAC.FNAC_MOD_PREM_SB AS DECIMAL(20, 4)) AS modal_subscriber_premium,
      CAST(FNAC.FNAC_MOD_PREM_DEP AS DECIMAL(20, 4)) AS modal_dependent_premium,
      CAST(FNAC.FNAC_RET_PREM AS DECIMAL(20, 4)) AS retroactive_premium,
      CAST(FNAC.FNAC_RET_YR1_PREM AS DECIMAL(20, 4)) AS retroactive_first_year_premium,
      CAST(FNAC.FNAC_RET_RNWL_PREM AS DECIMAL(20, 4)) AS retroactive_renewal_premium,
      CAST(FNAC.FNAC_RET_PREM_SB AS DECIMAL(20, 4)) AS retroactive_subscriber_premium,
      CAST(FNAC.FNAC_RET_PREM_DEP AS DECIMAL(20, 4)) AS retroactive_dependent_premium,
      CAST(FNAC.FNAC_TOT_PAID_REV AS DECIMAL(20, 4)) AS total_paid_revenue,
      CAST(FNAC.FNAC_TOT_PAID_CSH AS DECIMAL(20, 4)) AS total_paid_amount,
      CAST(FNAC.FNAC_YR1_PAID_CSH AS DECIMAL(20, 4)) AS first_year_paid_amount,
      CAST(FNAC.FNAC_RNWL_PAID_CSH AS DECIMAL(20, 4)) AS renewal_paid_amount,
      FNAC.PMFA_ID as fee_discount_id,
      FNAC.BLFD_FEE_DISC_IND as fee_discount_code,
      cast(FNAC.BLFD_FEE_AMT as decimal(20, 4)) as fee_amount,
      cast(FNAC.BLFD_DISC_AMT as decimal(20, 4)) as discount_amount,
      cast(FNAC.FNAC_TOT_PAID_FEE as decimal(20, 4)) as total_fee_paid
    )
  ) as financial_activity_payment_details
from
  bronze.CDS_FNAC_FNCL_ACT FNAC
where
  FNAC.FNAC_TYPE_IND = 'R'
GROUP BY
  FNAC.BLEI_CK,
  FNAC.BLBL_DUE_DT;

create
or replace global temp view V_BP_CMC_BLPT_PLAN_TOTL as --alternate fnd
with cte as (SELECT
  BLPT.BLEI_CK,
  BLPT.BLBL_DUE_DT,
  collect_list(
    STRUCT(
      md5(
        concat(
          char(31),
          nvl(cast(BLPT.BLEI_CK as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(
            cast(
              date_format(trim(BLPT.BLBL_DUE_DT), 'yyyy_MM_dd_HH_mm_ss_SSS') as varchar(20)
            ),
            char(0)
          ),
          char(31),
          '_',
          char(31),
          nvl(cast(BLPT.AFCP_PER_NO as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(BLPT.GRGR_CK as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(BLPT.SGSG_CK as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(BLPT.CSPI_ID as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(BLPT.PDPD_ID as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(BLPT.BLPT_SOURCE as varchar(20)), char(0)),
          char(31),
          '_',
          char(31),
          nvl(cast(BLPT.BLPT_SEQ_NO as varchar(20)), char(0))
        )
      ) as reference_id,
      BLPT.BLPT_SOURCE as payment_source,
      BLPT.BLPT_INVOICE_DTM as invoice_datetime,
      CAST(BLPT.BLPT_BILLED_AMT  AS DECIMAL(20, 4)) as billed_amount,
      CAST(INID.INID_OUTSTAND_BAL  AS DECIMAL(20, 4)) as outstanding_balance,
      CAST(INID.BLEI_NET_DUE  AS DECIMAL(20, 4))  as net_due_amount,
      INID.BLEI_BILL_LEVEL as bill_level,
      INID.BLBL_TYPE as bill_type,
      INID.BLBL_SPCL_BL_IND as special_bill_code,
      INID.INID_PYMT_TYPE as payment_type,
      INID.MEME_HICN as hcfa_claim_number,
      cast(BLPT.BLPT_RUN_OUT_IND as boolean) as run_out_ind,
      BLPT.CSPI_ID as plan_id,
      BLPT.PDPD_ID as product_id,
      BLPT.LOBD_ID as line_of_business_id,
      BLPT.BLCN_ID as contract_id,
      CAST(BLPT.BLPT_RED_SSL_AMT AS DECIMAL(20, 4)) AS reduction_ssl_total_amount,
      CAST(BLPT.BLPT_RED_SSL_EXC AS DECIMAL(20, 4)) AS reduction_ssl_excess_total_amount,
      CAST(BLPT.BLPT_RED_ASO_AMT AS DECIMAL(20, 4)) AS reduction_aso_total_amount,
      CAST(BLPT.BLPT_SSL_AMT AS DECIMAL(20, 4)) AS ssl_amount,
      CAST(BLPT.BLPT_SSL_EXC_AMT AS DECIMAL(20, 4)) AS ssl_excess_amount,
      CAST(BLPT.BLPT_EXTRACONT_AMT AS DECIMAL(20, 4)) AS extra_contractual_amount,
      CAST(BLPT.BLPT_ASO_AMT AS DECIMAL(20, 4)) AS amount_not_to_stop_loss,
     cast(BLPT.BLPT_COMM_INCL_IND as boolean) as commission_include_ind,
      cast(BLPT.BLPT_PYMT_CNT as int) as payment_count,
      CAST(BLPT.BLPT_RED_HSA_AMT  AS DECIMAL(20, 4)) as reduction_hra_payment_amount,
      CAST(BLPT.BLPT_HSA_AMT  AS DECIMAL(20, 4)) as hra_payment_amount,
      cast(BLPT.AFCP_PER_NO as int) as alternate_funding_agreement_period_number
    )
  ) as alternate_funding_payment_details
FROM
  BRONZE.CMC_BLPT_PLAN_TOTL BLPT
  JOIN BRONZE.CMC_BLBL_BILL_SUMM BLBL ON BLBL.BLEI_CK = BLPT.BLEI_CK
  AND BLBL.BLBL_DUE_DT = BLPT.BLBL_DUE_DT
  JOIN BRONZE.CDS_INID_INVOICE INID ON INID.BLEI_CK = BLBL.BLEI_CK
  AND INID.BLBL_DUE_DT = BLBL.BLBL_DUE_DT
GROUP BY
  BLPT.BLEI_CK,
  BLPT.BLBL_DUE_DT)
  select distinct * from cte;

CREATE OR REPLACE  global temp view V_BP_CMC_BLAF_ALT_FND_ARRAY
as
select BLAF.BLEI_CK,
collect_list(
    struct(
    md5(
    concat(
        char(31), nvl(cast(BLAF.BLEI_CK as varchar(20)),char(0))
        )
    ) as reference_id,
    cast(BLAF.BLEI_CK as string) as source_billing_entity_id,
    BLAF.BLAF_MODE as funding_period_frequency,
    BLAF.BLAF_SYNC_DAY as week_start_day,
    cast(BLAF.BLAF_GEN_VAL as int) as create_file_day,
    BLAF.BLAF_MCTR_FTYP as funding_type,
    BLAF.BLAF_MCTR_PMTH  as alternate_funding_payment_method,
    cast(BLAF.BLAF_RUN_OUT_MNTHS  as int) run_out_months,
    BLAF.BLAF_FND_STOP_DT as alternate_funding_stop_date,
    BLAF.BLAF_LST_FND_FR_DT as last_fund_claim_from_date,
    BLAF.BLAF_LST_FND_TH_DT as last_fund_claim_through_date,
    BLAF.BLAF_LST_FND_CR_DT as last_fund_capitation_date,
    BLAF.BLAF_LST_FND_DTM as last_funding_period_date_time,
    BLAF.BLAF_FND_BAT_STS as funding_batch_status,
    BLAF.BLAF_CLM_STS as alternate_funding_claim_status,
    cast(BLAF.BLAF_MNTH_LIAB_IND as boolean) as monthly_liability_ind,
    BLAF.BLAF_CLM_FEE_INCL as include_claim_fees,
    cast(BLAF.BLAF_OVRPY_ADJ_IND as boolean) as include_pending_claim_overpayments,
    cast(BLAF.BLAF_START_DAY as int) as start_day,
    cast(BLAF.BLAF_INT_INCL_IND as boolean) as include_claim_interest_ind
    )
)as alternate_funding_parameter_details
from bronze.CMC_BLAF_ALT_FND BLAF
  GROUP BY BLAF.BLEI_CK;

create
or replace global temp view V_BP_Ranked_Invoice as
select
  *
from
  (
    select
      *,
      ROW_NUMBER() OVER (PARTITION BY BLEI_CK,BLBL_DUE_DT ORDER BY BLEI_CK, BLBL_DUE_DT, BLIV_CREATE_DTM DESC, BLIV_ID DESC
      ) AS RN
    from
      BRONZE.cds_inid_invoice inv
    where BLBL_SPCL_BL_IND = 'N'
  )
where
  RN = 1;

select
  cast(
    BLRC.RCPT_ID || '_' || BLRC.BLEI_CK || '_' || BLRC.BLRC_SEQ_NO as string
  ) as bill_payment_id,
  cast(BLRC.RCPT_ID as string) as source_bill_payment_id,
  BLRC.BLEI_CK as billing_entity_id,
  BLRC.BLEI_CK as source_billing_entity_id,
  cast(null as string) as member_id,
  RCPT.RCPT_INPUT_SBSB_ID as subscriber_id,
  RCPT.RCPT_INPUT_SGSG_ID as sub_group_id,
  BLRC.BLBL_DUE_DT as billing_due_date,
  BLRC.BLCN_ID as billing_contract_id,
  RCPT.RCPT_CREATE_DTM as receipt_create_datetime,
  RCPT.RCPT_ID as receipt_id,
  RCPT.RCPT_AMT as receipt_amount,
  RCPT.RCPT_BATCH_ID as receipt_batch_id,
  RCPT.RCPT_RCVD_DT as receipt_received_date,
  BLRC.BLRC_IN_OUT_IND as payment_in_out_code,
  RCPT.RCPT_INPUT_BGBG_ID billing_group_id,
  RCPT.RCPT_INPUT_GRGR_ID as employer_group_id,
  BLRC.BLRC_SUSPENSE_IND as suspense_code,
  BLRC.RCPT_MCTR_HOLD as holding_account_type,
  BLRC.BLBL_DUE_DT as payment_applicable_billing_due_date,
  BLRC.BLRC_ALLOC_RCPT_ID as allocated_receipt_id,
  BLRC.BLRC_BLBL_PAID_STS as bill_payment_status,
  BLRC.BLRC_BLCS_PAID_STS as billing_contract_payment_status,
  BLRC.BLRC_PRCS_ID as billing_process_id,
  RCPT.RCPT_INPUT_AFAI_ID as alternate_funding_agreement_id,
  BLRC.BLRC_MAN_ALLOC_IND as manual_allocation_code,
  RCPT.RCPT_SUPRS_PRT_IND as suppress_reports_code,
  RCPT.RCPT_RCPT_CD as receipt_payment_type,
  RCPT.RCPT_MCTR_HOLD as holding_account,
  RCPT.MCBD_ID as bank_id,
  RCPT.RCPT_CHECK_NO as payment_reference_number,
  RCPT.RCPT_ASSOC_RCPT_ID as associated_receipt_id,
  cast(null as string) as receipt_source,
  RCPT.RCPT_MCTR_RSN as receipt_reason,
  RCPT.RCPT_PAY_METH as receipt_payment_method,
  RCPT.RCPT_RVRS_IND as receipt_reversal_ind,
  RCPT.RCPT_INPA_DTM as receipt_payment_date_time,
  RCPT.RCPT_INPUT_BL_PER_NVL as receipt_Input_billing_period,
  RCPT.RCPT_INPUT_INVOICE_NVL as receipt_input_invoice_id,
  RCPT.RCPT_PROCESS_ORDER_NVL as receipt_process_order,
  BLRE_SEQ_NO as related_entity_sequence_number,
  FNAC.financial_activity_payment_details,
  BLAF.alternate_funding_parameter_details as alternate_funding_parameter_details,
  BLPT.alternate_funding_payment_details as alternate_funding_payment_details,
  BLAC.general_ledger_posting_details as general_ledger_posting_details,
  BLRH.billing_payment_recovery_details as billing_payment_recovery_details,
    filter(
    array(
      struct(
        md5(
          concat(
            char(31),
            nvl(cast(BLRC.RCPT_ID AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(cast(BLRC.BLEI_CK AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(CAST(BLRC.BLRC_SEQ_NO AS STRING), CHAR(0)),
            CHAR(31),
            '_',
            char(31),
            nvl(
              CAST(BLRC.abacus_record_id AS STRING),
              CHAR(0)
            )
          )
        ) as reference_id,
        'CMC_BLRC_BILL_RCPT' as source_table_name,
        BLRC.abacus_record_id as abacus_record_id
      ),
      struct(
        md5(
          concat(
            char(31),
            nvl(cast(BLRC.RCPT_ID AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(cast(BLRC.BLEI_CK AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(CAST(BLRC.BLRC_SEQ_NO AS STRING), CHAR(0)),
            CHAR(31),
            '_',
            char(31),
            nvl(
              CAST(RCPT.abacus_record_id AS STRING),
              CHAR(0)
            )
          )
        ) as reference_id,
        'CMC_RCPT_RECEIPTS' as source_table_name,
        RCPT.abacus_record_id as abacus_record_id
      ),
      struct(
        md5(
          concat(
            char(31),
            nvl(cast(BLRC.RCPT_ID AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(cast(BLRC.BLEI_CK AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(CAST(BLRC.BLRC_SEQ_NO AS STRING), CHAR(0)),
            CHAR(31),
            '_',
            char(31),
            nvl(
              CAST(BLBL.abacus_record_id AS STRING),
              CHAR(0)
            )
          )
        ) as reference_id,
        'CMC_BLBL_BILL_SUMM' as source_table_name,
        BLBL.abacus_record_id as abacus_record_id
      ),
      struct(
        md5(
          concat(
            char(31),
            nvl(cast(BLRC.RCPT_ID AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(cast(BLRC.BLEI_CK AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(CAST(BLRC.BLRC_SEQ_NO AS STRING), CHAR(0)),
            CHAR(31),
            '_',
            char(31),
            nvl(
              CAST(INID.abacus_record_id AS STRING),
              CHAR(0)
            )
          )
        ) as reference_id,
        'CDS_INID_INVOICE' as source_table_name,
        INID.abacus_record_id as abacus_record_id
      ),
      struct(
        md5(
          concat(
            char(31),
            nvl(cast(BLRC.RCPT_ID AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(cast(BLRC.BLEI_CK AS STRING), char(0)),
            char(31),
            '_',
            char(31),
            nvl(CAST(BLRC.BLRC_SEQ_NO AS STRING), CHAR(0)),
            CHAR(31),
            '_',
            char(31),
            nvl(
              CAST(GRGR.abacus_record_id AS STRING),
              CHAR(0)
            )
          )
        ) as reference_id,
        'CMC_GRGR_GROUP' as source_table_name,
        GRGR.abacus_record_id as abacus_record_id
      )
    ),
    x -> x ["abacus_record_id"] is not null
  ) as source_extension_record_id,
  map(
     'original_source_value',
     CAST(NULL AS string)
   ) as original_source_value,
  'bill_payment' as abacus_entity_type,
cast(greatest(
  nvl(BLRC.abacus_ingestion_id, 0),
  nvl(RCPT.abacus_ingestion_id, 0),
  nvl(BLBL.abacus_ingestion_id, 0),
  nvl(INID.abacus_ingestion_id, 0),
  nvl(GRGR.abacus_ingestion_id, 0)
  ) as string) as abacus_ingestion_id,
  now() as abacus_consume_timestamp,