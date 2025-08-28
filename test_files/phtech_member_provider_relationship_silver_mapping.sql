CREATE OR REPLACE GLOBAL TEMP VIEW V_PHTECH_ELIGIBILITY_PHT_MPR as 
 select * FROM 
 (
  SELECT 
  member_id,
  eligibility_ud,
  eligibility_id,
  cim_system,
  benefitplan_nm,
  benefitplan_ud,
  relationship_ud,
  subscriber_id,
  hic_number,
  medicaid_number,
  abacus_record_id,
  row_number()over(partition by member_id||cim_system ORDER BY eff_date DESC, term_date DESC) as rn
  FROM BRONZE.PHTECH_ELIGIBILITY)
  where rn =1;

CREATE OR REPLACE GLOBAL TEMP VIEW V_PHTECH_MEMBER_PCP_PHT_MPR as 
 SELECT * FROM 
 (
  SELECT 
  member_id,
  provider_id,
  practice_office_id,
  provider_gender,
  provider_dob,
  cim_system,
  member_pcp_id,
  npi,
  carrier_ud,
  taxonomy_code,
  provider_full_name,
  provider_first_name,
  provider_middle_name,
  provider_last_name,
  provider_suffix,
  eff_date,
  abacus_record_id,
  ROW_NUMBER() OVER (PARTITION by member_id||cim_system ORDER BY eff_date DESC, term_date DESC) as rn
  FROM BRONZE.PHTECH_MEMBER_PCP
  WHERE provider_category = 'PCP')
  WHERE rn =1;

CREATE OR REPLACE GLOBAL TEMP VIEW V_PHTECH_PROVIDER_CONTRACT_PHT_MPR as 
 SELECT * FROM 
 (
  SELECT 
  provider_id,
  tax_id,
  provider_contract_id,
  cim_system,
  carrier_id,
  is_pcp,
  abacus_record_id,
  ROW_NUMBER() OVER (PARTITION by provider_id||cim_system ORDER BY eff_date DESC, term_date DESC) as rn
  FROM BRONZE.PHTECH_PROVIDER_CONTRACT)
  WHERE rn =1;

CREATE OR REPLACE GLOBAL TEMP VIEW V_PHTECH_PROVIDER_PRACTICE_OFFICE_PHT_MPR as 
 SELECT * FROM 
 (
  SELECT 
  provider_id,
  address1,
  address2,
  city,
  county,
  state,
  zipcode,
  phone,
  practice_office_id,
  cim_system,
  provider_practice_office_id,
  abacus_record_id,
  ROW_NUMBER() OVER (PARTITION by provider_id||practice_office_id ORDER BY abacus_event_order DESC) as rn
  FROM BRONZE.PHTECH_PROVIDER_PRACTICE_OFFICE)
  WHERE rn =1;

CREATE OR REPLACE GLOBAL TEMP VIEW V_PHTECH_MEMBER_RACE_PHT_MPR as 
 SELECT * FROM 
 (
  SELECT 
  member_id,
  member_race_id,
  race_ud,
  abacus_record_id,
  cim_system,
  ROW_NUMBER() OVER (PARTITION by member_id||cim_system ORDER BY member_race_id) as rn
  FROM BRONZE.PHTECH_MEMBER_RACE)
  WHERE rn =1;

CREATE OR REPLACE GLOBAL TEMP VIEW V_PHTECH_MEMBER_ETHNICITY_PHT_MPR as 
 SELECT * FROM 
 (
  SELECT 
  member_id,
  member_ethnicity_id,
  ethnicity_ud,
  abacus_record_id,
  cim_system,
  ROW_NUMBER() OVER (PARTITION by member_id||cim_system ORDER BY member_ethnicity_id) as rn
  FROM BRONZE.PHTECH_MEMBER_ETHNICITY)
  WHERE rn =1;

CREATE OR REPLACE GLOBAL TEMP VIEW V_PHTECH_PROVIDER_CATEGORY_PHT_MPR as 
 SELECT * FROM 
 (
  SELECT 
  provider_id,
  provider_category_id,
  provider_category,
  provider_category_name,
  cim_system,
  abacus_record_id,
  ROW_NUMBER() OVER (PARTITION by provider_id||cim_system ORDER BY eff_date DESC, term_date DESC) as rn
  FROM BRONZE.PHTECH_PROVIDER_CATEGORY
  WHERE provider_category = 'PCP')
  WHERE rn =1;

select
COALESCE(CAST(mem.member_id||PCP.EFF_DATE AS STRING), CAST(mem.member_id AS STRING)) as member_provider_relationship_id,
COALESCE(CAST(mem.member_id||PCP.EFF_DATE AS STRING), CAST(mem.member_id AS STRING)) as source_member_provider_relationship_id,
CAST(mem.member_id AS STRING) as member_source_id,
CAST(elig.eligibility_ud AS STRING) as assoc_member_member_type,
elig.benefitplan_nm as assoc_member_member_category,
elig.benefitplan_ud as assoc_member_member_category_id,
elig.relationship_ud as assoc_member_subscriber_relationship,
CAST(elig.subscriber_id  AS STRING) as assoc_member_subscriber_id,
CAST(pc.carrier_id  AS STRING) as assoc_member_carrier_id,
mem.first_name as assoc_member_first_name,
mem.middle_name as assoc_member_middle_name,
mem.last_name as assoc_member_last_name,
mem.name_prefix as assoc_member_prefix_name,
mem.name_suffix as assoc_member_suffix_name,
mem.address1 as assoc_member_address_line_1,
mem.address2 as assoc_member_address_line_2,
mem.city as assoc_member_city,
mem.county as assoc_member_county,
mem.state as assoc_member_state_province,
Coalesce(substring(mem.zipcode, 1,5), 'Unknown') as assoc_member_postal_code,
Case When LENGTH(trim(replace(mem.zipcode, '-', ''))) = 9 Then substring(replace(mem.zipcode, '-', ''),6,4) else 'Unknown' End as assoc_member_zip_code_extension,
mem.phone as assoc_member_phone_number,
mem.phone_ext as assoc_member_extension,
CAST(mem.dob AS TIMESTAMP) as assoc_member_date_of_birth,
cast(substr(mem.dob,1,4) AS STRING) as assoc_member_year_of_birth,
elig.hic_number as assoc_member_medicare_hic_number,
elig.medicaid_number as assoc_member_medicaid_id,
CASE WHEN upper(mem.gender) = 'F' THEN 'Female' 
      WHEN upper(mem.gender) = 'M' THEN 'Male' 
      WHEN upper(MEM.gender) = 'U' THEN 'Unknown' 
ELSE mem.gender END as assoc_member_gender,
race.race_ud as assoc_member_race,
eth.ethnicity_ud as assoc_member_ethnicity,
CAST(mem.dod AS DATE) AS assoc_member_deceased_date,
po.address1 as assoc_provider_address_line_1,
po.address2 as assoc_provider_address_line_2,
po.city as assoc_provider_city,
po.county as assoc_provider_county,
po.state as assoc_provider_state_province,
Coalesce(substring(TRIM(po.zipcode), 1,5), 'Unknown') as assoc_provider_postal_code,
Case When LENGTH(trim(po.zipcode)) = 9 Then substring(po.zipcode,6,4) else 'Unknown' End as assoc_provider_zip_code_extension,
CASE WHEN upper(pcp.provider_gender) = 'F' THEN 'Female' 
      WHEN upper(pcp.provider_gender) = 'M' THEN 'Male' 
      WHEN upper(pcp.provider_gender) = 'U' THEN 'Unknown' 
ELSE pcp.provider_gender END as assoc_provider_gender,
CAST(pcp.provider_dob AS DATE) as assoc_provider_birth_date,
cat.provider_category_name as assoc_provider_category,
CAST(pcp.eff_date AS DATE) as assoc_provider_eff_date,
CAST(pcp.eff_date AS DATE) as assoc_provider_exp_date,
pcp.npi as assoc_provider_npi,
CASE WHEN is_pcp = 1 THEN TRUE ELSE FALSE END as assoc_provider_pcp_ind,
pcp.provider_first_name as assoc_provider_first_name,
pcp.provider_middle_name as assoc_provider_middle_name,
pcp.provider_last_name as assoc_provider_last_name,
pcp.provider_suffix as assoc_provider_suffix_name,
po.phone as assoc_provider_phone,
ps.specialty_nm as assoc_provider_specialty,
filter(array(
      struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(mem.MEMBER_ID) AS STRING), CHAR(0)), 
          nvl(CAST(trim(mem.cim_system) AS STRING), CHAR(0)), 'PHTECH_MEMBER', CHAR(31))) as reference_id,
          'PHTECH_MEMBER' as source_table_name,
          trim(mem.abacus_record_id) as abacus_record_id
      ),

      struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(elig.eligibility_id) AS STRING), CHAR(0)),
          nvl(CAST(trim(elig.cim_system) AS STRING), CHAR(0)), 'PHTECH_ELIGIBILITY', CHAR(31))) as reference_id,
          'PHTECH_ELIGIBILITY' as source_table_name,
          trim(elig.abacus_record_id) as abacus_record_id
      ),

      struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(pcp.member_pcp_id) AS STRING), CHAR(0)), 
          nvl(CAST(trim(pcp.carrier_ud) AS STRING), CHAR(0)), 
          nvl(CAST(trim(pcp.cim_system) AS STRING), CHAR(0)), 'PHTECH_MEMBER_PCP', CHAR(31))) as reference_id,
          'PHTECH_MEMBER_PCP' as source_table_name,
          trim(pcp.abacus_record_id) as abacus_record_id
      ),

      struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(pc.provider_contract_id) AS STRING), CHAR(0)),
          nvl(CAST(trim(pc.cim_system) AS STRING), CHAR(0)), 'PHTECH_PROVIDER_CONTRACT', CHAR(31))) as reference_id,
          'PHTECH_PROVIDER_CONTRACT' as source_table_name,
          trim(pc.abacus_record_id) as abacus_record_id
       ),
    struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(po.provider_practice_office_id) AS STRING), CHAR(0)),
          nvl(CAST(trim(po.practice_office_id) AS STRING), CHAR(0)),
          nvl(CAST(trim(po.cim_system) AS STRING), CHAR(0)), 'provider_practice_office', CHAR(31))) as reference_id,
          'provider_practice_office' as source_table_name,
          trim(po.abacus_record_id) as abacus_record_id
      
      ),
    struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(cat.provider_category_id) AS STRING), CHAR(0)),
          nvl(CAST(trim(cat.cim_system) AS STRING), CHAR(0)), 'PHTECH_PROVIDER_CATEGORY', CHAR(31))) as reference_id,
          'PHTECH_PROVIDER_CATEGORY' as source_table_name,
          trim(cat.abacus_record_id) as abacus_record_id
    ),
    struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(race.member_race_id) AS STRING), CHAR(0)),
          nvl(CAST(trim(race.cim_system) AS STRING), CHAR(0)), 'PHTECH_MEMBER_RACE', CHAR(31))) as reference_id,
          'PHTECH_MEMBER_RACE' as source_table_name,
          trim(race.abacus_record_id) as abacus_record_id
    ),
    struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(eth.member_ethnicity_id)AS STRING), CHAR(0)),
          nvl(CAST(trim(eth.cim_system) AS STRING), CHAR(0)), 'PHTECH_MEMBER_ETHNICITY', CHAR(31))) as reference_id,
          'PHTECH_MEMBER_ETHNICITY' as source_table_name,
          trim(eth.abacus_record_id) as abacus_record_id
    ),
    struct(
          md5(concat(char(31), 'PHTech_Member_Provider_Relationship', char(31), nvl(CAST(trim(ps.provider_specialty_id)AS STRING), CHAR(0)),
          nvl(CAST(trim(ps.cim_system) AS STRING), CHAR(0)), 'PHTECH_PROVIDER_SPECIALTY', CHAR(31))) as reference_id,
          'PHTECH_PROVIDER_SPECIALTY' as source_table_name,
          trim(ps.abacus_record_id) as abacus_record_id
    )
    ),x->x["abacus_record_id"] is not null) as source_extension_record_id,
mem.abacus_ingestion_id as abacus_ingestion_id,
mem.abacus_record_id as abacus_record_id,
'PHTech' as source_name,
COALESCE(CAST(mem.member_id||PCP.EFF_DATE AS STRING), CAST(mem.member_id AS STRING)) as source_id,
CAST(True AS BOOLEAN) as source_authoritative_ind,
mem.abacus_source_file as source_file_name,
pc.tax_id as assoc_provider_tin,
array(
      struct(
    md5(
			concat(
				CHAR(31),
				'phtech_member_provider_relationship',
				char(31),
				NVL(CAST(trim(mem.member_id) AS STRING),CHAR(0)), 
				CHAR(31), 
				NVL(CAST(trim(pcp.EFF_DATE) AS STRING), CHAR(0)), 
				'assoc_service_providers', 
				CHAR(31)
	  )
		) AS reference_id,
 	CAST(pcp.provider_id AS STRING) as id,
  CAST(pcp.provider_id AS STRING) as source_service_provider_id,
  TRIM(pcp.provider_full_name) AS full_name ,
  TRIM(pcp.provider_first_name) AS first_name ,
  TRIM(pcp.provider_last_name) AS last_name ,
  TRIM(pcp.provider_middle_name) AS middle_name ,
  CAST(NULL AS STRING) as address_use,
  TRIM(po.address1) AS address_line_1,
  TRIM(po.address2) AS address_line_2,
  po.county as assoc_provider_county,
  TRIM(po.CITY) AS city,
  NULL as country,
  TRIM(po.STATE) AS state,
  COALESCE(substring(TRIM(po.zipcode), 1,5), 'Unknown') as postal_code,
  Case When len(trim(replace(po.zipcode, '-', ''))) = 9 Then substring(po.zipcode,6,4) else 'Unknown' End AS zip_code_extension,
  CAST(NULL AS STRING) as longitude,
  CAST(NULL AS STRING) as latitude,
  TRIM(po.phone) AS phone,
  NULL AS group_name,
  NULL as billing_group_name,
  pc.tax_id as tin,
  pcp.npi as npi,
  NULL AS type,
  NULL as primary_specialty_code,
  NULL AS other_specialty_code_1 ,
  null AS other_specialty_code_2 ,
  CAST(pcp.taxonomy_code as STRING) AS taxonomy_code_1,
  NULL AS taxonomy_code_2 , 
  NULL AS taxonomy_code_3, 
  NULL as group_id,
  NULL As id_code_type,
  NULL As id_code_desc
  )
) as assoc_service_providers
FROM BRONZE.PHTECh_member mem
LEFT JOIN global_temp.V_PHTECH_ELIGIBILITY_PHT_MPR elig
on mem.member_id = elig.member_id
LEFT JOIN global_temp.V_PHTECH_MEMBER_RACE_PHT_MPR race 
ON mem.member_id = race.member_id
LEFT JOIN global_temp.V_PHTECH_MEMBER_ETHNICITY_PHT_MPR ETH 
ON mem.member_id = ETH.member_id
LEFT JOIN global_temp.V_PHTECH_MEMBER_PCP_PHT_MPR pcp
on mem.member_id = pcp.member_id
LEFT JOIN global_temp.V_PHTECH_PROVIDER_PRACTICE_OFFICE_PHT_MPR  PO
ON pcp.provider_id = PO.provider_id
and pcp.practice_office_id = PO.practice_office_id
LEFT JOIN global_temp.V_PHTECH_PROVIDER_CONTRACT_PHT_MPR PC
ON pcp.provider_id = PC.provider_id
LEFT JOIN global_temp.V_PHTECH_PROVIDER_CATEGORY_PHT_MPR cat
ON pcp.provider_id = cat.provider_id 
LEFT JOIN BRONZE.PHTECH_PROVIDER_SPECIALTY ps
ON pcp.taxonomy_code = ps.taxonomy_code
and pcp.provider_id = ps.provider_id