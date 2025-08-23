# /rejection-report Task

When this command is used, execute the following task:

# Generate Rejection Report Task

## Purpose

To create a detailed, actionable report when a story or epic fails completion verification. This report provides specific guidance on what needs to be fixed before the work can be marked complete.

## Report Objectives

- **Clarity**: Make it crystal clear why verification failed
- **Actionability**: Provide specific steps to fix each issue
- **Priority**: Indicate which issues are blocking vs nice-to-have
- **Evidence**: Show exactly what was checked and what failed

## SEQUENTIAL Report Generation

### 1. Gather Verification Context

- Load the story/epic that failed verification
- Collect all verification check results
- Identify specific failure points
- Note any partial successes for context

### 2. Categorize Issues

Organize failures into categories:

#### 🚨 BLOCKING ISSUES (Must Fix)
- Unchecked DoD items
- Failing tests
- Missing acceptance criteria
- Security vulnerabilities
- Build failures

#### ⚠️ CRITICAL ISSUES (Should Fix)
- Insufficient evidence
- Missing documentation
- Integration problems
- Performance issues

#### 💡 IMPROVEMENTS (Nice to Have)
- Code quality suggestions
- Additional test coverage
- Documentation enhancements

### 3. Generate Fix Instructions

For EACH issue identified:

```markdown
### Issue: [Clear issue title]
**Category**: BLOCKING | CRITICAL | IMPROVEMENT
**Component**: [Where the issue exists]

**What Failed**:
[Specific description of what was checked and why it failed]

**Evidence**:
[Show the actual check that failed, e.g., unchecked items, test output]

**How to Fix**:
1. [Step-by-step instructions]
2. [Specific actions needed]
3. [What success looks like]

**Verification**:
[How to verify this issue is fixed]
```

### 4. Create Summary Dashboard

```markdown
# Completion Verification - REJECTION REPORT

**Date**: [timestamp]
**Type**: Story | Epic
**Item**: [ID and Title]
**Overall Status**: ❌ REJECTED

## Summary Statistics
- Total Checks: X
- Passed: Y
- Failed: Z
- Blocking Issues: A
- Critical Issues: B

## Quick Fix Checklist
A prioritized list of what to fix first:

1. [ ] [Most critical blocking issue]
2. [ ] [Next blocking issue]
3. [ ] [Continue...]
```

### 5. Provide Specific Examples

Include concrete examples of what's needed:

#### ❌ Current State (Failing)
```
Test Results: "Tests mostly pass with a few minor failures"
```

#### ✅ Required State (To Pass)
```
Test Results:
========================================
Running test suite...
✓ UserService (5 tests)
✓ AuthController (8 tests)
✓ Integration Tests (12 tests)

All 25 tests passed.
Duration: 4.3s
========================================
```

### 6. Include Evidence Requirements

Specify exactly what evidence is needed:

```markdown
## Required Evidence for Resubmission

### Test Evidence
- [ ] Full test suite output showing 100% pass
- [ ] Include timestamps
- [ ] No skipped tests

### Build Evidence
- [ ] Complete build log
- [ ] Zero errors or warnings
- [ ] Successful deployment readiness

### Functionality Evidence
- [ ] Screenshot/recording of each AC working
- [ ] Manual test steps performed
- [ ] Edge case handling demonstration
```

### 7. Set Expectations

Be clear about the resubmission process:

```markdown
## Next Steps

1. **Fix all BLOCKING issues** - These prevent completion
2. **Address CRITICAL issues** - These ensure quality
3. **Consider IMPROVEMENTS** - These enhance the solution
4. **Collect all evidence** - Document fixes thoroughly
5. **Rerun verification** - Use `*verify-story` command

## Resubmission Criteria
- ALL blocking issues must be resolved
- Evidence must be provided for all fixes
- Original acceptance criteria still apply
- No new issues introduced
```

## Report Templates

### For Unchecked DoD Items
```markdown
### Issue: Incomplete Definition of Done
**Category**: BLOCKING
**Component**: Story DoD Checklist

**What Failed**:
The following DoD items remain unchecked:
- [ ] All tests written and passing
- [ ] Security scan completed
- [ ] Documentation updated

**How to Fix**:
1. Complete each unchecked item
2. Mark with [x] only when truly complete
3. Do not provide explanations for unchecked items
```

### For Missing Evidence
```markdown
### Issue: Insufficient Test Evidence
**Category**: BLOCKING
**Component**: Verification Evidence

**What Failed**:
Generic claim "all tests pass" without supporting evidence

**How to Fix**:
1. Run complete test suite: `npm test`
2. Copy full output including pass/fail details
3. Include timestamp and test count
4. Add to story under "Test Results" section
```

### For Integration Issues
```markdown
### Issue: Story Integration Failure
**Category**: CRITICAL
**Component**: Cross-Story Integration

**What Failed**:
Story X.2 depends on API from X.1 but integration not verified

**How to Fix**:
1. Test X.2 against completed X.1 implementation
2. Verify API contracts match
3. Document integration test results
4. Update both stories with integration evidence
```

## Anti-Frustration Measures

- Be specific, not vague ("Fix tests" vs "Fix UserService.test.js line 45")
- Provide exact commands to run
- Show example of successful output
- Acknowledge partial progress made
- Estimate time to fix each issue

## Report Delivery

1. Save report to story/epic file in Verification Record section
2. Present summary to user immediately
3. Offer to explain any specific issue in detail
4. Be available to clarify requirements

Remember: The goal is to help developers succeed, not to create bureaucratic barriers. Make the path to completion clear and achievable.