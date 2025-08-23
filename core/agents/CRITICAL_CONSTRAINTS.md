# Critical Constraints for All Agents

## Manifest Requirements

All agents MUST read and understand these manifests before starting any implementation work:

### Required Reading
```
@.claude/manifests/CODEBASE_MANIFEST.yaml    # Overall codebase structure
@.claude/manifests/FUNCTION_REGISTRY.md      # All functions and their purposes
@.claude/manifests/EXPORT_REGISTRY.json      # Module exports and dependencies
@.claude/manifests/CODE_PATTERNS.md          # Common patterns and conventions
@.claude/manifests/DEPENDENCY_GRAPH.json     # Module relationships
@.claude/manifests/ERROR_HANDLING.md         # Error handling patterns
@.claude/manifests/PROJECT_CONTEXT.yaml      # Project-specific context
@.claude/manifests/TYPE_DEFINITIONS.ts       # TypeScript type definitions
```

### Why This Matters
1. **Prevents Silent Failures** - Understanding existing patterns prevents introducing bugs
2. **Maintains Consistency** - Following established patterns keeps code maintainable
3. **Enables Intelligence** - Knowing the codebase structure enables better decisions
4. **Avoids Duplication** - Understanding existing functions prevents reinventing wheels

### How to Use Manifests
1. **Before Starting**: Read relevant manifests for the area you're working in
2. **During Work**: Reference manifests to ensure consistency
3. **After Changes**: Update manifests if you've added new functions/patterns

### Enforcement
- GitHub Actions will validate that code follows manifest patterns
- PR reviews will check manifest compliance
- Silent failure detection will catch violations

## Agent Behavior Requirements

### 1. Context Loading
Before any implementation:
```bash
python3 ~/.claude/hooks/pre-agent-context.py
```

### 2. Branch Management
Use intelligent branching:
```bash
.claude/hooks/suggest-branch.sh
```

### 3. Checkpoint Commits
Create checkpoints after significant work:
```bash
python3 ~/.claude/hooks/auto-checkpoint-hook.py --now
```

### 4. Pattern Compliance
- Follow patterns documented in CODE_PATTERNS.md
- Use existing utilities from FUNCTION_REGISTRY.md
- Maintain type consistency with TYPE_DEFINITIONS.ts

### 5. Error Handling
- Never use empty catch blocks
- Always log errors appropriately
- Follow ERROR_HANDLING.md patterns

## Integration Points

### Session Lifecycle
Agents should be aware of session management:
- Auto-commits every 30 minutes
- Smart commits on significant changes
- PR creation when work is complete

### Git Branch Intelligence
Agents should use smart branching:
- Context-aware branch names
- Automatic branch creation for new work
- Smart switching with state preservation

### Code Intelligence
Agents must leverage:
- Function registry for existing utilities
- Export registry for module interfaces
- Dependency graph for impact analysis
- Type definitions for consistency

## Validation Checklist

Before completing any task, verify:
- [ ] Manifests were read and understood
- [ ] Existing patterns were followed
- [ ] No silent failures introduced
- [ ] Tests pass (if applicable)
- [ ] Documentation updated (if needed)
- [ ] Checkpoint commit created

---

**Note**: This document should be the foundation for all agent work. Agents that don't follow these constraints risk introducing bugs, inconsistencies, and technical debt.