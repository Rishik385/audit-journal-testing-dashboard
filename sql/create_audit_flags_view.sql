USE audit_analytics;

DROP VIEW IF EXISTS audit_flags;

CREATE VIEW audit_flags AS
SELECT
    journal_id,
    posting_date,
    account_code,
    account_name,
    amount,
    description,
    source_system,
    created_by,
    approved_by,
    created_timestamp,
    approval_timestamp,
    anomaly_type,

    CASE
        WHEN DAYOFWEEK(posting_date) IN (1,7)
        THEN 1 ELSE 0
    END AS weekend_flag,

    CASE
        WHEN MOD(amount,1000) = 0
        THEN 1 ELSE 0
    END AS round_amount_flag,

    CASE
        WHEN amount >= 95000 AND amount < 100000
        THEN 1 ELSE 0
    END AS near_approval_limit_flag,

    CASE
        WHEN created_by = approved_by
        THEN 1 ELSE 0
    END AS same_creator_approver_flag

FROM journal_entries;
