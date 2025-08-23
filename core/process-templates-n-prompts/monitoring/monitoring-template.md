# Monitoring & Observability Templates

## 1. Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    environment: 'prod'

rule_files:
  - "alert_rules.yml"
  - "recording_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'application'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - default
            - production
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__

  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
        - https://api.example.com/health
        - https://example.com
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

## 2. Alert Rules Configuration

```yaml
# alert_rules.yml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          (
            rate(http_requests_total{status=~"5.."}[5m]) /
            rate(http_requests_total[5m])
          ) * 100 > 5
        for: 5m
        labels:
          severity: critical
          service: "{{ $labels.service }}"
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% for service {{ $labels.service }}"
          runbook: "https://runbooks.example.com/high-error-rate"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 0.5
        for: 10m
        labels:
          severity: warning
          service: "{{ $labels.service }}"
        annotations:
          summary: "High latency detected"
          description: "95th percentile latency is {{ $value }}s for {{ $labels.service }}"

      - alert: DatabaseConnectionsHigh
        expr: |
          pg_stat_activity_count / pg_settings_max_connections * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connections usage high"
          description: "Database connections usage is {{ $value }}%"

      - alert: DiskSpaceHigh
        expr: |
          (1 - node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk space usage high"
          description: "Disk usage is {{ $value }}% on {{ $labels.instance }}"

  - name: infrastructure_alerts
    rules:
      - alert: NodeDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Node is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"

      - alert: HighCPUUsage
        expr: |
          100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}% on {{ $labels.instance }}"

      - alert: HighMemoryUsage
        expr: |
          (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}% on {{ $labels.instance }}"

  - name: slo_alerts
    rules:
      - alert: SLOBudgetBurn
        expr: |
          (
            slo_error_budget_remaining{slo="api-availability"} / 
            slo_error_budget_total{slo="api-availability"}
          ) < 0.1
        labels:
          severity: critical
          slo: "{{ $labels.slo }}"
        annotations:
          summary: "SLO error budget nearly exhausted"
          description: "Only {{ $value }}% of error budget remaining for {{ $labels.slo }}"
```

## 3. Grafana Dashboard JSON

```json
{
  "dashboard": {
    "id": null,
    "title": "Application Performance Dashboard",
    "tags": ["application", "performance"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ method }} {{ status }}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec",
            "min": 0
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "99th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "Seconds",
            "min": 0
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %"
          }
        ],
        "valueName": "current",
        "format": "percent",
        "thresholds": "5,10",
        "colorBackground": true,
        "gridPos": {
          "h": 4,
          "w": 6,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 4,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_activity_count",
            "legendFormat": "Active Connections"
          },
          {
            "expr": "pg_settings_max_connections",
            "legendFormat": "Max Connections"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 12
        }
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## 4. Application Instrumentation (Node.js)

```javascript
// monitoring.js
const promClient = require('prom-client');
const express = require('express');

// Create a Registry to register the metrics
const register = new promClient.Registry();

// Add default metrics
promClient.collectDefaultMetrics({
  app: 'your-app',
  prefix: 'nodejs_',
  timeout: 10000,
  gcDurationBuckets: [0.001, 0.01, 0.1, 1, 2, 5],
  register
});

// Custom metrics
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code', 'status_class'],
  registers: [register]
});

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
  registers: [register]
});

const activeConnections = new promClient.Gauge({
  name: 'active_connections_total',
  help: 'Total number of active connections',
  registers: [register]
});

const businessMetrics = new promClient.Counter({
  name: 'business_events_total',
  help: 'Total number of business events',
  labelNames: ['event_type', 'user_type'],
  registers: [register]
});

// Middleware for request metrics
const metricsMiddleware = (req, res, next) => {
  const start = Date.now();
  
  // Increment active connections
  activeConnections.inc();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const route = req.route ? req.route.path : req.url;
    const statusClass = `${Math.floor(res.statusCode / 100)}xx`;
    
    // Record metrics
    httpRequestsTotal
      .labels(req.method, route, res.statusCode, statusClass)
      .inc();
    
    httpRequestDuration
      .labels(req.method, route, res.statusCode)
      .observe(duration);
    
    // Decrement active connections
    activeConnections.dec();
  });
  
  next();
};

// Business metrics helper
const trackBusinessEvent = (eventType, userType = 'unknown') => {
  businessMetrics.labels(eventType, userType).inc();
};

// Health check with metrics
const healthCheck = (req, res) => {
  const healthStatus = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    version: process.env.APP_VERSION || 'unknown'
  };
  
  res.status(200).json(healthStatus);
};

// Metrics endpoint
const metricsEndpoint = async (req, res) => {
  try {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  } catch (error) {
    res.status(500).end(error);
  }
};

module.exports = {
  register,
  metricsMiddleware,
  trackBusinessEvent,
  healthCheck,
  metricsEndpoint,
  metrics: {
    httpRequestsTotal,
    httpRequestDuration,
    activeConnections,
    businessMetrics
  }
};
```

## 5. Logging Configuration

```javascript
// logger.js
const winston = require('winston');
const { ElasticsearchTransport } = require('winston-elasticsearch');

// Define log format
const logFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.printf(({ timestamp, level, message, stack, ...meta }) => {
    return JSON.stringify({
      timestamp,
      level,
      message,
      stack,
      ...meta,
      service: process.env.SERVICE_NAME || 'unknown',
      version: process.env.APP_VERSION || 'unknown',
      environment: process.env.NODE_ENV || 'development'
    });
  })
);

// Create logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: logFormat,
  defaultMeta: {
    service: process.env.SERVICE_NAME || 'your-app'
  },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error'
    }),
    new winston.transports.File({
      filename: 'logs/combined.log'
    })
  ]
});

// Add Elasticsearch transport in production
if (process.env.NODE_ENV === 'production') {
  logger.add(new ElasticsearchTransport({
    level: 'info',
    clientOpts: {
      node: process.env.ELASTICSEARCH_URL || 'http://localhost:9200'
    },
    index: 'application-logs'
  }));
}

// Request logging middleware
const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    const logData = {
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      userId: req.user?.id,
      traceId: req.headers['x-trace-id']
    };
    
    if (res.statusCode >= 400) {
      logger.warn('HTTP Request Error', logData);
    } else {
      logger.info('HTTP Request', logData);
    }
  });
  
  next();
};

// Error logging
const logError = (error, context = {}) => {
  logger.error('Application Error', {
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack
    },
    ...context
  });
};

// Business event logging
const logBusinessEvent = (event, data = {}) => {
  logger.info('Business Event', {
    event,
    ...data,
    category: 'business'
  });
};

// Security event logging
const logSecurityEvent = (event, severity = 'medium', data = {}) => {
  logger.warn('Security Event', {
    event,
    severity,
    ...data,
    category: 'security'
  });
};

module.exports = {
  logger,
  requestLogger,
  logError,
  logBusinessEvent,
  logSecurityEvent
};
```

## 6. SLO/SLI Configuration

```yaml
# slo-config.yaml
slos:
  - name: api-availability
    description: "API service availability"
    service: api-service
    sli:
      type: availability
      query: |
        rate(http_requests_total{status!~"5.."}[5m]) /
        rate(http_requests_total[5m])
    objectives:
      - target: 0.999  # 99.9%
        window: 30d
      - target: 0.995  # 99.5%
        window: 7d
    error_budget_policy:
      - burn_rate: 14.4
        window: 1h
        action: page
      - burn_rate: 6
        window: 6h
        action: ticket

  - name: api-latency
    description: "API response time SLO"
    service: api-service
    sli:
      type: latency
      query: |
        histogram_quantile(0.95,
          rate(http_request_duration_seconds_bucket[5m])
        )
    objectives:
      - target: 0.5    # 500ms
        window: 30d
      - target: 0.2    # 200ms
        window: 7d

  - name: data-freshness
    description: "Data pipeline freshness"
    service: data-pipeline
    sli:
      type: freshness
      query: |
        time() - last_successful_pipeline_run_timestamp
    objectives:
      - target: 3600   # 1 hour
        window: 24h
```