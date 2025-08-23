---
description: Execute comprehensive UX research using the UX research framework
argument-hint: [project-path]
---

# UX Research Framework Execution

## Initialize UX Research Framework

Use the comprehensive UX research framework from ~/.claude/process-templates-n-prompts/ux-research/

### Step 1: Check for Existing UX Research Infrastructure
First, check if `.claude/ux-research/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If UX research framework doesn't exist in the project:
```bash
mkdir -p .claude/ux-research
cp ~/.claude/process-templates-n-prompts/ux-research/*.md .claude/ux-research/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read ux-research-prompt.md** - Understand the UX research philosophy and methodology
   - Focus on user-centered design and evidence-based decisions
   - Review qualitative and quantitative research methods
   - Understand accessibility, inclusivity, and ethical research practices

2. **Load ux-research-template.md** - Use as the structure for research documentation
   - Reference for research plan and protocol templates
   - Use participant recruitment and screening templates
   - Follow analysis and insight documentation templates
   - Use recommendation and action item formats

3. **Follow ux-research-checklist.md** - Execute phases systematically
   - Start with Phase 0: Research Planning & Question Definition
   - Check off items as completed
   - Document research findings and insights
   - Track research impact and design decisions

## Execution Instructions

### Phase 0: Research Planning & Question Definition (MANDATORY FIRST)
- Define research objectives and key questions
- Identify target user segments and participant criteria
- Choose appropriate research methods and tools
- Plan research timeline and resource requirements
- Review ethical considerations and consent procedures
- Establish success metrics and evaluation criteria

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Participant Recruitment & Screening
- Phase 2: Research Protocol Development & Testing
- Phase 3: Data Collection & User Studies
- Phase 4: Analysis & Insight Generation
- Phase 5: Findings Documentation & Presentation
- Phase 6: Design Recommendations & Implementation
- Phase 7: Impact Measurement & Follow-up Research

## Key Principles

1. **ALWAYS start with clear research questions and hypotheses**
2. **Choose research methods that best answer your questions**
3. **Recruit diverse participants representative of your users**
4. **Maintain ethical standards and obtain proper consent**
5. **Analyze data objectively and avoid confirmation bias**
6. **Translate findings into actionable design recommendations**

## UX Research Goals
- Clear understanding of user needs, behaviors, and pain points
- Evidence-based insights to inform design decisions
- Validated design concepts and usability improvements
- Inclusive research practices representing diverse user groups
- Measurable impact on user experience and business metrics
- Continuous user feedback loop and research iteration

## Progress Tracking
Update the ux-research-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. research-plan.md - Comprehensive research strategy and methodology
2. participant-profiles.md - User personas and recruitment criteria
3. research-protocols/ - Interview guides, survey questions, and testing scripts
4. raw-data/ - Research session recordings, notes, and responses
5. analysis-insights.md - Key findings, patterns, and user insights
6. design-recommendations.md - Actionable improvement recommendations
7. impact-measurement.md - Research impact tracking and metrics
8. CHANGELOG.md - Document all research activities and findings

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Users don't care about your assumptions, they care about their experience. Listen deeply, observe carefully, design empathetically, measure impact.