# 🎯 Reusable Prompts Library

## Overview
A collection of battle-tested, versioned prompts for common development workflows with Claude Code. Each prompt is designed to be universally applicable across different project types while maintaining flexibility for specific needs.

## Structure
```
reusable-prompts/
├── daily/              # Daily workflow prompts
│   └── start-prompt.md # Project continuation protocol
├── analysis/           # Code analysis prompts
├── development/        # Feature development prompts
├── testing/            # Testing and QA prompts
├── documentation/      # Documentation prompts
└── README.md          # This file
```

## Available Prompts

### Daily Workflow
| Prompt | Version | Command | Description |
|--------|---------|---------|-------------|
| start-prompt | 1.1.0 | `/start-prompt` | Analyzes project state, ensures git safety, creates action plan |
| continuation-prompt | 1.1.0 | `/continuation-prompt` | Commits all work, pushes to remote, generates handoff package |

### Coming Soon
- `/analyze-codebase` - Deep codebase analysis
- `/review-pr` - Comprehensive PR review
- `/test-suite` - Test suite analysis and improvement
- `/document-api` - API documentation generation
- `/refactor-plan` - Refactoring strategy creation

## Using Prompts

### As Slash Commands
Most prompts are available as slash commands:
```
/start-prompt
/start-prompt focus on testing
/continuation-prompt
/continuation-prompt full --save
```

### Direct Usage
Copy the prompt content from the `.md` file and paste into Claude Code with your specific parameters.

### With Arguments
Many prompts accept optional arguments for customization:
```
/start-prompt continue auth feature
/continuation-prompt compact --prism
```

### Continuation Workflow
1. Before ending a session: Run `/continuation-prompt`
2. Copy the generated package
3. Start new Claude Code session
4. Paste the package as your first message
5. Claude will read critical files and continue exactly where you left off

## Prompt Standards

### Metadata Format
Every prompt includes:
```yaml
name: prompt-name
version: X.Y.Z
created_by: Author
created_date: YYYY-MM-DD
last_modified: YYYY-MM-DD
category: category-name
tags: [tag1, tag2]
changelog:
  - vX.Y.Z (date): Description
```

### Versioning
- **Major (X.0.0)**: Breaking changes to prompt structure
- **Minor (0.X.0)**: New features or capabilities
- **Patch (0.0.X)**: Bug fixes or minor improvements

### Quality Criteria
Each prompt must:
1. Be project-type agnostic (work with any codebase)
2. Include clear usage examples
3. Provide structured output format
4. Handle edge cases gracefully
5. Execute efficiently (parallel operations where possible)
6. Integrate with Claude Code features (TodoWrite, etc.)
7. Respect user's CLAUDE.md instructions

## Contributing New Prompts

### Template
```markdown
# [Prompt Title]

## Metadata
```yaml
name: prompt-name
version: 1.0.0
created_by: Your Name
created_date: YYYY-MM-DD
last_modified: YYYY-MM-DD
category: category
tags: [relevant, tags]
changelog:
  - v1.0.0 (YYYY-MM-DD): Initial implementation
```

## Purpose
[Clear description of what this prompt accomplishes]

## Usage
```
/command-name [arguments]
```

## Prompt Content
[The actual prompt instructions]

## Output Format
[Expected output structure]

## Notes
[Any additional context or limitations]
```

### Submission Process
1. Create prompt in appropriate category folder
2. Test thoroughly across different project types
3. Add slash command if applicable
4. Update this README with prompt details
5. Commit with message: `feat(prompts): Add [prompt-name] v1.0.0`

## Best Practices

### DO
- ✅ Make prompts reusable across projects
- ✅ Include version tracking
- ✅ Provide clear examples
- ✅ Use parallel execution for discovery
- ✅ Create structured output
- ✅ Integrate with Claude Code tools
- ✅ Handle missing files gracefully

### DON'T
- ❌ Hard-code project-specific paths
- ❌ Assume specific technology stack
- ❌ Create overly complex prompts
- ❌ Forget error handling
- ❌ Skip metadata section
- ❌ Ignore user's custom instructions

## Integration with Claude Code

These prompts are designed to work seamlessly with:
- **TodoWrite**: For task management
- **Git operations**: For version control
- **File operations**: For code analysis
- **MCP servers**: For extended capabilities
- **User's CLAUDE.md**: For custom instructions

## Maintenance

### Updating Prompts
1. Increment version number appropriately
2. Update last_modified date
3. Add changelog entry
4. Test changes thoroughly
5. Update slash command if needed

### Deprecation
When deprecating a prompt:
1. Mark as deprecated in metadata
2. Provide migration path
3. Keep for at least 3 months
4. Update documentation

## Support

For issues or suggestions:
1. Check existing prompts for similar functionality
2. Review prompt standards above
3. Create detailed improvement proposal
4. Include use cases and examples

---

*Last Updated: 2025-08-26*
*Prompt Library Version: 1.0.0*