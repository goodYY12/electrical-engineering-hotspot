CREATE TABLE IF NOT EXISTS electrical_radar_snapshots (
  captured_at timestamptz NOT NULL,
  category text NOT NULL,
  heat numeric(5, 2) NOT NULL,
  article_count integer NOT NULL,
  avg_hot_score numeric(5, 2) NOT NULL,
  PRIMARY KEY (captured_at, category)
);
