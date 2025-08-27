

CREATE TABLE source.healthcare_data
USING DELTA
AS
SELECT * FROM read_csv('dbfs:/FileStore/member_enrollment_file.csv', header=TRUE, infer_schema=TRUE);




CREATE TABLE target_domain_model (
    memberFirst STRING,
    memberLast STRING,
    mbrDOB DATE,
    mbrGender STRING,
    ssn STRING,
    memberID STRING,
    enrollmentStatus STRING,
    enrollmentEffectiveDate DATE,
    terminationDate DATE NULL,
    planID STRING,
    product STRING,
    lob STRING,
    memberMonth ARRAY<STRING>,
    dualEligibilityInd BOOLEAN,
    employerGroup ARRAY<OBJECT>,
    coverageDesc STRING,
    groupName STRING,
    groupStatus STRING,
    addressLine1 STRING,
    addressLine2 STRING NULL,
    zip STRING
);




SELECT
    memberFirst,
    memberLast,
    mbrDOB,
    mbrGender,
    ssn,
    memberID,
    enrollmentStatus,
    enrollmentEffectiveDate,
    terminationDate,
    planID,
    product,
    lob,
    memberMonth,
    dualEligibilityInd,
    employerGroup,
    coverageDesc,
    groupName,
    groupStatus,
    addressLine1,
    zip
FROM
    (SELECT
        FirstName AS memberFirst,
        LastName AS memberLast,
        DOB AS mbrDOB,
        Gender AS mbrGender,
        SSN AS ssn,
        MemberID AS memberID,
        CASE
            WHEN EnrollmentEnd IS NULL THEN 'Active'
            ELSE 'Inactive'
        END AS enrollmentStatus,
        EnrollmentStart AS enrollmentEffectiveDate,
        EnrollmentEnd AS terminationDate,
        GROUPID AS planID,
        GROUPNAME AS product,
        CASE
            WHEN GROUPID LIKE 'Group1%' THEN 'Commercial'
            ELSE 'Medicare'
        END AS lob,
        ARRAY_AGG(MONTH(DATEADD(month, 1, EnrollmentStart))) AS memberMonth,
        CASE
            WHEN MemberSeq > 1 THEN TRUE
            ELSE FALSE
        END AS dualEligibilityInd,
        ARRAY_AGG(STRUCT(GroupName AS groupName, GROUPID AS employerGroup)) AS employerGroup,
        CASE
            WHEN CoverageType = 'Medical' THEN 'Medical'
            ELSE 'Dental'
        END AS coverageDesc,
        GROUPNAME AS groupName,
        CASE
            WHEN GROUPStatus = 'Active' THEN 'Active'
            ELSE 'Inactive'
        END AS groupStatus,
        Address AS addressLine1,
        Zip AS zip
    FROM
        member_data) AS source_data;




SELECT
    UPPER(TRIM(FirstName)) AS memberFirst,
    UPPER(TRIM(LastName)) AS memberLast,
    TO_DATE(DOB) AS mbrDOB,
    CASE
        WHEN Gender = 'M' THEN 'Male'
        WHEN Gender = 'F' THEN 'Female'
        ELSE NULL
    END AS mbrGender,
    SSN AS ssn,
    MemberID::STRING AS memberID,
    CASE
        WHEN EnrollmentEnd IS NULL THEN 'Active'
        ELSE 'Inactive'
    END AS enrollmentStatus,
    EnrollmentStart AS enrollmentEffectiveDate,
    COALESCE(EnrollmentEnd, CURRENT_DATE()) AS terminationDate,
    GROUPING(PlanID) AS planID,
    GROUPING(Product) AS product,
    GROUPING(Lob) AS lob,
    memberMonthArray(EnrollmentStart, COALESCE(EnrollmentEnd, CURRENT_DATE())) AS memberMonth,
    CASE
        WHEN (EnrollmentEnd IS NULL OR EnrollmentEnd > CURRENT_DATE()) THEN TRUE
        ELSE FALSE
    END AS dualEligibilityInd,
    SYMBOL_CASE(GroupName, GroupID) AS employerGroup,
    CASE
        WHEN CoverageType = 'HMO' THEN 'HMO'
        WHEN CoverageType = 'PPO' THEN 'PPO'
        WHEN CoverageType = 'EPO' THEN 'EPO'
        ELSE NULL
    END AS coverageDesc,
    GroupName AS groupName,
    CASE
        WHEN GroupStatus = 'Active' THEN 'Active'
        ELSE 'Inactive'
    END AS groupStatus,
    Address AS addressLine1,
    Zip AS zip
FROM
    healthcare_data;




SELECT
    UPPER(memberFirst) AS memberFirst,
    UPPER(memberLast) AS memberLast,
    TO_DATE(DOB) AS mbrDOB,
    CASE
        WHEN Gender = 'M' THEN 'Male'
        WHEN Gender = 'F' THEN 'Female'
        ELSE 'Unknown'
    END AS mbrGender,
    SSN AS ssn,
    memberID AS memberID,
    CASE
        WHEN EnrollmentEnd IS NULL THEN 'Active'
        ELSE 'Inactive'
    END AS enrollmentStatus,
    EnrollmentStart AS enrollmentEffectiveDate,
    COALESCE(EnrollmentEnd, CURRENT_DATE()) AS terminationDate,
    planung.planID,
    planung.product,
    planung.lob,
    memberMonthArray(EnrollmentStart, COALESCE(EnrollmentEnd, CURRENT_DATE())) AS memberMonth,
    CASE
        WHEN dualEligibilityInd = TRUE THEN TRUE
        ELSE FALSE
    END AS dualEligibilityInd,
    array(SELECT groupName FROM group WHERE groupID = source.GroupID) AS employerGroup,
    CASE
        WHEN CoverageType = 'HMO' THEN 'HMO'
        WHEN CoverageType = 'PPO' THEN 'PPO'
        ELSE 'Other'
    END AS coverageDesc,
    groupName AS groupName,
    CASE
        WHEN GroupStatus = 'Active' THEN 'Active'
        ELSE 'Inactive'
    END AS groupStatus,
    Address AS addressLine1,
    Zip AS zip
FROM
    source_data
JOIN
    planung
ON
    source_data.MemberID = planung.memberID;





INSERT INTO target_table (memberFirst, memberLast, mbrDOB, mbrGender, ssn, memberID, enrollmentStatus, enrollmentEffectiveDate, terminationDate, planID, product, lob, memberMonth, dualEligibilityInd, employerGroup, coverageDesc, groupName, groupStatus, addressLine1, addressLine2, zip)
SELECT
    FirstName,
    LastName,
    DOB,
    Gender,
    SSN,
    MemberID,
    CASE
        WHEN EnrollmentEnd IS NULL THEN 'Active'
        ELSE 'Inactive'
    END AS enrollmentStatus,
    EnrollmentStart,
    EnrollmentEnd,
    'PlanA' AS planID,
    'HealthPlanA' AS product,
    'Medical' AS lob,
    GENERATE_DATE_ARRAY(EnrollmentStart, EnrollmentEnd, INTERVAL 1 MONTH),
    FALSE AS dualEligibilityInd,
    CAST(GroupName AS STRING) AS employerGroup,
    'Standard' AS coverageDesc,
    GroupName,
    'Active' AS groupStatus,
    Address,
    Zip
FROM
    source_table;

CREATE OR REPLACE TABLE target.transformed_members AS
SELECT
    memberFirst,
    memberLast,
    mbrDOB,
    mbrGender,
    ssn,
    memberID,
    enrollmentStatus,
    enrollmentEffectiveDate,
    CASE
        WHEN EnrollmentEnd IS NULL THEN NULL
        ELSE EnrollmentEnd
    END AS terminationDate,
    planID,
    product,
    lob,
    memberMonth,
    dualEligibilityInd,
    employerGroup,
    coverageDesc,
    groupName,
    groupStatus,
    Address,
    Zip
FROM
    (SELECT
        FirstName AS memberFirst,
        LastName AS memberLast,
        DOB AS mbrDOB,
        Gender AS mbrGender,
        SSN AS ssn,
        MemberID AS memberID,
        CASE
            WHEN EnrollmentEnd IS NULL THEN 'Active'
            ELSE 'Inactive'
        END AS enrollmentStatus,
        EnrollmentStart AS enrollmentEffectiveDate,
        CASE
            WHEN EnrollmentEnd IS NULL THEN NULL
            ELSE EnrollmentEnd
        END AS terminationDate,
        GROUPID AS planID,
        GROUPNAME AS product,
        CoverageType AS lob,
        GENERATE_DATE_ARRAY(EnrollmentStart, EnrollmentEnd, INTERVAL 1 MONTH) AS memberMonth,
        CASE
            WHEN GroupID IN (SELECT GroupID FROM Groups WHERE GroupStatus = 'Dual') THEN TRUE
            ELSE FALSE
        END AS dualEligibilityInd,
        JSON_ARRAYAGG(
            STRUCT(
                GroupName AS groupName,
                GroupStatus AS groupStatus
            )
        ) AS employerGroup,
        CASE
            WHEN CoverageType = 'Medical' THEN 'Medical'
            WHEN CoverageType = 'Dental' THEN 'Dental'
            WHEN CoverageType = 'Vision' THEN 'Vision'
            ELSE 'Other'
        END AS coverageDesc,
        GROUPNAME AS groupName,
        CASE
            WHEN GroupStatus = 'Active' THEN 'Active'
            ELSE 'Inactive'
        END AS groupStatus,
        Address AS Address,
        Zip AS Zip
    FROM
        members
) AS source_data;

EXPORT DATA target.transformed_members TO 's3://your-bucket/transformed_members/'
FILE_FORMAT = (TYPE = 'Parquet');


