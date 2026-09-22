
CREATE DATABASE IF NOT EXISTS audit_analytics;

USE audit_analytics;

DROP TABLE IF EXISTS journal_entries;

CREATE TABLE journal_entries (
    journal_id VARCHAR(20) PRIMARY KEY,
    posting_date DATE NOT NULL,
    account_code VARCHAR(20) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    description VARCHAR(255),
    source_system VARCHAR(30),
    created_by VARCHAR(50) NOT NULL,
    approved_by VARCHAR(50) NOT NULL,
    created_timestamp DATETIME NOT NULL,
    approval_timestamp DATETIME NOT NULL,
    is_injected BOOLEAN DEFAULT FALSE,
    anomaly_type VARCHAR(255) DEFAULT NULL
);