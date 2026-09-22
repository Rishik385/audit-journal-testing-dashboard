USE audit_analytics;

DROP VIEW IF EXISTS audit_dashboard;

CREATE VIEW audit_dashboard AS
SELECT
    *,
    (
        weekend_flag
        + round_amount_flag
        + near_approval_limit_flag
        + same_creator_approver_flag
    ) AS total_flags,

    CASE
        WHEN (
            weekend_flag
            + round_amount_flag
            + near_approval_limit_flag
            + same_creator_approver_flag
        ) = 0 THEN 'No Flags'
        WHEN (
            weekend_flag
            + round_amount_flag
            + near_approval_limit_flag
            + same_creator_approver_flag
        ) = 1 THEN 'Single Flag'
        ELSE 'Multiple Flags'
    END AS risk_category

FROM audit_flags;
