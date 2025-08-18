TRUNCATE TABLE rules RESTART IDENTITY;

INSERT INTO rules (title, description, code_pattern, severity, language, category, practice_type)
VALUES
    -- Bad Practices (with Regex Patterns)
    ('Avoid SELECT *', 'Using SELECT * can cause performance issues and break views or code if the schema changes.', 'select\s+\*\s+from', 'Major', 'SQL', 'Performance', 'bad'),
    ('Avoid Leading Wildcards in LIKE', 'Leading wildcards in LIKE clauses prevent the database from using an index, leading to slow queries.', 'like\s+''%[^'']*%''', 'Major', 'SQL', 'Performance', 'bad'),
    ('Avoid DELETE without WHERE', 'DELETE statements without a WHERE clause will delete all rows in a table. Use TRUNCATE for clarity if this is intended.', 'delete\s+from\s+[a-zA-Z0-9_]+\s*;', 'Major', 'SQL', 'Data Integrity', 'bad'),
    ('Avoid Implicit Joins', 'Use explicit JOIN syntax instead of comma-separated tables in the FROM clause for better readability and to avoid accidental cross joins.', '(?i)\\bfrom\\b(?:(?!\\bwhere\\b|\\bgroup by\\b|\\border by\\b|\\bjoin\\b).)*,', 'Minor', 'SQL', 'Clarity', 'bad'),

    -- Good Practices (with Simple Keywords)
    ('Use Explicit Column Names', 'Always specify the columns you need in a SELECT statement.', 'select', 'Minor', 'SQL', 'Clarity', 'good'),
    ('Use Explicit JOINs', 'Use explicit JOIN syntax for clarity and to prevent accidental cross joins.', 'join', 'Minor', 'SQL', 'Clarity', 'good'),

    -- More Bad Practices
    ('Avoid NOLOCK hint', 'The NOLOCK hint can lead to reading uncommitted data (dirty reads), which can cause data inconsistency.', '\(\s*NOLOCK\s*\)', 'Critical', 'SQL', 'Data Integrity', 'bad'),
    ('Avoid functions on indexed columns', 'Applying functions to indexed columns in a WHERE clause can prevent the optimizer from using the index.', 'WHERE\s+\w+\([^)]+\)\s*=', 'Major', 'SQL', 'Performance', 'bad'),
    ('Use COUNT(1) or COUNT(column) instead of COUNT(*)', 'COUNT(*) can be slower as it may check all columns. Use COUNT(1) for existence checks or COUNT(column) for non-null counts.', 'COUNT\s*\(\s*\*\s*\)', 'Minor', 'SQL', 'Performance', 'bad'),
    ('Avoid HAVING for WHERE conditions', 'HAVING should only be used to filter aggregated results. Use WHERE for row-level filtering before aggregation.', 'having\s+[^=]*$', 'Minor', 'SQL', 'Performance', 'bad'),
    ('Use table aliases in JOINs', 'Using table aliases (e.g., `FROM products p JOIN categories c`) improves readability, especially in complex queries.', '(?i)\\bjoin\\b\\s+\\w+\\s+(?!as\\b)\\w+\\s+\\bon\\b', 'Minor', 'SQL', 'Clarity', 'bad'),

    -- More Good Practices
    ('Use TRUNCATE to clear tables', 'TRUNCATE is faster than DELETE for clearing all rows from a table.', 'truncate\s+table', 'Minor', 'SQL', 'Performance', 'good'),
    ('Use UNION ALL over UNION', 'Use UNION ALL if you do not need to remove duplicate rows, as it is more performant.', 'union\s+all', 'Minor', 'SQL', 'Performance', 'good'),
    ('Use table aliases', 'Using table aliases improves readability in queries with multiple tables.', 'as\s+[a-zA-Z_]', 'Minor', 'SQL', 'Clarity', 'good'),
    ('Use CASE for conditional logic', 'The CASE statement is the standard way to handle conditional logic within SQL queries.', 'case\s+when', 'Minor', 'SQL', 'Clarity', 'good'),
    ('Comment complex queries', 'Adding comments (--) to explain complex logic improves maintainability.', '--', 'Minor', 'SQL', 'Clarity', 'good'),
    ('Avoid storing SSN in plain text', 'Social Security Numbers must be encrypted or hashed when stored in healthcare systems for HIPAA compliance.', '(?i)(create|alter)\s+table.*ssn\s+(?:varchar|char|text)', 'Critical', 'SQL', 'Security', 'bad'),
    ('Avoid unencrypted patient identifiers', 'Patient identifiers like MRN, SSN, or DOB should be encrypted in healthcare databases.', '(?i)(create|alter)\s+table.*(?:patient_id|mrn|medical_record_number|date_of_birth|dob)\s+(?:varchar|char|text|date)(?!\s+encrypted)', 'Critical', 'SQL', 'Security', 'bad'),
    ('Missing audit columns on patient tables', 'Healthcare data tables must have audit columns (created_by, modified_by, created_at, modified_at) for compliance.', '(?i)create\s+table\s+(?:patient|diagnosis|medication|encounter)(?!.*(?:created_by|modified_by))', 'Major', 'SQL', 'Compliance', 'bad'),
    
    -- Data Modification Bad Practices
    ('Direct UPDATE on diagnosis codes', 'Diagnosis codes (ICD-10/CPT) should not be directly updated. Use versioning or audit trails instead.', '(?i)update\s+(?:diagnosis|icd|cpt|procedure_codes?).*set\s+(?:code|icd_code|cpt_code)', 'Critical', 'SQL', 'Data Integrity', 'bad'),
    ('DELETE patient records without archiving', 'Patient records should be archived, not deleted, to maintain medical history and comply with retention policies.', '(?i)delete\s+from\s+(?:patient|encounter|diagnosis|medication|lab_result)', 'Critical', 'SQL', 'Compliance', 'bad'),
    ('Bulk UPDATE on clinical data', 'Bulk updates on clinical data without WHERE clause can compromise patient safety and data integrity.', '(?i)update\s+(?:medication|dosage|lab_result|vital_signs?|allerg(?:y|ies))(?:\s+set)?(?!.*where)', 'Critical', 'SQL', 'Data Integrity', 'bad'),
    
    -- Specific Column Alteration Rules
    ('ALTER medication dosage columns', 'Changing medication dosage column types can lead to precision loss and patient safety issues.', '(?i)alter\s+table\s+\w*(?:medication|prescription|drug)\w*.*(?:modify|alter)\s+column\s+\w*(?:dose|dosage|quantity)\w*', 'Critical', 'SQL', 'Data Integrity', 'bad'),
    ('DROP COLUMN on clinical tables', 'Dropping columns from clinical tables can violate data retention requirements.', '(?i)alter\s+table\s+(?:patient|diagnosis|medication|lab_result|encounter).*drop\s+column', 'Major', 'SQL', 'Compliance', 'bad'),
    ('FLOAT for medication dosages', 'Use DECIMAL for medication dosages instead of FLOAT to avoid precision errors that could affect patient safety.', '(?i)(?:create|alter)\s+table.*(?:dose|dosage|quantity)\s+float', 'Critical', 'SQL', 'Data Integrity', 'bad'),
    
    -- Good Practices for Health Data
    ('Use encryption for PHI', 'Personal Health Information should be encrypted using appropriate encryption functions.', '(?i)(?:aes_encrypt|encrypt|hashbytes)', 'Minor', 'SQL', 'Security', 'good'),
    ('Audit trail implementation', 'Using triggers or temporal tables for audit trails on sensitive health data.', '(?i)(?:create\s+trigger.*for\s+(?:insert|update|delete)|temporal_table|system_versioning)', 'Minor', 'SQL', 'Compliance', 'good'),
    ('Parameterized queries for patient data', 'Using parameterized queries (@param or ?) prevents SQL injection when handling patient data.', '(?:@\w+|\\?)', 'Minor', 'SQL', 'Security', 'good'),
    
    -- Data Quality Rules
    ('NULL values in critical health fields', 'Critical fields like blood type, allergies, or emergency contact should have NOT NULL constraints.', '(?i)create\s+table.*(?:blood_type|allerg(?:y|ies)|emergency_contact)(?!.*not\s+null)', 'Major', 'SQL', 'Data Integrity', 'bad'),
    ('Missing check constraints on vital signs', 'Vital signs should have reasonable check constraints (e.g., heart rate between 0-300).', '(?i)create\s+table.*(?:heart_rate|blood_pressure|temperature|weight)(?!.*check)', 'Major', 'SQL', 'Data Integrity', 'bad'),
    
    -- Performance specific to health data
    ('Missing index on patient lookup columns', 'Common lookup columns (MRN, SSN, patient_id) should be indexed for performance.', '(?i)create\s+table\s+patient(?!.*(?:create\s+index|index\s+on).*(?:mrn|patient_id|ssn))', 'Major', 'SQL', 'Performance', 'bad'),
    ('Joining large clinical tables without filters', 'Joining encounter/diagnosis tables without date filters can cause performance issues.', '(?i)join\s+(?:encounter|diagnosis|lab_result)(?!.*where.*(?:date|created_at|encounter_date))', 'Major', 'SQL', 'Performance', 'bad');