USE audit_analytics;

SELECT
    'Weekend Posting' AS audit_test,
    SUM(DAYOFWEEK(posting_date) IN (1,7) AND anomaly_type = 'WEEKEND_POSTING') AS true_positives,
    SUM(DAYOFWEEK(posting_date) IN (1,7) AND (anomaly_type IS NULL OR anomaly_type <> 'WEEKEND_POSTING')) AS false_positives,
    SUM(DAYOFWEEK(posting_date) NOT IN (1,7) AND anomaly_type = 'WEEKEND_POSTING') AS false_negatives
FROM journal_entries

UNION ALL

SELECT
    'Round Amount',
    SUM(MOD(amount,1000) = 0 AND anomaly_type = 'ROUND_AMOUNT'),
    SUM(MOD(amount,1000) = 0 AND (anomaly_type IS NULL OR anomaly_type <> 'ROUND_AMOUNT')),
    SUM(MOD(amount,1000) <> 0 AND anomaly_type = 'ROUND_AMOUNT')
FROM journal_entries

UNION ALL

SELECT
    'Near Approval Limit',
    SUM(amount >= 95000 AND amount < 100000 AND anomaly_type = 'NEAR_APPROVAL_LIMIT'),
    SUM(amount >= 95000 AND amount < 100000 AND (anomaly_type IS NULL OR anomaly_type <> 'NEAR_APPROVAL_LIMIT')),
    SUM((amount < 95000 OR amount >= 100000) AND anomaly_type = 'NEAR_APPROVAL_LIMIT')
FROM journal_entries

UNION ALL

SELECT
    'Same Creator Approver',
    SUM(created_by = approved_by AND anomaly_type = 'SAME_CREATOR_APPROVER'),
    SUM(created_by = approved_by AND (anomaly_type IS NULL OR anomaly_type <> 'SAME_CREATOR_APPROVER')),
    SUM(created_by <> approved_by AND anomaly_type = 'SAME_CREATOR_APPROVER')
FROM journal_entries;
