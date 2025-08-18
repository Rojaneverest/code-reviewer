-- Test Query for Health Data Rules
-- This query contains multiple bad practices

-- Bad: SELECT * from patient table
SELECT * FROM patients p
-- Bad: Implicit join with comma
FROM patients, encounters e, medications m
-- Bad: Leading wildcard in patient search
WHERE p.name LIKE '%Smith%'
-- Bad: Function on indexed column
AND UPPER(p.mrn) = 'MRN123456'
-- Bad: NOLOCK hint on sensitive data
AND e.patient_id = p.id WITH (NOLOCK);

-- Bad: Direct UPDATE on diagnosis without WHERE (bulk update)
UPDATE diagnosis 
SET icd_code = 'I10';

-- Bad: DELETE patient records without archiving
DELETE FROM patient 
WHERE last_visit_date < '2020-01-01';

-- Bad: ALTER medication dosage column
ALTER TABLE medications 
ALTER COLUMN dosage FLOAT;

-- Bad: CREATE table with SSN in plain text
CREATE TABLE patient_records (
    id INT PRIMARY KEY,
    ssn VARCHAR(11),  -- Bad: unencrypted SSN
    mrn VARCHAR(20),  -- Bad: unencrypted MRN
    blood_type VARCHAR(3),  -- Bad: missing NOT NULL
    weight DECIMAL(5,2),  -- Bad: missing check constraint
    -- Bad: missing audit columns (created_by, modified_by, etc.)
);

-- Bad: DROP COLUMN from clinical table
ALTER TABLE lab_results 
DROP COLUMN test_value;

-- Good practices that should be recognized:
TRUNCATE TABLE temp_data;

-- Good: Using encryption
SELECT patient_id, AES_ENCRYPT(ssn, 'key') as encrypted_ssn
FROM patients;

-- Good: Parameterized query
SELECT * FROM medications 
WHERE patient_id = @patient_id
AND prescription_date = ?;

-- Good: CASE statement for conditional logic
SELECT 
    patient_id,
    CASE 
        WHEN age < 18 THEN 'Pediatric'
        WHEN age >= 65 THEN 'Geriatric'
        ELSE 'Adult'
    END as patient_category
FROM patients p
-- Good: Explicit JOIN
INNER JOIN encounters e ON p.id = e.patient_id
-- Good: Using table aliases
WHERE e.encounter_date > '2024-01-01'
-- Good: UNION ALL for performance
UNION ALL
SELECT patient_id, 'Historical' as patient_category
FROM archived_patients;

-- Good: Comment explaining complex logic
-- This CTE calculates medication adherence rates for chronic conditions
WITH medication_adherence AS (
    SELECT COUNT(1) as dose_count  -- Good: COUNT(1) instead of COUNT(*)
    FROM medication_schedule
)
SELECT * FROM medication_adherence;