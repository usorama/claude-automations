# Universal Production Readiness Checklist

## 🚦 Pre-Flight Checks (Before First Deploy)

### Configuration & Secrets
- [ ] All environment variables documented in `.env.example`
- [ ] No secrets hardcoded in source code
- [ ] Secrets management system configured (Vault, AWS Secrets Manager, etc.)
- [ ] Configuration validation runs at startup
- [ ] App fails to start if required config missing
- [ ] Different configs for dev/staging/production

### Dependency Management
- [ ] All critical dependencies identified and documented
- [ ] Startup validation for required services
- [ ] Graceful degradation for optional services
- [ ] No mock/stub code in production paths
- [ ] Dependency health checks implemented
- [ ] Connection retry logic with exponential backoff

### Error Handling
- [ ] No empty catch blocks
- [ ] All errors logged with context
- [ ] Error tracking service configured (Sentry, Rollbar, etc.)
- [ ] Custom error types for different scenarios
- [ ] User-friendly error messages
- [ ] No sensitive data in error messages

## 🔍 Observability

### Logging
- [ ] Structured logging implemented (JSON format)
- [ ] Log levels properly used (ERROR, WARN, INFO, DEBUG)
- [ ] Correlation IDs for request tracing
- [ ] No sensitive data in logs (PII, passwords, tokens)
- [ ] Log retention policy defined
- [ ] Centralized log aggregation configured

### Monitoring
- [ ] Application metrics exposed (`/metrics` endpoint)
- [ ] Key business metrics tracked
- [ ] Performance metrics (response time, throughput)
- [ ] Error rate monitoring
- [ ] Custom dashboards created
- [ ] SLIs and SLOs defined

### Health Checks
- [ ] `/health` endpoint returns accurate status
- [ ] `/ready` endpoint for container orchestration
- [ ] Individual service health checks
- [ ] Health check includes dependency status
- [ ] Degraded state properly reported
- [ ] Health check doesn't perform heavy operations

### Alerting
- [ ] Critical alerts configured (service down, high error rate)
- [ ] Warning alerts for degraded performance
- [ ] Alert fatigue prevention (proper thresholds)
- [ ] Escalation policy defined
- [ ] On-call rotation established
- [ ] Runbooks linked to alerts

## 🛡️ Reliability

### Circuit Breakers
- [ ] Circuit breakers on all external calls
- [ ] Configurable thresholds and timeouts
- [ ] Circuit state exposed in metrics
- [ ] Fallback behavior documented
- [ ] Testing of circuit breaker triggers

### Timeouts & Retries
- [ ] Timeouts on all network calls
- [ ] Retry logic with exponential backoff
- [ ] Maximum retry limits configured
- [ ] Idempotency keys for critical operations
- [ ] Dead letter queues for failed messages

### Rate Limiting
- [ ] API rate limiting implemented
- [ ] Per-user/per-IP limits configured
- [ ] Rate limit headers in responses
- [ ] Graceful handling of rate limit exceeded
- [ ] Rate limit metrics tracked

### Caching
- [ ] Cache strategy documented
- [ ] Cache invalidation logic implemented
- [ ] Cache metrics (hit/miss ratio)
- [ ] Cache failure handling
- [ ] TTL appropriately configured

## 🔐 Security

### Authentication & Authorization
- [ ] Authentication required for protected endpoints
- [ ] Authorization checks at service boundaries
- [ ] JWT/Session expiry handled properly
- [ ] Refresh token rotation implemented
- [ ] Account lockout after failed attempts

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] TLS/SSL for data in transit
- [ ] PII handling documented
- [ ] Data retention policies implemented
- [ ] GDPR/compliance requirements met

### Security Headers
- [ ] CSP (Content Security Policy) configured
- [ ] CORS properly configured
- [ ] Security headers (HSTS, X-Frame-Options, etc.)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention

### Vulnerability Management
- [ ] Dependency scanning in CI/CD
- [ ] Container image scanning
- [ ] Security testing in pipeline
- [ ] Penetration testing completed
- [ ] Security incident response plan

## 🚀 Performance

### Load Testing
- [ ] Load tests simulating expected traffic
- [ ] Stress tests to find breaking point
- [ ] Performance benchmarks established
- [ ] Database query optimization completed
- [ ] N+1 query problems resolved

### Resource Management
- [ ] Memory leaks tested and fixed
- [ ] Connection pooling configured
- [ ] File handles properly closed
- [ ] Background job processing optimized
- [ ] Garbage collection tuned (if applicable)

### Scalability
- [ ] Horizontal scaling tested
- [ ] Database can handle expected load
- [ ] Caching strategy for high traffic
- [ ] CDN configured for static assets
- [ ] Auto-scaling policies configured

## 📦 Deployment

### CI/CD Pipeline
- [ ] Automated builds on commit
- [ ] All tests run in pipeline
- [ ] Security scanning integrated
- [ ] Deployment to staging automatic
- [ ] Production deployment gated
- [ ] Rollback procedure tested

### Database
- [ ] Migration strategy defined
- [ ] Rollback scripts prepared
- [ ] Database backups automated
- [ ] Point-in-time recovery tested
- [ ] Connection pooling configured

### Infrastructure
- [ ] Infrastructure as Code (Terraform, CloudFormation)
- [ ] Disaster recovery plan documented
- [ ] Multi-region deployment (if required)
- [ ] Load balancer health checks
- [ ] SSL certificates auto-renewal

## 📊 Data Management

### Backup & Recovery
- [ ] Automated backups scheduled
- [ ] Backup retention policy defined
- [ ] Recovery procedures documented
- [ ] Recovery time objective (RTO) met
- [ ] Recovery point objective (RPO) met

### Data Quality
- [ ] Data validation at ingestion
- [ ] Data consistency checks
- [ ] Orphaned data cleanup jobs
- [ ] Archive strategy for old data
- [ ] Data export capabilities

## 👥 Team Readiness

### Documentation
- [ ] API documentation complete
- [ ] Architecture diagrams updated
- [ ] Runbooks for common issues
- [ ] Deployment guide written
- [ ] Configuration documentation

### Training
- [ ] Team trained on monitoring tools
- [ ] Incident response training completed
- [ ] On-call responsibilities clear
- [ ] Knowledge transfer sessions done
- [ ] New team member onboarding guide

### Support
- [ ] Support ticket system integrated
- [ ] Escalation path defined
- [ ] SLA commitments documented
- [ ] Customer communication plan
- [ ] Status page configured

## ✅ Final Validation

### Smoke Tests
- [ ] Critical user journeys tested
- [ ] API endpoint availability verified
- [ ] Database connectivity confirmed
- [ ] External service integration tested
- [ ] UI rendering correctly

### Compliance
- [ ] Security audit completed
- [ ] Compliance requirements verified
- [ ] Privacy policy updated
- [ ] Terms of service reviewed
- [ ] Accessibility standards met (WCAG)

### Go/No-Go Decision
- [ ] All P0 items completed
- [ ] Rollback plan ready
- [ ] Communication plan prepared
- [ ] Stakeholder approval obtained
- [ ] Launch window scheduled

## 🔄 Post-Launch

### Day 1
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify all alerts working
- [ ] Confirm backups running
- [ ] Review user feedback

### Week 1
- [ ] Analyze usage patterns
- [ ] Performance optimization based on data
- [ ] Address any critical issues
- [ ] Update documentation based on findings
- [ ] Team retrospective conducted

### Month 1
- [ ] Full security review
- [ ] Cost optimization analysis
- [ ] Capacity planning review
- [ ] Process improvements identified
- [ ] Roadmap updated based on learnings

## 🎯 Success Metrics

Define and track:
- **Availability**: Target uptime (e.g., 99.9%)
- **Performance**: P50, P95, P99 latencies
- **Error Rate**: Acceptable error threshold
- **User Satisfaction**: NPS, support tickets
- **Business Metrics**: Conversion, retention

## 🚨 Red Flags

Never go to production with:
- [ ] Hardcoded secrets
- [ ] No error tracking
- [ ] No health checks
- [ ] Mock data in production code
- [ ] No backup strategy
- [ ] Single points of failure
- [ ] No monitoring/alerting
- [ ] Untested rollback procedure
- [ ] No runbooks
- [ ] Team not trained

---

**Remember**: This checklist should be customized for your specific application, technology stack, and business requirements. Not all items may apply to every project, but each should be consciously considered and decided upon.