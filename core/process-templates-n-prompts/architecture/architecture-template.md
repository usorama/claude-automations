# Architecture & System Design Templates

## 1. Architecture Decision Record (ADR) Template

```markdown
# ADR-[NUMBER]: [TITLE]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[Describe the issue or problem that needs to be addressed. Include relevant background information, constraints, and forces at play.]

## Decision
[State the architectural decision that has been made.]

## Consequences
### Positive
- [List positive outcomes]
- [Benefits gained]

### Negative
- [List negative outcomes]
- [Trade-offs accepted]

### Risks
- [Potential risks]
- [Mitigation strategies]

## Options Considered
### Option 1: [Name]
**Pros:**
- [Advantages]

**Cons:**
- [Disadvantages]

### Option 2: [Name]
**Pros:**
- [Advantages]

**Cons:**
- [Disadvantages]

## Related Decisions
- [ADR-XXX: Related decision]
- [ADR-YYY: Another related decision]

## References
- [Links to relevant documentation]
- [Articles, papers, or resources]

## Notes
[Any additional notes, implementation details, or follow-up actions]

**Date**: YYYY-MM-DD
**Author**: [Name]
**Reviewers**: [Names]
```

## 2. System Architecture Document Template

```markdown
# System Architecture Document

## 1. Executive Summary
[High-level overview of the system architecture in 2-3 paragraphs]

## 2. System Overview
### 2.1 Purpose
[System purpose and business value]

### 2.2 Scope
[What's included and excluded]

### 2.3 Goals and Objectives
- [Goal 1]
- [Goal 2]

## 3. Architectural Principles
- **Principle 1**: [Description]
- **Principle 2**: [Description]

## 4. System Context
### 4.1 External Systems
- [System A]: [Integration purpose]
- [System B]: [Integration purpose]

### 4.2 User Classes
- [User Type 1]: [Description and needs]
- [User Type 2]: [Description and needs]

## 5. Architecture Overview
### 5.1 High-Level Architecture
[Architecture diagram and description]

### 5.2 Architecture Style
[Microservices | Monolithic | Serverless | Event-Driven | etc.]

### 5.3 Key Components
| Component | Responsibility | Technology |
|-----------|---------------|------------|
| API Gateway | Request routing | Kong/Nginx |
| Auth Service | Authentication | OAuth2/JWT |
| Database | Data persistence | PostgreSQL |

## 6. Detailed Architecture
### 6.1 Component Architecture
[Detailed component diagrams and descriptions]

### 6.2 Data Architecture
[Data flow diagrams and schema design]

### 6.3 Deployment Architecture
[Infrastructure and deployment topology]

## 7. Technology Stack
### 7.1 Frontend
- Framework: [React/Vue/Angular]
- State Management: [Redux/MobX]
- Build Tools: [Webpack/Vite]

### 7.2 Backend
- Language: [Node.js/Python/Go]
- Framework: [Express/FastAPI/Gin]
- ORM: [Prisma/SQLAlchemy]

### 7.3 Infrastructure
- Cloud: [AWS/GCP/Azure]
- Containers: [Docker/Kubernetes]
- CI/CD: [GitHub Actions/Jenkins]

## 8. Quality Attributes
### 8.1 Performance
- Response Time: <200ms (P95)
- Throughput: 10,000 req/sec
- Concurrent Users: 100,000

### 8.2 Security
- Authentication: OAuth2
- Encryption: TLS 1.3
- Compliance: GDPR, SOC2

### 8.3 Scalability
- Horizontal Scaling: Auto-scaling groups
- Database: Read replicas
- Caching: Multi-layer

## 9. Risks and Mitigations
| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | High | High | [Strategy] |
| [Risk 2] | Medium | Low | [Strategy] |

## 10. Appendices
### A. Glossary
### B. References
### C. Change Log
```

## 3. API Design Template

```yaml
# api-specification.yaml
openapi: 3.0.0
info:
  title: System API
  version: 1.0.0
  description: API specification for the system
  contact:
    email: api@example.com

servers:
  - url: https://api.example.com/v1
    description: Production server
  - url: https://staging-api.example.com/v1
    description: Staging server

paths:
  /users:
    get:
      summary: List users
      operationId: listUsers
      tags:
        - Users
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  users:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '500':
          $ref: '#/components/responses/InternalError'
    
    post:
      summary: Create user
      operationId: createUser
      tags:
        - Users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - name
      properties:
        id:
          type: string
          format: uuid
        email:
          type: string
          format: email
        name:
          type: string
        createdAt:
          type: string
          format: date-time
    
    CreateUserRequest:
      type: object
      required:
        - email
        - name
        - password
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        password:
          type: string
          format: password
          minLength: 8
    
    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
        totalPages:
          type: integer
  
  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
                example: "Unauthorized"
    
    InternalError:
      description: Internal server error
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
                example: "Internal server error"
  
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - bearerAuth: []
```

## 4. Database Schema Template

```sql
-- database-schema.sql

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User-Organization relationship
CREATE TABLE user_organizations (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, organization_id)
);

-- Audit log table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Partitioning for audit logs (monthly)
CREATE TABLE audit_logs_2024_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Functions and triggers
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

## 5. Infrastructure as Code Template

```yaml
# infrastructure.yaml - Kubernetes deployment

apiVersion: v1
kind: Namespace
metadata:
  name: production

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: production
  labels:
    app: api-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
      - name: api
        image: myapp/api:1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis.url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: production
spec:
  selector:
    app: api-service
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-service-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 6. Terraform Infrastructure Template

```hcl
# main.tf - AWS infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "${var.project_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true
  enable_dns_hostnames = true

  tags = local.common_tags
}

# RDS Database
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-db"
  
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = var.db_instance_class
  
  allocated_storage     = 100
  storage_encrypted     = true
  storage_type         = "gp3"
  
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.database.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.project_name}-db-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  
  tags = local.common_tags
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = local.common_tags
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = module.vpc.public_subnets
  
  enable_deletion_protection = true
  enable_http2              = true
  
  tags = local.common_tags
}

# Auto Scaling Group
resource "aws_autoscaling_group" "app" {
  name                = "${var.project_name}-asg"
  vpc_zone_identifier = module.vpc.private_subnets
  
  min_size         = var.asg_min_size
  max_size         = var.asg_max_size
  desired_capacity = var.asg_desired_capacity
  
  health_check_type         = "ELB"
  health_check_grace_period = 300
  
  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }
  
  tag {
    key                 = "Name"
    value               = "${var.project_name}-instance"
    propagate_at_launch = true
  }
}
```

## 7. Docker Compose Development Environment

```yaml
# docker-compose.yml

version: '3.8'

services:
  # Application
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://user:password@postgres:5432/myapp
      - REDIS_URL=redis://redis:6379
    volumes:
      - .:/app
      - /app/node_modules
    depends_on:
      - postgres
      - redis
    networks:
      - app-network

  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=myapp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - app-network

  # Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

  # Message Queue
  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=admin
      - RABBITMQ_DEFAULT_PASS=admin
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - app-network

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - app-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
  prometheus_data:
  grafana_data:

networks:
  app-network:
    driver: bridge
```

## 8. CI/CD Pipeline Template

```yaml
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  ECR_REPOSITORY: myapp-api
  ECS_SERVICE: api-service
  ECS_CLUSTER: production-cluster

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run linting
        run: npm run lint
      
      - name: Security scan
        run: npm audit --audit-level=moderate

  build-and-push:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster ${{ env.ECS_CLUSTER }} \
            --service ${{ env.ECS_SERVICE }} \
            --force-new-deployment \
            --region ${{ env.AWS_REGION }}
      
      - name: Wait for deployment
        run: |
          aws ecs wait services-stable \
            --cluster ${{ env.ECS_CLUSTER }} \
            --services ${{ env.ECS_SERVICE }} \
            --region ${{ env.AWS_REGION }}
```

## 9. Monitoring Configuration Template

```yaml
# monitoring-config.yaml

# Prometheus configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'api-service'
    static_configs:
      - targets: ['api-service:8080']
    metrics_path: '/metrics'

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

# Alert rules
rule_files:
  - '/etc/prometheus/alerts.yml'

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

---
# alerts.yml
groups:
  - name: api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency detected
          description: "95th percentile latency is {{ $value }} seconds"

      - alert: LowDiskSpace
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: Low disk space
          description: "Less than 10% disk space remaining"
```

## 10. Architecture Review Checklist

```markdown
# Architecture Review Checklist

## General Architecture
- [ ] Architecture documented clearly
- [ ] Component responsibilities well-defined
- [ ] Dependencies mapped and minimized
- [ ] Technology choices justified
- [ ] Trade-offs documented

## Scalability
- [ ] Horizontal scaling supported
- [ ] Database scaling strategy defined
- [ ] Caching strategy implemented
- [ ] Load balancing configured
- [ ] Auto-scaling policies defined

## Security
- [ ] Authentication implemented
- [ ] Authorization model defined
- [ ] Data encryption at rest and transit
- [ ] Secrets management solution
- [ ] Security headers configured
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection

## Performance
- [ ] Performance targets defined
- [ ] Bottlenecks identified
- [ ] Caching implemented
- [ ] Database optimized
- [ ] CDN configured
- [ ] Compression enabled

## Reliability
- [ ] Health checks implemented
- [ ] Circuit breakers configured
- [ ] Retry logic implemented
- [ ] Graceful degradation planned
- [ ] Backup strategy defined
- [ ] Disaster recovery plan

## Observability
- [ ] Logging strategy defined
- [ ] Metrics collection implemented
- [ ] Distributed tracing configured
- [ ] Alerting rules defined
- [ ] Dashboards created
- [ ] Error tracking setup

## Operations
- [ ] CI/CD pipeline configured
- [ ] Infrastructure as code
- [ ] Environment parity maintained
- [ ] Rollback procedures defined
- [ ] Runbooks created
- [ ] On-call rotation planned

## Compliance
- [ ] Regulatory requirements met
- [ ] Data privacy ensured
- [ ] Audit logging implemented
- [ ] Compliance documentation
- [ ] Security certifications

## Documentation
- [ ] Architecture diagrams current
- [ ] API documentation complete
- [ ] Deployment guides written
- [ ] Troubleshooting guides available
- [ ] Onboarding documentation

## Team Readiness
- [ ] Team trained on architecture
- [ ] Responsibilities assigned
- [ ] Communication plan established
- [ ] Knowledge transfer completed
- [ ] Support processes defined
```