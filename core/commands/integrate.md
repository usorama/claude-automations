---
description: Execute comprehensive system integration using the integration framework
argument-hint: [project-path]
---

# Integration Framework Execution

## Initialize Integration Framework

Use the comprehensive integration framework from ~/.claude/process-templates-n-prompts/integrations/

### Step 1: Check for Existing Integration Infrastructure
First, check if `.claude/integrations/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If integration framework doesn't exist in the project:
```bash
mkdir -p .claude/integrations
cp ~/.claude/process-templates-n-prompts/integrations/*.md .claude/integrations/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read integrations-prompt.md** - Understand the integration philosophy and patterns
   - Focus on loose coupling, fault tolerance, and data consistency
   - Review synchronous vs asynchronous integration patterns
   - Understand API versioning, contract testing, and backward compatibility

2. **Load integrations-template.md** - Use as the structure for integration documentation
   - Reference for integration architecture templates
   - Use API contract and interface definition templates
   - Follow testing and validation templates
   - Use monitoring and error handling formats

3. **Follow integrations-checklist.md** - Execute phases systematically
   - Start with Phase 0: Integration Planning & Architecture
   - Check off items as completed
   - Document integration contracts and interfaces
   - Track integration health and performance metrics

## Execution Instructions

### Phase 0: Integration Planning & Architecture (MANDATORY FIRST)
- Map current system landscape and integration points
- Define integration requirements and data flow patterns
- Choose appropriate integration patterns and technologies
- Document API contracts and interface specifications
- Plan for error handling, retries, and circuit breakers
- Establish integration testing and validation strategies

### Subsequent Phases
Continue through all phases in order:
- Phase 1: API Design & Contract Definition
- Phase 2: Integration Implementation & Development
- Phase 3: Data Mapping & Transformation Logic
- Phase 4: Error Handling & Resilience Patterns
- Phase 5: Testing & Contract Validation
- Phase 6: Monitoring & Observability Setup
- Phase 7: Performance Optimization & Scaling

## Key Principles

1. **ALWAYS design for loose coupling and high cohesion**
2. **Implement comprehensive error handling and retry logic**
3. **Use circuit breakers and bulkheads for fault isolation**
4. **Design APIs with versioning and backward compatibility**
5. **Test integration contracts continuously**
6. **Monitor integration health and performance metrics**

## Integration Goals
- Loose coupling between systems with clear boundaries
- Reliable data exchange with error handling and recovery
- API-first design with versioning and documentation
- Comprehensive testing including contract validation
- Resilient integration patterns with fault tolerance
- Real-time monitoring and alerting for integration health

## Progress Tracking
Update the integrations-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. integration-architecture.md - System integration design and patterns
2. api-contracts/ - API specifications and interface definitions
3. data-mapping.md - Data transformation and mapping documentation
4. error-handling.md - Integration error handling and recovery procedures
5. testing-strategy.md - Integration testing approach and contract validation
6. monitoring-setup.md - Integration health monitoring and alerting
7. performance-optimization.md - Integration performance tuning and scaling
8. CHANGELOG.md - Document all integration changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Great integrations are invisible when they work and resilient when they don't. Design for failure, test the contracts, monitor the flows, optimize for scale.