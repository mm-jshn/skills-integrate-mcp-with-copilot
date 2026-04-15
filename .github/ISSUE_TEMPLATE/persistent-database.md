---
title: "Persistent Database Backend"
labels: [enhancement]
---

## Feature
Replace in-memory storage with a persistent database (e.g., SQLite, PostgreSQL, MySQL) for all data (activities, users, attendance, etc.).

## Why
Ensures data is not lost on server restart and supports scaling.

## Acceptance Criteria
- All data stored in a database
- Migrations for schema changes
- No loss of data on restart
