# /verify-story Task

When this command is used, execute the following task:

# Verify Story Completion Task

## Purpose

To enforce binary completion verification for stories, ensuring only truly complete work passes. This task performs evidence-based verification with no allowance for partial completion or explanatory excuses.

## CRITICAL ENFORCEMENT RULES

- **BINARY DECISION**: Stories are either COMPLETE or INCOMPLETE (no partial credit)
- **NO EXCEPTIONS**: Cannot accept "good enough" or "mostly working"
- **EVIDENCE REQUIRED**: Must have concrete proof of functionality
- **VETO POWER**: This verification can block story completion

## SEQUENTIAL Task Execution (Do not proceed until current step is complete)

### 0. Load Story and Configuration

- Load the current story file being verified
- Load `.bmad-core/core-config.yaml` to check enforcement settings
- Verify `enforcement.completion_verification` is set to `mandatory`
- If story status is already "Complete", inform user it's already verified

### 1. DoD Checklist Verification

- Load and execute the story-dod-checklist
- **CRITICAL**: Count EVERY checkbox in the checklist
- **PASS CRITERIA**: 100% of items must be marked [x]
- **FAIL CONDITIONS**:
  - ANY item marked [ ] (unchecked)
  - ANY item marked [N/A] without explicit story justification
  - Missing checklist execution

### 2. Evidence Collection Verification

Check for documented evidence in the story file:

- **Test Results**:
  - Must have actual test execution logs
  - Must show 100% pass rate
  - Must include timestamp
  - Generic "tests pass" is NOT acceptable
  
- **Build Status**:
  - Must show successful build output
  - Zero errors and warnings
  - Must be from current implementation
  
- **Functionality Demo**:
  - Screenshots or detailed description of manual testing
  - Each acceptance criterion must be verified
  - Must demonstrate actual working functionality

### 3. Acceptance Criteria Verification

For EACH acceptance criterion in the story:

- Verify it has been explicitly tested
- Check for evidence of functionality
- Confirm no regression in existing features
- Validate edge cases are handled

### 4. Code Quality Verification

Review the File List and changes:

- **Security Issues**:
  - No hardcoded passwords or secrets
  - No exposed credentials in logs
  - Proper input validation
  
- **Implementation Completeness**:
  - All promised features implemented
  - No TODO or FIXME comments indicating incomplete work
  - No commented-out code suggesting unfinished features

### 5. Task Completion Verification

- ALL tasks in the story must be marked [x]
- ALL subtasks must be marked [x]
- File List must be complete and accurate
- Change Log must document all modifications

### 6. Performance Verification (if applicable)

If story has performance requirements:

- Response time metrics documented
- Load handling demonstrated
- Resource usage within limits
- Performance regression check

### 7. Generate Verification Decision

## DECISION MATRIX

### ✅ APPROVED - ALL of the following must be true:
- 100% of DoD checklist items marked [x]
- All tests passing with evidence
- All acceptance criteria verified working
- No critical security issues
- All tasks and subtasks complete
- Evidence documented for all claims
- Build successful with zero errors

### ❌ REJECTED - ANY of the following triggers rejection:
- Any DoD item unchecked [ ]
- Any test failing
- Any acceptance criteria not working
- Critical security issue found
- Incomplete tasks or subtasks
- Missing or insufficient evidence
- Build errors or warnings

## Verification Report Format

```markdown
## Verification Record

### Verification Status
**Status**: COMPLETE | INCOMPLETE
**Date**: [timestamp]
**Verified By**: completion-enforcer (Victoria)

### Verification Results
- DoD Checklist: [X/Y items checked]
- Test Results: PASS/FAIL
- Build Status: PASS/FAIL
- Acceptance Criteria: [X/Y verified]
- Evidence Review: SUFFICIENT/INSUFFICIENT

### Decision
**DECISION**: APPROVED | REJECTED

### Rejection Reason (if rejected)
[Specific reasons for rejection with required fixes]

### Evidence Summary
- Test Logs: [Reference or excerpt]
- Build Output: [Reference or excerpt]
- Functionality Demo: [Description or screenshots]
```

## Post-Verification Actions

### If APPROVED:
1. Update story Verification Record with approval
2. Allow story status change to "Ready for Review"
3. Log successful verification

### If REJECTED:
1. Update story Verification Record with rejection details
2. Keep story status as "In Progress"
3. Generate rejection report with specific fixes needed
4. Block any attempt to mark complete
5. Inform dev agent of required fixes

## Anti-Gaming Measures

- Reject generic evidence like "all tests pass"
- Require actual log output, not summaries
- Verify timestamps are current
- Check for copy-pasted evidence
- Validate evidence matches current implementation

Remember: The goal is ensuring quality delivery, not just checking boxes. Be thorough, be strict, but be fair.