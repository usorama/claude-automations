# BMAD-METHOD Resource Access Guide

## 🔗 Direct Resource Access

All BMAD agents have **DIRECT FILE ACCESS** to the complete BMAD-METHOD repository:

### Core Resource Locations
```bash
# Tasks - Executable procedures
~/.claude/.bmad-core/tasks/
├── advanced-elicitation.md
├── brownfield-create-epic.md
├── brownfield-create-story.md
├── correct-course.md
├── create-brownfield-story.md
├── create-deep-research-prompt.md
├── create-next-story.md
├── document-project.md
├── facilitate-brainstorming-session.md
├── generate-ai-frontend-prompt.md
├── index-docs.md
├── kb-mode-interaction.md
├── review-story.md
├── shard-doc.md
└── validate-next-story.md

# Templates - Reusable document structures
~/.claude/.bmad-core/templates/
├── architecture-tmpl.yaml
├── brainstorming-output-tmpl.yaml
├── brownfield-architecture-tmpl.yaml
├── brownfield-prd-tmpl.yaml
├── competitor-analysis-tmpl.yaml
├── front-end-architecture-tmpl.yaml
├── fullstack-architecture-tmpl.yaml
├── market-research-tmpl.yaml
├── prd-tmpl.yaml
├── project-brief-tmpl.yaml
├── saas-webapp-prd-tmpl.yaml
└── story-tmpl.yaml

# Workflows - Multi-step processes
~/.claude/.bmad-core/workflows/
├── brownfield-fullstack-workflow.md
├── brownfield-service-workflow.md
├── brownfield-ui-workflow.md
├── greenfield-fullstack-workflow.md
├── greenfield-service-workflow.md
└── greenfield-ui-workflow.md

# Checklists - Quality validation
~/.claude/.bmad-core/checklists/
├── architect-checklist.md
├── change-checklist.md
├── pm-checklist.md
├── po-master-checklist.md
├── story-dod-checklist.md
└── story-draft-checklist.md

# Documentation
~/.claude/.bmad-core/docs/
└── [Complete BMAD documentation]
```

## 📚 How to Use Resources

### For BMAD Agents

1. **Always READ the actual files** instead of relying on memory:
```bash
# Example: Execute a task
Read file: ~/.claude/.bmad-core/tasks/advanced-elicitation.md
# Then follow the exact procedure from the file
```

2. **Use templates by loading them directly**:
```bash
# Example: Create a PRD
Read file: ~/.claude/.bmad-core/templates/prd-tmpl.yaml
# Then populate the template with project-specific content
```

3. **Follow workflows step-by-step**:
```bash
# Example: Brownfield project
Read file: ~/.claude/.bmad-core/workflows/brownfield-fullstack-workflow.md
# Execute each phase as documented
```

4. **Validate with checklists**:
```bash
# Example: Story completion
Read file: ~/.claude/.bmad-core/checklists/story-dod-checklist.md
# Verify each item before marking complete
```

## 🤖 Agent-Specific Resource Usage

### bmad-analyst
Primary resources:
- `tasks/advanced-elicitation.md`
- `tasks/create-deep-research-prompt.md`
- `templates/market-research-tmpl.yaml`
- `templates/competitor-analysis-tmpl.yaml`

### bmad-architect
Primary resources:
- `templates/architecture-tmpl.yaml`
- `templates/fullstack-architecture-tmpl.yaml`
- `workflows/greenfield-fullstack-workflow.md`
- `checklists/architect-checklist.md`

### bmad-scrum-master
Primary resources:
- `tasks/create-next-story.md`
- `tasks/validate-next-story.md`
- `templates/story-tmpl.yaml`
- `checklists/story-dod-checklist.md`

### bmad-product-owner
Primary resources:
- `templates/prd-tmpl.yaml`
- `templates/project-brief-tmpl.yaml`
- `checklists/po-master-checklist.md`
- `tasks/document-project.md`

### bmad-developer
Primary resources:
- `tasks/generate-ai-frontend-prompt.md`
- `workflows/greenfield-service-workflow.md`
- `checklists/story-dod-checklist.md`

### bmad-qa
Primary resources:
- `checklists/story-dod-checklist.md`
- `checklists/change-checklist.md`
- `tasks/review-story.md`

### completion-enforcer
Primary resources:
- ALL checklists in `~/.claude/.bmad-core/checklists/`
- `tasks/validate-next-story.md`

## 🔄 Resource Synchronization

The BMAD resources are **automatically synchronized** from:
- **Source**: `~/Projects/useful-repos/BMAD-METHOD/`
- **Target**: `~/.claude/.bmad-core/`
- **Method**: Symbolic links (always up-to-date)

## 💡 Best Practices

1. **Always verify resource exists** before using:
```bash
ls ~/.claude/.bmad-core/tasks/[task-name].md
```

2. **Read the full resource** before executing:
```bash
Read ~/.claude/.bmad-core/[resource-path]
```

3. **Follow the exact procedures** documented in the files

4. **Cross-reference related resources** (templates with checklists, etc.)

5. **Document which resources were used** in your output

## 🚨 Important Notes

- **DO NOT rely on cached or memorized versions** - Always read the actual files
- **Resources are shared** across all BMAD agents for consistency
- **Updates to BMAD-METHOD** are immediately reflected via symlinks
- **Project-specific overrides** can be placed in `.claude/bmad-overrides/`

## 🔗 Quick Command Reference

```bash
# List all available tasks
ls ~/.claude/.bmad-core/tasks/

# List all available templates
ls ~/.claude/.bmad-core/templates/

# List all workflows
ls ~/.claude/.bmad-core/workflows/

# List all checklists
ls ~/.claude/.bmad-core/checklists/

# Read a specific resource
cat ~/.claude/.bmad-core/[category]/[filename]
```

---

**Remember**: The power of BMAD Method comes from consistent execution of proven patterns. Always use the actual resource files to ensure accuracy and completeness.