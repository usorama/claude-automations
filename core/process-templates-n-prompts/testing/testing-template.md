# E2E TESTING TEMPLATE FOR CLAUDE CODE (PROJECT-AGNOSTIC)

## 🔍 DISCOVERY SECTION (EXECUTE FIRST)
### Existing Artifact Inventory
```yaml
existing_artifacts:
  test_directories:
    found: []  # List all test directories found
    patterns_used: []  # e.g., *.test.ts, *.spec.js
    
  test_manifests:
    found: []  # existing manifests, docs
    format: []  # markdown, yaml, json
    
  test_configurations:
    playwright_config: null  # path if exists
    jest_config: null  # path if exists
    cypress_config: null  # path if exists
    other_configs: []
    
  coverage_reports:
    existing_coverage: null  # baseline percentage
    report_location: null  # path to reports
    
  ci_cd_integration:
    github_actions: []  # workflow files
    gitlab_ci: null
    jenkins: null
    azure_devops: null
    other: []
```

### Integration Strategy
```yaml
integration_approach:
  strategy: UPDATE  # UPDATE | EXTEND | CREATE_NEW
  reason: ""  # Why this approach was chosen
  
  preserve:
    - existing_test_ids
    - test_data_fixtures
    - helper_functions
    - page_objects
    - custom_commands
    
  update:
    - coverage_targets
    - test_scenarios
    - documentation
    - deprecated_patterns
    
  add_new:
    - missing_test_cases
    - uncovered_endpoints
    - new_user_journeys
    - ui_ux_tests
    - accessibility_tests
```

## Project Configuration
```yaml
project_name: ${PROJECT_NAME}
project_type: ${PROJECT_TYPE}  # web|mobile|desktop|api|cli|library
test_framework: ${EXISTING_OR_PLAYWRIGHT}  # Use existing if found
coverage_target: 100%
coverage_baseline: ${EXISTING_COVERAGE}%  # Current coverage
parallel_execution: true
max_workers: 10

# Testing Categories
testing_types:
  - functional
  - visual_regression
  - accessibility
  - performance
  - security
  - usability
  - localization
  - compatibility

# Compatibility Settings
maintain_compatibility:
  with_existing_tests: true
  with_ci_cd: true
  with_naming_conventions: true
```

## Test Structure Template

### 0. Existing Test Analysis
```yaml
existing_tests_analysis:
  test_count: ${EXISTING_TEST_COUNT}
  coverage_gaps:
    - uncovered_endpoints: []
    - missing_user_roles: []
    - untested_components: []
    - missing_ui_states: []
    - accessibility_gaps: []
    
  quality_issues:
    - flaky_tests: []
    - slow_tests: []
    - outdated_tests: []
    - incomplete_tests: []
    
  reusable_components:
    - test_utilities: []
    - page_objects: []
    - fixtures: []
    - custom_matchers: []
```

### 1. Infrastructure Tests
```yaml
infrastructure_tests:
  # Mark existing tests
  existing:
    - test_id: ${EXISTING_ID}
      status: KEEP  # KEEP | UPDATE | DEPRECATE
      reason: "Still valid and passing"
      
  # New tests to add
  new:
    containers:
      - test_id: INFRA-001-NEW
        description: Verify all services start successfully
        conflicts_with: null  # Check for conflicts
        test_steps:
          - action: Start all services
            verify: All services running
          - action: Check health endpoints
            verify: All return healthy status
        assertions:
          - All services accessible
          - No restart loops
          - Resource usage within limits
```

### 2. Route Coverage Tests (Generic)
```xml
<route_tests>
  <test id="ROUTE-001" status="UPDATE">
    <description>Test all GET endpoints</description>
    <test_steps>
      <step status="EXISTING">
        <action>GET /api/resources</action>
        <expected>200 with resource list</expected>
      </step>
      <step status="NEW">
        <action>GET /api/resources/:id</action>
        <expected>200 with resource details</expected>
      </step>
    </test_steps>
  </test>
</route_tests>
```

### 3. User Journey Tests (Generic Personas)
```typescript
// Generic user personas - adapt to your project
interface TestMetadata {
  isNew: boolean;
  replacesTest?: string;
  extendsTest?: string;
  version: string;
}

interface UserJourney {
  metadata: TestMetadata;
  persona: string;  // Admin | User | Guest | Premium | Free | etc.
  journey_name: string;
  steps: JourneyStep[];
  expected_outcome: string;
}

// Example: Admin Journey
const adminJourney: UserJourney = {
  metadata: {
    isNew: false,
    extendsTest: 'existing-admin-journey-v1',
    version: '2.0.0'
  },
  persona: 'Admin',
  journey_name: 'System configuration workflow',
  steps: [
    { action: 'Login as admin', verify: 'Admin dashboard visible', status: 'existing' },
    { action: 'Navigate to settings', verify: 'Settings page loaded', status: 'existing' },
    { action: 'Modify configuration', verify: 'Changes saved', status: 'new' },
    { action: 'Verify changes applied', verify: 'System updated', status: 'new' }
  ],
  expected_outcome: 'Configuration successfully updated'
};

// Example: Standard User Journey
const userJourney: UserJourney = {
  metadata: {
    isNew: true,
    version: '1.0.0'
  },
  persona: 'Standard User',
  journey_name: 'Core functionality workflow',
  steps: [
    { action: 'Login as user', verify: 'User dashboard visible' },
    { action: 'Access main feature', verify: 'Feature available' },
    { action: 'Perform primary action', verify: 'Action completed' },
    { action: 'View results', verify: 'Results displayed correctly' }
  ],
  expected_outcome: 'User successfully completes primary workflow'
};
```

### 4. UI/UX Testing Template
```yaml
ui_ux_tests:
  visual_regression:
    - test_id: UI-VR-001
      description: Component visual consistency
      viewports: [mobile, tablet, desktop, 4k]
      browsers: [chrome, firefox, safari, edge]
      scenarios:
        - default_state
        - hover_state
        - active_state
        - disabled_state
        - error_state
        - loading_state
      
  responsive_design:
    - test_id: UI-RD-001
      breakpoints:
        - mobile: 320px, 375px, 414px
        - tablet: 768px, 1024px
        - desktop: 1280px, 1440px, 1920px
      test_items:
        - layout_integrity
        - text_readability
        - image_scaling
        - navigation_usability
        - form_interaction
        
  interaction_testing:
    - test_id: UI-INT-001
      interactions:
        - click_events
        - hover_effects
        - drag_and_drop
        - swipe_gestures
        - keyboard_shortcuts
        - focus_management
        
  usability_metrics:
    - task_completion_rate
    - error_rate
    - time_on_task
    - user_satisfaction
    - learnability
```

### 5. Accessibility Testing Template
```yaml
accessibility_tests:
  wcag_compliance:
    level: AA  # A | AA | AAA
    version: 2.1
    
  automated_checks:
    - test_id: A11Y-001
      tools: [axe-core, pa11y, lighthouse]
      criteria:
        - color_contrast: 4.5:1 minimum
        - heading_hierarchy: properly nested
        - form_labels: all inputs labeled
        - alt_text: all images described
        - keyboard_navigation: fully functional
        - focus_indicators: clearly visible
        - aria_attributes: properly used
        
  screen_reader_tests:
    - test_id: A11Y-SR-001
      readers: [NVDA, JAWS, VoiceOver]
      test_scenarios:
        - navigation_announcement
        - form_interaction
        - error_messages
        - dynamic_content_updates
        - table_navigation
```

### 6. Performance Testing Template
```yaml
performance_benchmarks:
  page_metrics:
    first_contentful_paint: < 1.8s
    largest_contentful_paint: < 2.5s
    first_input_delay: < 100ms
    cumulative_layout_shift: < 0.1
    time_to_interactive: < 3.8s
    
  api_performance:
    response_time_p50: < 200ms
    response_time_p95: < 500ms
    response_time_p99: < 1000ms
    throughput: > 1000 req/s
    error_rate: < 0.1%
    
  resource_usage:
    memory_usage: < 512MB
    cpu_usage: < 70%
    network_bandwidth: optimized
    database_connections: < 100
    
  load_testing:
    concurrent_users: [10, 50, 100, 500, 1000]
    sustained_load_duration: 60 minutes
    spike_test_multiplier: 2x
    stress_test_limit: find breaking point
```

### 7. Security Testing Template
```yaml
security_tests:
  vulnerability_scanning:
    - owasp_top_10
    - dependency_audit
    - container_scanning
    - infrastructure_scanning
    
  authentication_tests:
    - password_policies
    - session_management
    - multi_factor_auth
    - oauth_flows
    - jwt_validation
    
  authorization_tests:
    - role_based_access
    - resource_permissions
    - api_rate_limiting
    - privilege_escalation
    
  input_validation:
    - sql_injection
    - xss_prevention
    - csrf_protection
    - file_upload_validation
    - api_input_sanitization
```

### 8. Localization Testing Template
```yaml
localization_tests:
  supported_locales: []  # Add your supported locales
  
  text_validation:
    - translation_completeness
    - text_truncation
    - character_encoding
    - special_characters
    
  formatting_tests:
    - date_time_formats
    - number_formats
    - currency_display
    - address_formats
    
  layout_tests:
    - rtl_support
    - text_expansion
    - font_rendering
    - ui_element_alignment
```

### 9. Component Testing (Generic)
```yaml
component_tests:
  # Existing components with tests
  existing_coverage:
    - component: FormComponent
      current_tests: [valid_input, invalid_input]
      add_tests: [edge_cases, accessibility, visual_regression]
      coverage_before: 60%
      coverage_target: 100%
      
  # New components without tests  
  new_coverage:
    - component: DataTableComponent
      test_cases:
        - data_rendering
        - sorting_functionality
        - filtering_options
        - pagination
        - empty_state
        - error_state
        - loading_state
        - responsive_behavior
        - keyboard_navigation
        - screen_reader_support
```

### 10. Self-Healing Test Pattern
```typescript
class SelfHealingTest {
  maxRetries = 3;
  existingSelectors: Map<string, string>;
  
  constructor() {
    this.existingSelectors = this.loadExistingSelectors();
  }
  
  async findElement(identifier: string): Promise<Element> {
    // Try existing selector first
    if (this.existingSelectors.has(identifier)) {
      try {
        return await this.page.locator(this.existingSelectors.get(identifier));
      } catch {
        // Existing selector failed, try healing
      }
    }
    
    // Try multiple strategies
    const strategies = [
      () => this.byTestId(identifier),
      () => this.byRole(identifier),
      () => this.byLabel(identifier),
      () => this.byText(identifier),
      () => this.byPlaceholder(identifier),
      () => this.byTitle(identifier),
      () => this.byAltText(identifier)
    ];
    
    for (const strategy of strategies) {
      try {
        const element = await strategy();
        this.cacheSelector(identifier, element);
        return element;
      } catch {
        continue;
      }
    }
    
    throw new Error(`Unable to find element: ${identifier}`);
  }
}
```

## Coverage Metrics Template (Comprehensive)
```javascript
const coverageMetrics = {
  baseline: {  // What existed before
    functional_coverage: 0,
    visual_coverage: 0,
    accessibility_score: 0,
    performance_score: 0,
    security_score: 0,
    code_coverage: {
      statements: 0,
      branches: 0,
      functions: 0,
      lines: 0
    }
  },
  target: {  // What we're aiming for
    functional_coverage: 100,
    visual_coverage: 95,
    accessibility_score: 100,
    performance_score: 90,
    security_score: 95,
    code_coverage: {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90
    }
  },
  current: {  // After our updates
    // Will be populated after test execution
  },
  improvement: {  // Calculated difference
    // Will be calculated after test execution
  }
};
```

## Report Generation Template
```markdown
# Comprehensive E2E Test Report

## Executive Summary
- **Project Type**: ${PROJECT_TYPE}
- **Testing Scope**: ${TESTING_SCOPE}
- **Overall Coverage**: ${OVERALL_COVERAGE}%
- **Quality Score**: ${QUALITY_SCORE}/100

## Coverage Analysis

### Functional Testing
- Baseline: ${BASELINE_FUNCTIONAL}%
- Current: ${CURRENT_FUNCTIONAL}%
- Improvement: ${IMPROVEMENT_FUNCTIONAL}%

### UI/UX Testing
- Visual Regression: ${VISUAL_REGRESSION_RESULTS}
- Responsive Design: ${RESPONSIVE_RESULTS}
- Usability Score: ${USABILITY_SCORE}

### Accessibility Testing
- WCAG Compliance: ${WCAG_LEVEL}
- Issues Found: ${A11Y_ISSUES}
- Score: ${A11Y_SCORE}/100

### Performance Testing
- Load Time: ${LOAD_TIME}
- Performance Score: ${PERF_SCORE}/100
- Bottlenecks: ${BOTTLENECKS}

### Security Testing
- Vulnerabilities: ${VULNERABILITIES}
- Risk Level: ${RISK_LEVEL}
- Compliance: ${COMPLIANCE_STATUS}

## Test Execution Summary
${TEST_EXECUTION_DETAILS}

## Recommendations
${RECOMMENDATIONS}

## Action Items
${ACTION_ITEMS}
```

## Variables to Replace
All ${VARIABLES} should be replaced with project-specific values
