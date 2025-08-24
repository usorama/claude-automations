-- PRISM Intelligence Database Schema
-- Stores all learning data, metrics, and observability information

-- Agent context usage patterns
CREATE TABLE IF NOT EXISTS context_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT (datetime('now')),
    session_id TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    task_description TEXT,
    task_type TEXT,
    manifests_loaded TEXT,  -- JSON array
    manifests_used TEXT,    -- JSON array
    context_size_kb REAL,
    execution_time_ms INTEGER,
    success BOOLEAN,
    error_message TEXT
);

-- Context relevance scores
CREATE TABLE IF NOT EXISTS relevance_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT (datetime('now')),
    context_item TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    task_type TEXT,
    relevance_score REAL,
    was_used BOOLEAN,
    was_helpful BOOLEAN
);

-- Agent performance metrics
CREATE TABLE IF NOT EXISTS agent_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT (datetime('now')),
    agent_type TEXT NOT NULL,
    task_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_context_size_kb REAL,
    avg_execution_time_ms REAL,
    context_hit_rate REAL  -- % of loaded context actually used
);

-- System health and failures
CREATE TABLE IF NOT EXISTS system_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT (datetime('now')),
    component TEXT NOT NULL,
    status TEXT CHECK(status IN ('healthy', 'degraded', 'failed')),
    message TEXT,
    metrics TEXT  -- JSON object with component-specific metrics
);

-- Learning patterns
CREATE TABLE IF NOT EXISTS learning_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at DATETIME DEFAULT (datetime('now')),
    updated_at DATETIME DEFAULT (datetime('now')),
    pattern_type TEXT NOT NULL,
    pattern_data TEXT NOT NULL,  -- JSON object
    confidence REAL DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0
);

-- Alerts and notifications
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT (datetime('now')),
    severity TEXT CHECK(severity IN ('info', 'warning', 'error', 'critical')),
    component TEXT NOT NULL,
    message TEXT NOT NULL,
    details TEXT,  -- JSON object
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at DATETIME,
    resolution TEXT
);

-- Cross-repository intelligence
CREATE TABLE IF NOT EXISTS repository_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    pattern_value TEXT NOT NULL,
    frequency INTEGER DEFAULT 1,
    last_seen DATETIME DEFAULT (datetime('now')),
    confidence REAL DEFAULT 0.5
);

-- Observable metrics summary (for dashboard)
CREATE VIEW IF NOT EXISTS dashboard_metrics AS
SELECT 
    DATE(timestamp) as date,
    COUNT(DISTINCT session_id) as total_sessions,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_tasks,
    AVG(context_size_kb) as avg_context_size,
    AVG(execution_time_ms) as avg_execution_time,
    (SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
FROM context_usage
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Recent failures view (for immediate attention)
CREATE VIEW IF NOT EXISTS recent_failures AS
SELECT 
    cu.timestamp,
    cu.agent_type,
    cu.task_description,
    cu.error_message,
    a.severity,
    a.message as alert_message
FROM context_usage cu
LEFT JOIN alerts a ON a.timestamp = cu.timestamp
WHERE cu.success = 0
ORDER BY cu.timestamp DESC
LIMIT 10;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_context_usage_agent_type ON context_usage(agent_type);
CREATE INDEX IF NOT EXISTS idx_context_usage_timestamp ON context_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_context_usage_success ON context_usage(success);
CREATE INDEX IF NOT EXISTS idx_relevance_scores_context_item ON relevance_scores(context_item);
CREATE INDEX IF NOT EXISTS idx_relevance_scores_score ON relevance_scores(relevance_score);
CREATE INDEX IF NOT EXISTS idx_system_health_status ON system_health(status);
CREATE INDEX IF NOT EXISTS idx_system_health_component ON system_health(component);
CREATE INDEX IF NOT EXISTS idx_learning_patterns_type ON learning_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_learning_patterns_confidence ON learning_patterns(confidence);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(acknowledged);