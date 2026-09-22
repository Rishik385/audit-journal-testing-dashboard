USE audit_analytics;

DROP VIEW IF EXISTS audit_rule_summary;

CREATE VIEW audit_rule_summary AS
SELECT 'Weekend Posting' AS audit_rule, SUM(weekend_flag) AS flagged_count
FROM audit_flags

UNION ALL

SELECT 'Round Amount', SUM(round_amount_flag)
FROM audit_flags

UNION ALL

SELECT 'Near Approval Limit', SUM(near_approval_limit_flag)
FROM audit_flags

UNION ALL

SELECT 'Same Creator Approver', SUM(same_creator_approver_flag)
FROM audit_flags;
