from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS source_documents (
  id INTEGER PRIMARY KEY, canonical_url TEXT NOT NULL UNIQUE, title TEXT,
  source_type TEXT NOT NULL, source_grade TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS source_revisions (
  id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES source_documents(id),
  revision INTEGER NOT NULL, accessed_at TEXT NOT NULL, publication_date TEXT,
  content_hash TEXT NOT NULL, media_type TEXT, raw_path TEXT, parsed_path TEXT,
  access_limited INTEGER NOT NULL DEFAULT 0,
  UNIQUE(document_id, revision), UNIQUE(document_id, content_hash)
);
CREATE TABLE IF NOT EXISTS evidence_records (
  evidence_id TEXT PRIMARY KEY, revision_id INTEGER REFERENCES source_revisions(id),
  page_number INTEGER, table_name TEXT, raw_text_snippet TEXT,
  extraction_method TEXT NOT NULL, confidence TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS programs (
  program_id TEXT PRIMARY KEY, school TEXT NOT NULL, college TEXT NOT NULL,
  major_code TEXT NOT NULL, major_name TEXT NOT NULL, degree_type TEXT NOT NULL,
  study_mode TEXT NOT NULL, research_direction TEXT, special_program TEXT,
  campus TEXT, admission_year INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS field_facts (
  id INTEGER PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
  field_path TEXT NOT NULL, admission_year INTEGER NOT NULL, value_json TEXT NOT NULL,
  unit TEXT, scope_json TEXT NOT NULL, derived INTEGER NOT NULL DEFAULT 0,
  calculation_formula TEXT, confidence TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fact_evidence (
  fact_id INTEGER NOT NULL REFERENCES field_facts(id),
  evidence_id TEXT NOT NULL REFERENCES evidence_records(evidence_id),
  role TEXT NOT NULL DEFAULT 'support', PRIMARY KEY(fact_id, evidence_id, role)
);
CREATE TABLE IF NOT EXISTS evidence_conflicts (
  conflict_id TEXT PRIMARY KEY, entity_id TEXT NOT NULL, field_path TEXT NOT NULL,
  admission_year INTEGER NOT NULL, status TEXT NOT NULL, resolution_json TEXT
);
CREATE TABLE IF NOT EXISTS data_quality_issues (
  id INTEGER PRIMARY KEY, code TEXT NOT NULL, severity TEXT NOT NULL,
  message TEXT NOT NULL, entity_id TEXT, field_path TEXT, resolved INTEGER NOT NULL DEFAULT 0
);
"""


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection
