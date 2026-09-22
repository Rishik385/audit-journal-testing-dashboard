# Audit Journal Entry Testing Dashboard

<p align="center">
  <strong>Rule-Based Audit Analytics using Python, MySQL, and Power BI</strong>
</p>

<p align="center">
  A data analytics project for identifying potentially unusual journal entries through automated audit rules and interactive dashboard reporting.
</p>

---

## Project Overview

The **Audit Journal Entry Testing Dashboard** analyzes journal entry data to identify potentially unusual transactions using rule-based audit tests.

The project simulates an audit analytics workflow in which journal entries are generated, stored in MySQL, evaluated using SQL rules, and presented through an interactive Power BI dashboard.

The dataset is synthetic and intended for educational and portfolio demonstration purposes.

## Objectives

- Generate a structured journal entry dataset.
- Store and analyze journal entries using MySQL.
- Identify potentially unusual transactions through audit rules.
- Summarize audit findings using SQL.
- Build an interactive Power BI dashboard.
- Validate detection rules against injected synthetic anomalies.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data generation and validation |
| Pandas | Data processing |
| Faker | Synthetic data generation |
| MySQL | Data storage and SQL analysis |
| SQL | Audit rules and KPI views |
| Power BI | Interactive dashboard |
| Git and GitHub | Version control and project sharing |

## Project Architecture

`	ext
Synthetic Data Generation
          |
          v
    CSV Dataset
          |
          v
     MySQL Database
          |
          v
    SQL Audit Rules
          |
          v
   KPI and Summary Views
          |
          v
   Power BI Dashboard
          |
          v
 Audit Analysis and Reporting

