# /verify-epic Task

When this command is used, execute the following task:

# Verify Epic Completion Task

## Purpose

To verify that an entire epic is truly complete by validating all constituent stories meet strict completion criteria. This task ensures epics cannot be marked complete with incomplete stories or missing deliverables.

## CRITICAL ENFORCEMENT RULES

- **ALL STORIES COMPLETE**: Every story in the epic must be verified complete
- **NO PARTIAL CREDIT**: Cannot mark epic complete with ANY incomplete stories
- **CASCADING VERIFICATION**: Each story must pass individual verification
- **EPIC-LEVEL VALIDATION**: Additional checks for epic coherence and completeness

## SEQUENTIAL Task Execution

### 0. Load Epic and Configuration

- Load the epic file being verified
- Load `.bmad-core/core-config.yaml` to check enforcement settings
- Identify all stories belonging to this epic
- Load epic success criteria and objectives

### 1. Story Verification Cascade

For EACH story in the epic:

- Check if story has Verification Record
- If no verification record:
  - Run verify-story task on that story
  - Collect verification result
- If verification record exists:
  - Validate it shows APPROVED status
  - Check verification is recent (not stale)

**FAIL FAST**: If ANY story fails verification, epic verification fails immediately

### 2. Epic Completion Metrics

Calculate and verify:

- **Story Completion Rate**: Must be 100%
- **Verified Stories**: Count of stories with APPROVED verification
- **Total Stories**: Total count of stories in epic
- **Required**: Verified Stories MUST equal Total Stories

### 3. Epic Success Criteria Verification

For each success criterion defined in the epic:

- Verify it has been addressed by completed stories
- Check for evidence across all stories
- Validate integration between story deliverables
- Ensure no gaps in functionality

### 4. Cross-Story Integration Verification

- **Feature Coherence**: Do all stories work together as intended?
- **No Gaps**: Are there missing features between stories?
- **Integration Points**: Are story boundaries properly integrated?
- **End-to-End Flow**: Does the complete epic deliver the promised value?

### 5. Epic-Level Documentation Verification

Check for required epic documentation:

- Architecture decisions documented
- API changes consolidated
- Database migrations complete
- Deployment instructions updated
- User documentation prepared

### 6. Technical Debt Assessment

Review across all stories for:

- Accumulated technical debt
- Unresolved TODO items
- Deferred fixes or improvements
- Security issues across stories

### 7. Performance and Scale Verification

If epic has performance requirements:

- Aggregate performance metrics from all stories
- Verify system-wide performance goals met
- Check for performance regression
- Validate scale requirements satisfied

## DECISION MATRIX

### ✅ EPIC APPROVED - ALL must be true:
- 100% of stories verified COMPLETE
- All epic success criteria met
- No integration gaps between stories
- Epic-level documentation complete
- No critical technical debt
- Performance requirements satisfied

### ❌ EPIC REJECTED - ANY triggers rejection:
- Any story verification failed
- Any story not verified
- Epic success criteria not met
- Integration issues between stories
- Missing epic documentation
- Unacceptable technical debt

## Epic Verification Report Format

```markdown
## Epic Verification Record

### Epic Details
**Epic**: [Epic ID and Title]
**Date**: [timestamp]
**Verified By**: completion-enforcer (Victoria)

### Story Verification Summary
Total Stories: X
Verified Complete: Y
Verification Failed: Z

### Detailed Story Status
- Story X.1: [Title] - APPROVED/REJECTED
- Story X.2: [Title] - APPROVED/REJECTED
- [Continue for all stories...]

### Epic Success Criteria
- [ ] Criterion 1: [Status and Evidence]
- [ ] Criterion 2: [Status and Evidence]
- [Continue for all criteria...]

### Integration Verification
- Feature Coherence: PASS/FAIL
- Integration Points: PASS/FAIL
- End-to-End Testing: PASS/FAIL

### Decision
**DECISION**: APPROVED | REJECTED

### Rejection Details (if rejected)
[Specific reasons with required fixes]

### Recommendations
[Any follow-up items or improvements needed]
```

## Post-Verification Actions

### If APPROVED:
1. Update epic with verification record
2. Mark epic as COMPLETE
3. Generate epic completion summary
4. Archive verification evidence

### If REJECTED:
1. Update epic with rejection details
2. Keep epic status as IN PROGRESS
3. Generate fix list for incomplete items
4. Block completion until issues resolved

## Special Considerations

### Partial Epic Delivery
- If business requests partial delivery, create new epic
- Cannot mark original epic complete with missing stories
- Document what was descoped and why

### Story Dependencies
- Verify stories were completed in correct order
- Check that dependent stories weren't completed prematurely
- Validate integration points between dependent stories

### Rollback Scenarios
- If a verified story later fails in production
- Epic verification may need to be revoked
- Document lessons learned for future verification

Remember: Epic verification is about ensuring the complete solution works as intended, not just that individual parts are done.