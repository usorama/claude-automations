# E2E TESTING CHECKLIST FOR CLAUDE CODE (PROJECT-AGNOSTIC)

## 🔎 PHASE 0: DISCOVERY & INVENTORY (MANDATORY FIRST)
### Existing Test Infrastructure Discovery
- [ ] **SEARCH** for test directories (test/, tests/, spec/, __tests__/)
- [ ] **FIND** existing test files and note naming patterns
- [ ] **LOCATE** testing manifests or documentation
- [ ] **CHECK** for playwright.config.* or other test configs
- [ ] **IDENTIFY** existing coverage reports and metrics
- [ ] **DISCOVER** CI/CD test workflows (.github/, .gitlab-ci.yml)
- [ ] **FIND** existing claude.md or .claude/ directories
- [ ] **LIST** all test-related dependencies in package.json/requirements

### Document What Exists
- [ ] Record existing test count and types
- [ ] Note current coverage percentage
- [ ] Document test naming conventions
- [ ] List testing frameworks in use
- [ ] Identify test data management approach
- [ ] Map existing test utilities and helpers
- [ ] Document UI testing tools if present
- [ ] Note accessibility testing setup
- [ ] Find performance testing configurations

### Analyze Quality of Existing Tests
- [ ] Identify passing vs failing tests
- [ ] Find flaky or unstable tests
- [ ] Locate slow-running tests
- [ ] Check for outdated test patterns
- [ ] Assess test maintainability
- [ ] Evaluate existing coverage gaps
- [ ] Review UI/UX test coverage
- [ ] Check accessibility test completeness

### Decision Points
- [ ] **DECIDE**: Update existing OR create new test structure
- [ ] **DETERMINE**: Which tests to preserve, update, or deprecate
- [ ] **PLAN**: Integration strategy with existing infrastructure
- [ ] **CONFIRM**: Compatibility requirements with CI/CD

## 🎯 PHASE 1: PREPARATION & ANALYSIS
### Codebase Analysis (With Context)
- [ ] **THINK** - Activate thinking mode before starting
- [ ] **IDENTIFY** project type (web/mobile/desktop/api/cli/library)
- [ ] **COMPARE** project structure with existing tests
- [ ] **READ** and verify package files (package.json, requirements.txt, etc.)
- [ ] **CHECK** if config files are already tested
- [ ] **MAP** infrastructure configs against existing tests
- [ ] **IDENTIFY** untested external service dependencies

### Route & Endpoint Discovery (Incremental)
- [ ] **REVIEW** existing route/endpoint test coverage
- [ ] **IDENTIFY** new/untested routes since last update
- [ ] **COMPARE** API endpoints with existing test files
- [ ] **FIND** GraphQL schemas/operations not yet tested
- [ ] **DISCOVER** WebSocket endpoints without tests
- [ ] **LIST** authentication/authorization endpoints needing coverage
- [ ] **MAP** public vs protected routes

### Component Inventory (Gap Analysis)
- [ ] **CHECK** which UI components have tests
- [ ] **IDENTIFY** new components without coverage
- [ ] **VERIFY** shared/reusable component test status
- [ ] **MAP** component dependencies not tested
- [ ] **FIND** forms/inputs lacking validation tests
- [ ] **LIST** untested interactive elements
- [ ] **IDENTIFY** missing visual regression tests

### UI/UX Testing Requirements
- [ ] **MAP** all user interface states
- [ ] **IDENTIFY** interactive elements
- [ ] **DOCUMENT** animation and transitions
- [ ] **LIST** responsive breakpoints
- [ ] **FIND** touch/gesture interactions
- [ ] **NOTE** micro-interactions
- [ ] **CHECK** loading and error states

### Accessibility Requirements
- [ ] **IDENTIFY** WCAG compliance level needed
- [ ] **CHECK** existing accessibility tests
- [ ] **MAP** keyboard navigation paths
- [ ] **LIST** screen reader requirements
- [ ] **DOCUMENT** color contrast needs
- [ ] **FIND** ARIA implementation gaps

### Dependency Validation (Update Check)
- [ ] **VERIFY** if import tests exist and are current
- [ ] **UPDATE** circular dependency checks
- [ ] **IDENTIFY** new unused imports
- [ ] **VALIDATE** export statement coverage
- [ ] **CHECK** for new package vulnerabilities
- [ ] **CONFIRM** version compatibility tests exist

## 📋 PHASE 2: TEST PLANNING (BUILD ON EXISTING)
### Testing Manifest Creation/Update
- [ ] **CHECK** if testing-manifest.md exists
  - If YES:
    - [ ] Read existing manifest completely
    - [ ] Identify outdated sections
    - [ ] Update with new findings
    - [ ] Preserve valid content
    - [ ] Version the document
  - If NO:
    - [ ] Create new testing-manifest.md
    - [ ] Follow discovered conventions
    - [ ] Document all test scenarios

### User Roles & Journeys (Generic)
- [ ] **IDENTIFY** all user roles in the system
- [ ] **MAP** permissions per role
- [ ] **DOCUMENT** critical user journeys
- [ ] **CREATE** test scenarios for each role:
  - [ ] Admin/Super User workflows
  - [ ] Standard User workflows
  - [ ] Guest/Anonymous workflows
  - [ ] Premium/Paid User workflows (if applicable)
  - [ ] Limited/Free User workflows (if applicable)
  - [ ] API Consumer workflows (if applicable)
- [ ] **DEFINE** error recovery paths
- [ ] **MAP** state transitions

### Test Categories Setup (Comprehensive)
- [ ] **FUNCTIONAL** - Core functionality tests
- [ ] **VISUAL** - UI consistency and regression
- [ ] **ACCESSIBILITY** - WCAG compliance
- [ ] **PERFORMANCE** - Speed and efficiency
- [ ] **SECURITY** - Vulnerability testing
- [ ] **USABILITY** - User experience validation
- [ ] **COMPATIBILITY** - Cross-platform/browser
- [ ] **LOCALIZATION** - i18n/l10n testing
- [ ] **INTEGRATION** - Third-party services
- [ ] **DATA** - Data integrity and validation

## 🔨 PHASE 3: IMPLEMENTATION (RESPECT EXISTING)
### Test Framework Configuration
- [ ] **CHECK** existing test framework setup
- [ ] **VERIFY** test runner configuration
- [ ] **UPDATE** deprecated settings
- [ ] **ADD** missing test categories
- [ ] **CONFIGURE** reporting mechanisms
- [ ] **SET UP** parallel execution
- [ ] **ENABLE** coverage tracking

### Test File Creation (Extend, Don't Replace)
- [ ] **USE** existing test directory structure
- [ ] **FOLLOW** established naming patterns
- [ ] **EXTEND** existing page object models
- [ ] **REUSE** existing test utilities
- [ ] **UPDATE** test data factories
- [ ] **ENHANCE** existing fixtures
- [ ] **ADD** new helper functions as needed

### UI/UX Test Implementation
- [ ] **CREATE** visual regression baselines
- [ ] **SET UP** viewport testing
- [ ] **IMPLEMENT** interaction tests
- [ ] **ADD** animation performance tests
- [ ] **CREATE** responsive design tests
- [ ] **IMPLEMENT** cross-browser tests
- [ ] **ADD** usability test scenarios

### Accessibility Test Implementation
- [ ] **CONFIGURE** automated a11y tools
- [ ] **CREATE** keyboard navigation tests
- [ ] **IMPLEMENT** screen reader tests
- [ ] **ADD** color contrast validation
- [ ] **CREATE** ARIA compliance tests
- [ ] **IMPLEMENT** focus management tests

### Performance Test Implementation
- [ ] **SET UP** load testing scenarios
- [ ] **CREATE** stress test cases
- [ ] **IMPLEMENT** spike tests
- [ ] **ADD** endurance tests
- [ ] **CREATE** volume tests
- [ ] **IMPLEMENT** scalability tests

### Security Test Implementation
- [ ] **CONFIGURE** vulnerability scanners
- [ ] **CREATE** authentication tests
- [ ] **IMPLEMENT** authorization tests
- [ ] **ADD** input validation tests
- [ ] **CREATE** session management tests
- [ ] **IMPLEMENT** API security tests

## ✅ PHASE 4: TEST EXECUTION (COMPREHENSIVE)
### Pre-Execution Checks
- [ ] **VERIFY** existing tests still pass
- [ ] **ENSURE** backward compatibility
- [ ] **CONFIRM** CI/CD pipeline ready
- [ ] **CHECK** test data is prepared
- [ ] **VALIDATE** environment setup
- [ ] **CONFIRM** all test tools configured

### Functional Testing
- [ ] Execute unit tests
- [ ] Run integration tests
- [ ] Execute E2E tests
- [ ] Verify business logic
- [ ] Test data flows
- [ ] Validate calculations
- [ ] Check state management

### UI/UX Testing
- [ ] Run visual regression tests
- [ ] Execute responsive design tests
- [ ] Test all interactions
- [ ] Verify animations
- [ ] Check loading states
- [ ] Test error states
- [ ] Validate empty states
- [ ] Test micro-interactions

### Accessibility Testing
- [ ] Run automated a11y scans
- [ ] Test keyboard navigation
- [ ] Verify screen reader compatibility
- [ ] Check color contrast
- [ ] Validate ARIA implementation
- [ ] Test focus management
- [ ] Verify semantic HTML

### Performance Testing
- [ ] Execute load tests
- [ ] Run stress tests
- [ ] Perform spike tests
- [ ] Execute endurance tests
- [ ] Check memory usage
- [ ] Monitor CPU usage
- [ ] Test network efficiency
- [ ] Validate caching

### Security Testing
- [ ] Run vulnerability scans
- [ ] Test authentication flows
- [ ] Verify authorization rules
- [ ] Test input validation
- [ ] Check session management
- [ ] Validate API security
- [ ] Test for OWASP Top 10

### Cross-Platform/Browser Testing
- [ ] Test on Chrome
- [ ] Test on Firefox
- [ ] Test on Safari
- [ ] Test on Edge
- [ ] Test on mobile browsers
- [ ] Test on different OS
- [ ] Verify responsive behavior

## 🔍 PHASE 5: QUALITY VALIDATION (COMPARATIVE)
### Code Quality Checks (Before vs After)
- [ ] **COMPARE** duplicate code (baseline vs current)
- [ ] **VERIFY** no new missing routes
- [ ] **CONFIRM** imports still correct
- [ ] **CHECK** for new stale code
- [ ] **VALIDATE** dependency usage
- [ ] **ENSURE** error handling improved
- [ ] **VERIFY** memory leak prevention

### Coverage Verification (Improvement Metrics)
- [ ] **MEASURE** baseline coverage percentage
- [ ] **CALCULATE** new coverage percentage
- [ ] **DOCUMENT** coverage improvement
- [ ] **VERIFY** functional coverage targets
- [ ] **CONFIRM** UI/UX test coverage
- [ ] **VALIDATE** accessibility coverage
- [ ] **CHECK** performance test coverage
- [ ] **ENSURE** security test coverage

### Technical Debt Analysis (Track Changes)
- [ ] **REVIEW** previously identified debt
- [ ] **IDENTIFY** new code smells
- [ ] **DOCUMENT** resolved issues
- [ ] **FIND** complexity hotspots
- [ ] **NOTE** refactoring needs
- [ ] **LIST** remaining issues
- [ ] **PRIORITIZE** fix order

### Quality Metrics Validation
- [ ] **CHECK** code complexity metrics
- [ ] **VERIFY** maintainability index
- [ ] **VALIDATE** test quality metrics
- [ ] **CONFIRM** documentation coverage
- [ ] **CHECK** code duplication percentage
- [ ] **VERIFY** cyclomatic complexity

## 📊 PHASE 6: REPORTING (COMPREHENSIVE)
### Test Results Documentation
- [ ] **CREATE** executive summary
- [ ] **SHOW** before/after metrics
- [ ] **HIGHLIGHT** improvements made
- [ ] **DOCUMENT** new coverage areas
- [ ] **LIST** preserved test value
- [ ] **EXPLAIN** any regressions
- [ ] **PROVIDE** fix recommendations

### Multi-Dimensional Metrics
- [ ] Functional test results
- [ ] Visual regression results
- [ ] Accessibility audit results
- [ ] Performance test results
- [ ] Security scan results
- [ ] Usability test results
- [ ] Compatibility test results
- [ ] Localization test results

### Issue Documentation (Categorized)
- [ ] **CATEGORIZE** by severity (Critical/High/Medium/Low)
- [ ] **CLASSIFY** by type (Bug/Performance/Security/UX/A11y)
- [ ] **SEPARATE** existing vs new issues
- [ ] **PRIORITIZE** based on impact
- [ ] **DOCUMENT** reproduction steps
- [ ] **PROVIDE** fix recommendations
- [ ] **ESTIMATE** resolution effort

### Stakeholder Reports
- [ ] Technical report for developers
- [ ] Executive summary for management
- [ ] Quality report for QA team
- [ ] Security report for security team
- [ ] Accessibility report for compliance
- [ ] Performance report for DevOps
- [ ] UX report for design team

## 🚀 PHASE 7: CONTINUOUS IMPROVEMENT
### CI/CD Integration (Maintain Compatibility)
- [ ] **ENSURE** existing pipelines work
- [ ] **UPDATE** test commands if needed
- [ ] **ADD** new test stages
- [ ] **CONFIGURE** quality gates
- [ ] **SET UP** automated reporting
- [ ] **ENABLE** trend analysis
- [ ] **CREATE** feedback loops

### Test Maintenance Strategy
- [ ] **SCHEDULE** regular test reviews
- [ ] **AUTOMATE** test updates where possible
- [ ] **MONITOR** test effectiveness
- [ ] **TRACK** flakiness metrics
- [ ] **OPTIMIZE** execution time
- [ ] **UPDATE** test data regularly
- [ ] **MAINTAIN** test documentation

### Documentation Evolution
- [ ] **VERSION** all test artifacts
- [ ] **UPDATE** testing guides
- [ ] **MAINTAIN** test catalogs
- [ ] **DOCUMENT** best practices
- [ ] **CREATE** troubleshooting guides
- [ ] **UPDATE** onboarding docs
- [ ] **MAINTAIN** change logs

## 🎯 FINAL VALIDATION
### Success Criteria (Universal)
- [ ] **FUNCTIONAL** - All features work correctly
- [ ] **VISUAL** - UI is consistent and polished
- [ ] **ACCESSIBLE** - Meets WCAG standards
- [ ] **PERFORMANT** - Meets speed targets
- [ ] **SECURE** - No critical vulnerabilities
- [ ] **USABLE** - Good user experience
- [ ] **COMPATIBLE** - Works across platforms
- [ ] **DOCUMENTED** - Comprehensive documentation

### Quality Gates
- [ ] All existing tests passing
- [ ] New tests integrated successfully
- [ ] Coverage targets achieved
- [ ] Performance benchmarks met
- [ ] Security standards satisfied
- [ ] Accessibility requirements fulfilled
- [ ] Documentation complete and current

### Sign-off Checklist
- [ ] Development team approval
- [ ] QA team sign-off
- [ ] Security team clearance
- [ ] UX team approval
- [ ] Accessibility audit passed
- [ ] Performance validated
- [ ] Documentation reviewed
- [ ] Deployment ready

## 🚨 CRITICAL REMINDERS
⚠️ **NEVER**:
- Skip the discovery phase
- Delete tests without justification
- Ignore existing patterns
- Create duplicate test files
- Override working configurations
- Make assumptions about code
- Assume project type or domain

✅ **ALWAYS**:
- Check what exists first
- Preserve working tests
- Build on existing infrastructure
- Document all changes
- Maintain backward compatibility
- Test all aspects comprehensively
- Use evidence-based verification

## 📝 CHANGE LOG
Track all modifications:
- [ ] Tests added: _____________
- [ ] Tests updated: ___________
- [ ] Tests preserved: _________
- [ ] Tests deprecated: ________
- [ ] Config changes: __________
- [ ] Breaking changes: ________

## 🔄 ROLLBACK PLAN
In case of issues:
- [ ] Git commit hash before changes: _______
- [ ] Backup location of original tests: _______
- [ ] Rollback command documented
- [ ] Team notified of changes
- [ ] Rollback tested and verified

## 📈 METRICS TRACKING
### Baseline (Before)
- Functional Coverage: _______%
- Visual Coverage: _______%
- Accessibility Score: _______
- Performance Score: _______
- Security Score: _______
- Overall Quality: _______

### Current (After)
- Functional Coverage: _______%
- Visual Coverage: _______%
- Accessibility Score: _______
- Performance Score: _______
- Security Score: _______
- Overall Quality: _______

### Improvement
- Coverage Gain: _______%
- Quality Improvement: _______%
- Issues Resolved: _______
- New Issues Found: _______

---
**Last Updated**: [Date]
**Version**: 2.0.0 (Project-Agnostic)
**Owner**: [Your Name]
**Project**: [Project Name]
**Project Type**: [Web/Mobile/Desktop/API/CLI/Library]
**Testing Scope**: [Full/Partial/Specific Features]
