---
description: Execute comprehensive data pipeline development using the data pipeline framework
argument-hint: [project-path]
---

# Data Pipeline Framework Execution

## Initialize Data Pipeline Framework

Use the comprehensive data pipeline framework from ~/.claude/process-templates-n-prompts/data-pipeline/

### Step 1: Check for Existing Data Pipeline Infrastructure
First, check if `.claude/data-pipeline/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If data pipeline framework doesn't exist in the project:
```bash
mkdir -p .claude/data-pipeline
cp ~/.claude/process-templates-n-prompts/data-pipeline/*.md .claude/data-pipeline/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read data-pipeline-prompt.md** - Understand the data pipeline philosophy and best practices
   - Focus on data quality, lineage, and governance principles
   - Review ETL/ELT patterns, streaming, and batch processing strategies
   - Understand data security, privacy, and compliance requirements

2. **Load data-pipeline-template.md** - Use as the structure for pipeline documentation
   - Reference for data flow design templates
   - Use data quality validation templates
   - Follow pipeline orchestration and scheduling templates
   - Use monitoring and alerting configuration formats

3. **Follow data-pipeline-checklist.md** - Execute phases systematically
   - Start with Phase 0: Data Requirements & Architecture Planning
   - Check off items as completed
   - Document data transformations and quality rules
   - Track pipeline performance and data quality metrics

## Execution Instructions

### Phase 0: Data Requirements & Architecture Planning (MANDATORY FIRST)
- Define data sources, destinations, and transformation requirements
- Map data flow architecture and processing patterns
- Document data quality requirements and validation rules
- Identify data governance and compliance requirements
- Review existing data infrastructure and integration points
- Establish data SLAs and performance targets

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Data Ingestion & Source Integration
- Phase 2: Data Transformation & Processing Logic
- Phase 3: Data Quality Validation & Monitoring
- Phase 4: Pipeline Orchestration & Scheduling
- Phase 5: Data Storage & Output Management
- Phase 6: Monitoring & Alerting Implementation
- Phase 7: Performance Optimization & Scaling

## Key Principles

1. **ALWAYS validate data quality at every pipeline stage**
2. **Design for idempotency and fault tolerance**
3. **Implement comprehensive data lineage tracking**
4. **Secure data in transit and at rest**
5. **Monitor pipeline health and data freshness**
6. **Plan for schema evolution and backward compatibility**

## Data Pipeline Goals
- Reliable and scalable data ingestion from multiple sources
- Robust data transformation with quality validation
- Comprehensive monitoring and alerting for pipeline health
- Clear data lineage and governance documentation
- Efficient processing with optimal resource utilization
- Secure handling of sensitive data throughout the pipeline

## Progress Tracking
Update the data-pipeline-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. data-architecture.md - Overall data pipeline architecture and design
2. data-sources.md - Source system integrations and extraction logic
3. transformation-logic.md - Data transformation rules and business logic
4. data-quality-rules.md - Validation rules and quality monitoring
5. pipeline-orchestration.md - Workflow scheduling and dependency management
6. monitoring-setup.md - Pipeline monitoring, alerting, and observability
7. data-lineage.md - Data flow tracking and impact analysis documentation
8. CHANGELOG.md - Document all data pipeline changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Data pipelines are the circulatory system of modern applications. Build for reliability, monitor for quality, secure for trust, scale for growth.