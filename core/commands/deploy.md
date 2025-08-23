---
description: Execute comprehensive deployment using the deployment & DevOps framework
argument-hint: [project-path]
---

# Deployment & DevOps Framework Execution

## Initialize Deployment Framework

Use the comprehensive deployment framework from ~/.claude/process-templates-n-prompts/deployment/

### Step 1: Check for Existing Deployment Infrastructure
First, check if `.claude/deployment/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If deployment framework doesn't exist in the project:
```bash
mkdir -p .claude/deployment
cp ~/.claude/process-templates-n-prompts/deployment/*.md .claude/deployment/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read deployment-prompt.md** - Understand the deployment philosophy and DevOps practices
   - Focus on CI/CD pipeline design and infrastructure as code
   - Review containerization, orchestration, and scaling strategies
   - Understand blue-green, canary, and rolling deployment patterns

2. **Load deployment-template.md** - Use as the structure for deployment documentation
   - Reference for pipeline configuration templates
   - Use infrastructure provisioning templates
   - Follow deployment strategy templates
   - Use monitoring and rollback procedures

3. **Follow deployment-checklist.md** - Execute phases systematically
   - Start with Phase 0: Infrastructure Assessment & Planning
   - Check off items as completed
   - Document deployment configurations
   - Track deployment metrics and success rates

## Execution Instructions

### Phase 0: Infrastructure Assessment & Planning (MANDATORY FIRST)
- Assess current infrastructure and deployment processes
- Define deployment environments and promotion pipeline
- Document infrastructure requirements and constraints
- Map dependencies and integration points
- Review security and compliance requirements
- Establish deployment metrics and success criteria

### Subsequent Phases
Continue through all phases in order:
- Phase 1: CI/CD Pipeline Design & Implementation
- Phase 2: Infrastructure as Code & Provisioning
- Phase 3: Containerization & Orchestration
- Phase 4: Deployment Strategy & Automation
- Phase 5: Monitoring & Observability Setup
- Phase 6: Security & Compliance Integration
- Phase 7: Optimization & Continuous Improvement

## Key Principles

1. **ALWAYS automate deployment processes for consistency**
2. **Implement infrastructure as code for reproducibility**
3. **Design for rollback and disaster recovery**
4. **Monitor deployments and system health continuously**
5. **Secure the entire deployment pipeline**
6. **Test deployment processes in staging environments**

## Deployment Goals
- Fully automated CI/CD pipeline with quality gates
- Infrastructure as code with version control
- Zero-downtime deployment strategies
- Comprehensive monitoring and alerting
- Secure deployment with compliance validation
- Fast rollback and disaster recovery capabilities

## Progress Tracking
Update the deployment-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. cicd-pipeline.yml - Continuous integration and deployment configuration
2. infrastructure-code/ - Terraform/CloudFormation infrastructure definitions
3. deployment-strategies.md - Blue-green, canary, and rolling deployment guides
4. container-configuration/ - Docker and Kubernetes configurations
5. monitoring-setup.md - Deployment monitoring and alerting configuration
6. rollback-procedures.md - Emergency rollback and recovery procedures
7. security-compliance.md - Deployment security and compliance validation
8. CHANGELOG.md - Document all deployment changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Deployment is where code meets reality. Automate relentlessly, monitor continuously, prepare for failure, celebrate success.