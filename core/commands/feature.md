---
description: Execute comprehensive feature development using the feature development framework
argument-hint: [project-path]
---

# Feature Development Framework Execution

## Initialize Feature Development Framework

Use the comprehensive feature development framework from ~/.claude/process-templates-n-prompts/features/

### Step 1: Check for Existing Feature Development Setup
First, check if `.claude/features/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If feature framework doesn't exist in the project:
```bash
mkdir -p .claude/features
cp ~/.claude/process-templates-n-prompts/features/*.md .claude/features/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read features-prompt.md** - Understand the feature development philosophy and methodology
   - Focus on user-centered development and agile practices
   - Review feature flags, A/B testing, and gradual rollout strategies
   - Understand product-engineering collaboration patterns

2. **Load features-template.md** - Use as the structure for feature documentation
   - Reference for feature specification structures
   - Use user story and acceptance criteria templates
   - Follow feature development workflow templates
   - Use testing and validation formats

3. **Follow features-checklist.md** - Execute phases systematically
   - Start with Phase 0: Feature Discovery & Requirements
   - Check off items as completed
   - Document feature specifications and user stories
   - Track development progress and quality metrics

## Execution Instructions

### Phase 0: Feature Discovery & Requirements (MANDATORY FIRST)
- Define feature purpose and user value proposition
- Gather and analyze user requirements and use cases
- Document functional and non-functional specifications
- Map user journeys and interaction flows
- Review existing features and potential integration points
- Establish success metrics and acceptance criteria

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Feature Design & Technical Planning
- Phase 2: Implementation & Development
- Phase 3: Testing & Quality Assurance
- Phase 4: Integration & System Testing
- Phase 5: User Acceptance & Validation
- Phase 6: Deployment & Release
- Phase 7: Monitoring & Post-Release Optimization

## Key Principles

1. **ALWAYS start with user value and clear requirements**
2. **Design for usability, accessibility, and performance**
3. **Implement comprehensive testing at all levels**
4. **Use feature flags for safe deployment and rollback**
5. **Monitor user behavior and feature performance**
6. **Iterate based on user feedback and data**

## Feature Goals
- Clear user value proposition with measurable outcomes
- Comprehensive feature specifications and user stories
- High-quality implementation with thorough testing
- Accessible and performant user experience
- Safe deployment with monitoring and rollback capability
- Post-launch optimization based on user feedback

## Progress Tracking
Update the features-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. feature-specification.md - Detailed feature requirements
2. user-stories.md - User stories with acceptance criteria
3. technical-design.md - Implementation architecture and approach
4. test-plan.md - Comprehensive testing strategy
5. deployment-plan.md - Release and rollout strategy
6. user-documentation.md - End-user guides and help content
7. performance-metrics.md - Feature performance and usage analytics
8. CHANGELOG.md - Document all feature changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Great features solve real problems for real users. Build with empathy, test thoroughly, deploy safely, measure impact.