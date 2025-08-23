---
description: Execute comprehensive security assessment using the security & compliance framework
argument-hint: [project-path]
---

# Security & Compliance Framework Execution

## Initialize Security Framework

Use the comprehensive security framework from ~/.claude/process-templates-n-prompts/security/

### Step 1: Check for Existing Security Infrastructure
First, check if `.claude/security/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If security framework doesn't exist in the project:
```bash
mkdir -p .claude/security
cp ~/.claude/process-templates-n-prompts/security/*.md .claude/security/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read security-prompt.md** - Understand the security philosophy and threat modeling approach
   - Focus on defense-in-depth strategies and security by design
   - Review compliance requirements and regulatory frameworks
   - Understand security testing and vulnerability assessment methods

2. **Load security-template.md** - Use as the structure for security documentation
   - Reference for security control implementations
   - Use security assessment templates
   - Follow threat modeling frameworks
   - Use compliance documentation formats

3. **Follow security-checklist.md** - Execute phases systematically
   - Start with Phase 0: Security Assessment & Threat Modeling
   - Check off items as completed
   - Document security controls and mitigations
   - Track security metrics and compliance status

## Execution Instructions

### Phase 0: Security Assessment & Threat Modeling (MANDATORY FIRST)
- Identify assets, threats, and attack vectors
- Assess current security posture and vulnerabilities
- Document security requirements and compliance needs
- Map data flows and trust boundaries
- Review existing security controls and policies
- Establish security baselines and risk tolerance

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Security Architecture & Design
- Phase 2: Authentication & Authorization Implementation
- Phase 3: Data Protection & Privacy Controls
- Phase 4: Security Testing & Vulnerability Assessment
- Phase 5: Incident Response & Recovery Planning
- Phase 6: Compliance & Audit Preparation
- Phase 7: Security Monitoring & Continuous Improvement

## Key Principles

1. **ALWAYS assume breach and plan defense in depth**
2. **Implement security by design, not as an afterthought**
3. **Follow principle of least privilege and zero trust**
4. **Encrypt data in transit and at rest**
5. **Validate and sanitize all inputs and outputs**
6. **Monitor, log, and alert on security events**

## Security Goals
- Comprehensive threat model with risk assessment
- Strong authentication and authorization controls
- Data protection and privacy compliance
- Vulnerability management and patch process
- Incident response and business continuity plans
- Security monitoring and alerting systems

## Progress Tracking
Update the security-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. threat-model.md - Comprehensive threat analysis
2. security-controls.md - Implemented security measures
3. auth-implementation.md - Authentication and authorization details
4. data-protection.md - Data privacy and protection controls
5. vulnerability-assessment.md - Security testing results
6. incident-response-plan.md - Security incident procedures
7. compliance-report.md - Regulatory compliance status
8. CHANGELOG.md - Document all security changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Security is not a product but a process. Build secure, test thoroughly, monitor continuously, respond quickly.