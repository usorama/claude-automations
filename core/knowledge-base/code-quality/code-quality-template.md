# Code Review & Quality Templates

## 1. ESLint Configuration

```javascript
// .eslintrc.js
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
    jest: true,
  },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:security/recommended',
    'prettier',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: [
    '@typescript-eslint',
    'react',
    'react-hooks',
    'jsx-a11y',
    'security',
    'import',
  ],
  rules: {
    // Code Quality Rules
    'no-console': 'warn',
    'no-debugger': 'error',
    'no-unused-vars': 'error',
    'no-var': 'error',
    'prefer-const': 'error',
    'no-duplicate-imports': 'error',
    
    // TypeScript Rules
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/prefer-nullish-coalescing': 'error',
    '@typescript-eslint/prefer-optional-chain': 'error',
    
    // React Rules
    'react/prop-types': 'off', // TypeScript handles this
    'react/react-in-jsx-scope': 'off', // React 17+
    'react/jsx-uses-react': 'off', // React 17+
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    
    // Import Rules
    'import/order': [
      'error',
      {
        groups: [
          'builtin',
          'external',
          'internal',
          'parent',
          'sibling',
          'index',
        ],
        'newlines-between': 'always',
        alphabetize: {
          order: 'asc',
          caseInsensitive: true,
        },
      },
    ],
    
    // Security Rules
    'security/detect-object-injection': 'error',
    'security/detect-non-literal-regexp': 'warn',
    'security/detect-unsafe-regex': 'error',
    
    // Accessibility Rules
    'jsx-a11y/alt-text': 'error',
    'jsx-a11y/aria-role': 'error',
    'jsx-a11y/click-events-have-key-events': 'error',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  overrides: [
    {
      files: ['*.test.js', '*.test.ts', '*.test.tsx'],
      env: {
        jest: true,
      },
      rules: {
        'security/detect-non-literal-regexp': 'off',
      },
    },
  ],
};
```

## 2. Pull Request Template

```markdown
<!-- .github/pull_request_template.md -->
## Description

Brief description of the changes and the problem they solve.

Fixes #(issue number)

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Performance improvement
- [ ] Code refactoring (no functional changes)
- [ ] Documentation update
- [ ] Test coverage improvement

## How Has This Been Tested?

- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing
- [ ] Performance testing

**Test Configuration**:
* Operating System:
* Browser (if applicable):
* Node.js version:

## Checklist

### Code Quality
- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings or errors

### Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Test coverage has not decreased
- [ ] Any dependent changes have been merged and published

### Documentation
- [ ] I have made corresponding changes to the documentation
- [ ] API documentation has been updated (if applicable)
- [ ] README has been updated (if applicable)

### Security & Performance
- [ ] I have checked for security vulnerabilities in my code
- [ ] I have considered the performance impact of my changes
- [ ] No sensitive information is exposed in the code

### Review
- [ ] I have requested review from appropriate team members
- [ ] All review comments have been addressed
- [ ] The PR title clearly describes the change
- [ ] Related issues are linked

## Screenshots (if applicable)

Add screenshots to help explain your changes.

## Additional Notes

Add any other context or notes about the pull request here.
```

## 3. SonarQube Quality Gate Configuration

```yaml
# sonar-project.properties
sonar.projectKey=your-project-key
sonar.projectName=Your Project Name
sonar.projectVersion=1.0

# Source code settings
sonar.sources=src
sonar.tests=src
sonar.test.inclusions=**/*.test.js,**/*.test.ts,**/*.test.tsx,**/*.spec.js

# Exclusions
sonar.exclusions=**/node_modules/**,**/build/**,**/dist/**,**/*.min.js
sonar.test.exclusions=**/node_modules/**,**/build/**,**/dist/**

# Coverage settings
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.typescript.lcov.reportPaths=coverage/lcov.info

# Quality gate conditions
sonar.qualitygate.wait=true

# Custom quality profiles
sonar.profile=Recommended
```

```json
{
  "qualityGate": {
    "name": "Custom Quality Gate",
    "conditions": [
      {
        "metric": "new_coverage",
        "operator": "LT",
        "threshold": "80",
        "error": true
      },
      {
        "metric": "new_duplicated_lines_density",
        "operator": "GT",
        "threshold": "3",
        "error": true
      },
      {
        "metric": "new_maintainability_rating",
        "operator": "GT",
        "threshold": "1",
        "error": true
      },
      {
        "metric": "new_reliability_rating",
        "operator": "GT",
        "threshold": "1",
        "error": true
      },
      {
        "metric": "new_security_rating",
        "operator": "GT",
        "threshold": "1",
        "error": true
      },
      {
        "metric": "new_security_hotspots_reviewed",
        "operator": "LT",
        "threshold": "100",
        "error": true
      }
    ]
  }
}
```

## 4. GitHub Actions CI/CD with Quality Gates

```yaml
# .github/workflows/quality-check.yml
name: Code Quality Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run linting
      run: npm run lint

    - name: Run formatting check
      run: npm run format:check

    - name: Run type checking
      run: npm run type-check

    - name: Run unit tests with coverage
      run: npm run test:coverage

    - name: Run security audit
      run: npm audit --audit-level=moderate

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info
        flags: unittests
        name: codecov-umbrella

    - name: SonarQube Scan
      uses: sonarqube-quality-gate-action@master
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      with:
        scanMetadataReportFile: target/sonar/report-task.txt

    - name: Quality Gate Check
      run: |
        # Check if quality gate passes
        if [ "${{ steps.sonarqube.outputs.quality-gate-status }}" != "PASSED" ]; then
          echo "Quality gate failed"
          exit 1
        fi

  dependency-check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/node@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      with:
        args: --severity-threshold=high

  build-check:
    runs-on: ubuntu-latest
    needs: [quality-check, dependency-check]
    steps:
    - uses: actions/checkout@v4
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'
    - name: Install dependencies
      run: npm ci
    - name: Build project
      run: npm run build
    - name: Run production smoke tests
      run: npm run test:smoke
```

## 5. Code Review Checklist

```markdown
# Code Review Checklist

## Functionality
- [ ] Code correctly implements the requirements
- [ ] Edge cases are handled appropriately
- [ ] Error handling is implemented and appropriate
- [ ] Code handles null/undefined values safely
- [ ] Business logic is correct and complete

## Code Quality
- [ ] Code is readable and self-documenting
- [ ] Variable and function names are descriptive
- [ ] Functions are small and do one thing well
- [ ] Code follows DRY (Don't Repeat Yourself) principle
- [ ] Complex logic is commented and explained

## Architecture & Design
- [ ] Code follows established patterns and conventions
- [ ] Separation of concerns is maintained
- [ ] Dependencies are appropriate and minimal
- [ ] Code is modular and reusable
- [ ] Interfaces are well-defined

## Performance
- [ ] No obvious performance bottlenecks
- [ ] Database queries are optimized
- [ ] Appropriate caching is implemented
- [ ] Memory usage is efficient
- [ ] No unnecessary re-renders (React)

## Security
- [ ] Input validation is implemented
- [ ] No sensitive data in logs or client-side code
- [ ] Authentication and authorization are proper
- [ ] No SQL injection vulnerabilities
- [ ] HTTPS is used for sensitive operations

## Testing
- [ ] Adequate test coverage for new code
- [ ] Tests are meaningful and test the right things
- [ ] Tests are maintainable and readable
- [ ] Integration tests cover critical paths
- [ ] Tests pass consistently

## Documentation
- [ ] API documentation is updated
- [ ] README is updated if needed
- [ ] Inline comments explain complex logic
- [ ] Breaking changes are documented
- [ ] Migration guides provided if needed

## Deployment & Operations
- [ ] Configuration changes are documented
- [ ] Database migrations are safe and reversible
- [ ] Monitoring and logging are adequate
- [ ] Feature flags are used appropriately
- [ ] Rollback plan is considered
```

## 6. Pre-commit Hooks Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-case-conflict
      - id: check-added-large-files
        args: ['--maxkb=1000']

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.44.0
    hooks:
      - id: eslint
        files: \.(js|ts|tsx)$
        types: [file]
        additional_dependencies:
          - eslint@8.44.0
          - '@typescript-eslint/eslint-plugin@5.61.0'
          - '@typescript-eslint/parser@5.61.0'

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        files: \.(js|ts|tsx|json|yml|yaml|md)$

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v2.3.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]

  - repo: local
    hooks:
      - id: jest
        name: jest
        entry: npm run test:staged
        language: system
        pass_filenames: false
        files: \.(js|ts|tsx)$

      - id: type-check
        name: TypeScript type check
        entry: npm run type-check
        language: system
        pass_filenames: false
        files: \.(ts|tsx)$

      - id: security-check
        name: Security audit
        entry: npm audit
        language: system
        pass_filenames: false
        always_run: true
```

## 7. Jest Testing Configuration

```javascript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/*.(test|spec).+(ts|tsx|js)'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/reportWebVitals.ts'
  ],
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/build/',
    '/coverage/',
    '/.git/'
  ],
  coverageReporters: [
    'text',
    'lcov',
    'html',
    'json-summary'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
  },
  testTimeout: 10000,
  maxWorkers: '50%',
  clearMocks: true,
  restoreMocks: true
};
```