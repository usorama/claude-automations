---
description: Execute with planning + rules enforcement
argument-hint: [task]
---

Execute this task with detailed planning AND mandatory AI development rules:
$ARGUMENTS

## Combined Directives:

### 📋 **DETAILED PLANNING**
Create a detailed, actionable plan with clear steps, milestones, dependencies, and success criteria. Include risk assessment and contingencies.

### 📚 **MANDATORY RULES ENFORCEMENT**
STRICTLY follow ALL AI development rules in ~/claude-automations/rules.md:

**CRITICAL Planning Requirements:**
- **Research First**: Thoroughly research existing codebase, dependencies, and architecture
- **Plan Before Code**: Create comprehensive implementation plan BEFORE any coding
- **Identify Duplicates**: Find and eliminate conflicting implementations
- **Dependency Analysis**: Review all manifests (package.json, requirements.txt, etc.)
- **Risk Assessment**: Identify and mitigate AI-specific risks (NIST framework)
- **Test Strategy**: Plan test-driven development approach
- **Compliance Check**: Ensure EU AI Act and NIST compliance in plan

**The plan MUST incorporate all rule categories:**
1. Planning & Discovery
2. Code Quality & Security
3. Workflow & Process  
4. Testing & Validation
5. Documentation & Compliance
6. Dependency & Architecture
7. AI-Specific Development

Read complete rules: @~/claude-automations/rules.md