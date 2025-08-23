---
description: Execute comprehensive incident response using the incident response framework
argument-hint: [project-path]
---

# Incident Response Framework Execution

## Initialize Incident Response Framework

Use the comprehensive incident response framework from ~/.claude/process-templates-n-prompts/incident-response/

### Step 1: Check for Existing Incident Response Infrastructure
First, check if `.claude/incident-response/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If incident response framework doesn't exist in the project:
```bash
mkdir -p .claude/incident-response
cp ~/.claude/process-templates-n-prompts/incident-response/*.md .claude/incident-response/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read incident-response-prompt.md** - Understand the incident response philosophy and methodology
   - Focus on rapid detection, containment, and recovery procedures
   - Review communication protocols and stakeholder management
   - Understand post-incident analysis and continuous improvement

2. **Load incident-response-template.md** - Use as the structure for incident documentation
   - Reference for incident classification and escalation templates
   - Use communication and status update templates
   - Follow post-mortem and root cause analysis templates
   - Use incident tracking and reporting formats

3. **Follow incident-response-checklist.md** - Execute phases systematically
   - Start with Phase 0: Incident Preparation & Planning
   - Check off items as completed
   - Document incident procedures and playbooks
   - Track incident metrics and response effectiveness

## Execution Instructions

### Phase 0: Incident Preparation & Planning (MANDATORY FIRST)
- Define incident classification and severity levels
- Establish incident response team roles and responsibilities
- Document escalation paths and communication protocols
- Create incident response playbooks for common scenarios
- Review monitoring and alerting for incident detection
- Set up incident tracking and communication tools

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Detection & Alert Management
- Phase 2: Incident Classification & Initial Response
- Phase 3: Containment & Damage Control
- Phase 4: Investigation & Root Cause Analysis
- Phase 5: Recovery & Service Restoration
- Phase 6: Post-Incident Review & Documentation
- Phase 7: Process Improvement & Prevention

## Key Principles

1. **ALWAYS prioritize service restoration over root cause analysis**
2. **Communicate early, often, and transparently with stakeholders**
3. **Document everything during the incident for later analysis**
4. **Follow established procedures but adapt to situation needs**
5. **Learn from every incident to prevent future occurrences**
6. **Practice incident response through regular drills and exercises**

## Incident Response Goals
- Rapid incident detection and response team mobilization
- Clear communication with all stakeholders during incidents
- Systematic containment and service restoration procedures
- Thorough post-incident analysis and improvement planning
- Comprehensive incident documentation and knowledge sharing
- Continuous improvement of incident response capabilities

## Progress Tracking
Update the incident-response-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. incident-response-plan.md - Comprehensive incident response procedures
2. escalation-matrix.md - Incident classification and escalation paths
3. communication-templates/ - Status update and stakeholder communication templates
4. incident-playbooks/ - Specific response procedures for common incident types
5. post-mortem-template.md - Standardized post-incident analysis format
6. incident-tracking.md - Incident logging and status tracking procedures
7. training-exercises.md - Incident response drills and training plans
8. CHANGELOG.md - Document all incident response improvements

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: When systems fail, people succeed. Prepare thoroughly, respond quickly, communicate clearly, learn continuously.