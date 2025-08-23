---
description: Execute comprehensive database design using the database framework
argument-hint: [project-path]
---

# Database Design Framework Execution

## Initialize Database Framework

Use the comprehensive database framework from ~/.claude/process-templates-n-prompts/database/

### Step 1: Check for Existing Database Infrastructure
First, check if `.claude/database/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If database framework doesn't exist in the project:
```bash
mkdir -p .claude/database
cp ~/.claude/process-templates-n-prompts/database/*.md .claude/database/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read database-prompt.md** - Understand the database design philosophy and principles
   - Focus on data modeling, normalization, and performance optimization
   - Review ACID properties, consistency, and transaction management
   - Understand backup, recovery, and disaster planning strategies

2. **Load database-template.md** - Use as the structure for database documentation
   - Reference for schema design structures
   - Use entity relationship modeling templates
   - Follow migration and versioning templates
   - Use performance tuning documentation formats

3. **Follow database-checklist.md** - Execute phases systematically
   - Start with Phase 0: Data Requirements & Analysis
   - Check off items as completed
   - Document database schemas and relationships
   - Track performance and optimization metrics

## Execution Instructions

### Phase 0: Data Requirements & Analysis (MANDATORY FIRST)
- Analyze data requirements and business rules
- Identify entities, relationships, and constraints
- Document data flow and access patterns
- Map existing data sources and integration points
- Review compliance and data governance requirements
- Establish performance and scalability targets

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Database Design & Modeling
- Phase 2: Schema Implementation & Migration
- Phase 3: Performance Optimization & Indexing
- Phase 4: Security & Access Control
- Phase 5: Backup & Recovery Planning
- Phase 6: Monitoring & Maintenance
- Phase 7: Scaling & Evolution Planning

## Key Principles

1. **ALWAYS normalize to eliminate redundancy and ensure integrity**
2. **Design for performance with appropriate indexing strategies**
3. **Implement comprehensive backup and recovery procedures**
4. **Secure data with proper access controls and encryption**
5. **Plan for scalability and future growth**
6. **Monitor performance and optimize continuously**

## Database Goals
- Normalized schema design with clear relationships
- Optimized performance with strategic indexing
- Robust backup and disaster recovery procedures
- Secure access controls and data encryption
- Scalable architecture for growth
- Comprehensive monitoring and alerting

## Progress Tracking
Update the database-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. database-schema.sql - Complete database schema definition
2. entity-relationship-diagram.md - ERD with relationship documentation
3. migration-scripts/ - Database migration and versioning scripts
4. performance-optimization.md - Indexing and query optimization guide
5. security-configuration.md - Access control and encryption setup
6. backup-recovery-plan.md - Backup and disaster recovery procedures
7. monitoring-setup.md - Database monitoring and alerting configuration
8. CHANGELOG.md - Document all database changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Data is your most valuable asset. Design with integrity, optimize for performance, secure comprehensively, backup religiously.