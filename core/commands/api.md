---
description: Execute comprehensive API development using the API development framework
argument-hint: [project-path]
---

# API Development Framework Execution

## Initialize API Development Framework

Use the comprehensive API development framework from ~/.claude/process-templates-n-prompts/api-development/

### Step 1: Check for Existing API Infrastructure
First, check if `.claude/api/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If API framework doesn't exist in the project:
```bash
mkdir -p .claude/api
cp ~/.claude/process-templates-n-prompts/api-development/*.md .claude/api/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read api-prompt.md** - Understand the API design philosophy and development approach
   - Focus on RESTful design principles and GraphQL best practices
   - Review API versioning and evolution strategies
   - Understand security, authentication, and authorization patterns

2. **Load api-template.md** - Use as the structure for API documentation and implementation
   - Reference for endpoint design structures
   - Use naming conventions from template
   - Follow API specification templates (OpenAPI/Swagger)
   - Use response and error handling formats

3. **Follow api-checklist.md** - Execute phases systematically
   - Start with Phase 0: API Requirements & Design
   - Check off items as completed
   - Document API specifications
   - Track performance and security metrics

## Execution Instructions

### Phase 0: API Requirements & Design (MANDATORY FIRST)
- Define API purpose and scope
- Identify target consumers and use cases
- Document functional and non-functional requirements
- Map data models and relationships
- Review existing APIs and integration points
- Define authentication and authorization requirements

### Subsequent Phases
Continue through all phases in order:
- Phase 1: API Specification & Documentation
- Phase 2: API Implementation & Development
- Phase 3: Security & Authentication Implementation
- Phase 4: Testing & Validation
- Phase 5: Performance Optimization
- Phase 6: Documentation & Developer Experience
- Phase 7: Monitoring & Maintenance

## Key Principles

1. **ALWAYS design API contracts before implementation**
2. **Follow RESTful design principles and HTTP standards**
3. **Implement comprehensive error handling and validation**
4. **Ensure consistent naming conventions and patterns**
5. **Plan for versioning and backward compatibility**
6. **Security first - authenticate, authorize, validate, sanitize**

## API Goals
- RESTful design with clear resource modeling
- Comprehensive OpenAPI/Swagger documentation
- Robust error handling and validation
- Performance optimization and caching
- Security best practices implementation
- Developer-friendly experience with examples

## Progress Tracking
Update the api-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. api-specification.yaml - OpenAPI/Swagger specification
2. api-documentation.md - Developer-friendly API docs
3. authentication-guide.md - Auth implementation details
4. error-handling.md - Error codes and handling patterns
5. rate-limiting.md - Rate limiting and throttling docs
6. api-testing-suite/ - Comprehensive API tests
7. performance-benchmarks.md - API performance metrics
8. CHANGELOG.md - Document all API changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: A well-designed API is a contract that enables ecosystems. Design with consumers in mind, document thoroughly, version responsibly.