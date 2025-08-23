---
description: Execute comprehensive monitoring using the monitoring & observability framework
argument-hint: [project-path]
---

# Monitoring & Observability Framework Execution

## Initialize Monitoring Framework

Use the comprehensive monitoring framework from ~/.claude/process-templates-n-prompts/monitoring/

### Step 1: Check for Existing Monitoring Infrastructure
First, check if `.claude/monitoring/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If monitoring framework doesn't exist in the project:
```bash
mkdir -p .claude/monitoring
cp ~/.claude/process-templates-n-prompts/monitoring/*.md .claude/monitoring/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read monitoring-prompt.md** - Understand the monitoring philosophy and observability practices
   - Focus on the three pillars: metrics, logs, and traces
   - Review SLI/SLO definition and alerting strategies
   - Understand monitoring stack design and tool integration

2. **Load monitoring-template.md** - Use as the structure for monitoring documentation
   - Reference for dashboard configuration templates
   - Use alert rule and notification templates
   - Follow observability implementation templates
   - Use incident response integration formats

3. **Follow monitoring-checklist.md** - Execute phases systematically
   - Start with Phase 0: Monitoring Requirements & Assessment
   - Check off items as completed
   - Document monitoring configurations
   - Track system health and alert effectiveness metrics

## Execution Instructions

### Phase 0: Monitoring Requirements & Assessment (MANDATORY FIRST)
- Define monitoring objectives and success criteria
- Identify critical system components and dependencies
- Document current monitoring gaps and blind spots
- Map user journeys and business-critical paths
- Review existing monitoring tools and data sources
- Establish SLIs, SLOs, and error budgets

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Metrics Collection & Instrumentation
- Phase 2: Logging Strategy & Implementation
- Phase 3: Distributed Tracing Setup
- Phase 4: Dashboard Design & Visualization
- Phase 5: Alerting & Notification Configuration
- Phase 6: Incident Response Integration
- Phase 7: Monitoring Optimization & Maintenance

## Key Principles

1. **ALWAYS monitor what matters to users and business**
2. **Implement the three pillars: metrics, logs, and traces**
3. **Set up proactive alerting based on SLI/SLO thresholds**
4. **Design dashboards for different audiences and scenarios**
5. **Integrate monitoring with incident response workflows**
6. **Continuously optimize based on alert fatigue and effectiveness**

## Monitoring Goals
- Comprehensive visibility into system health and performance
- Proactive alerting with minimal false positives
- Rich dashboards for different stakeholder needs
- Distributed tracing for complex system debugging
- Integration with incident response and on-call procedures
- Continuous monitoring optimization and noise reduction

## Progress Tracking
Update the monitoring-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. monitoring-strategy.md - Overall monitoring approach and objectives
2. metrics-collection.md - Instrumentation and metrics configuration
3. logging-configuration.md - Log collection, parsing, and retention setup
4. tracing-implementation.md - Distributed tracing setup and configuration
5. dashboard-designs/ - Monitoring dashboards for different audiences
6. alert-rules.md - Alert conditions, thresholds, and notification routing
7. incident-integration.md - Monitoring integration with incident response
8. CHANGELOG.md - Document all monitoring changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: You can't improve what you don't measure, and you can't fix what you can't see. Monitor comprehensively, alert intelligently, respond quickly.