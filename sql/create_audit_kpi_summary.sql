USE audit_analytics;

DROP VIEW IF EXISTS audit_kpi_summary;

CREATE VIEW audit_kpi_summary AS
SELECT
    COUNT(*) AS total_journal_entries,

    SUM(amount) AS total_transaction_value,

    SUM(weekend_flag) AS weekend_posting_count,

    SUM(round_amount_flag) AS round_amount_count,

    SUM(near_approval_limit_flag) AS near_approval_limit_count,

    SUM(same_creator_approver_flag) AS same_creator_approver_count,

    SUM(total_flags > 0) AS flagged_entries,

    SUM(total_flags > 1) AS multiple_flag_entries,

    SUM(anomaly_type IS NOT NULL) AS injected_anomaly_records

FROM audit_dashboard;
