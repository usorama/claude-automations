# /manifests Command - Manifest Management Hub

## Purpose
Central command for all manifest operations - check, update, view, and manage project manifests.

## Usage
```bash
/manifests              # Show all manifest status
/manifests status       # Detailed status check
/manifests update       # Update stale manifests
/manifests refresh      # Quick refresh all
/manifests view [type]  # View specific manifest
/manifests init         # Create initial manifests
```

## What Are Manifests?

**Manifests are living documentation** that map your entire codebase:
- What exists where
- How things connect
- What's tested vs not
- Security policies
- Deployment configs
- Dependencies

## Why Manifests Matter

### 1. **AI Context**
Claude Code uses manifests to understand your project quickly without scanning everything repeatedly.

### 2. **Team Knowledge**
New developers can understand the project structure instantly.

### 3. **Coverage Tracking**
See what's tested, documented, secured at a glance.

### 4. **Change Detection**
Know what changed between versions.

### 5. **Automation**
CI/CD and tools can use manifests for smart decisions.

## Manifest Types

| Manifest | Purpose | Key Information |
|----------|---------|-----------------|
| **project-manifest.json** | Overall structure | Entry points, config, scripts |
| **api-manifest.json** | API documentation | Endpoints, methods, contracts |
| **database-manifest.json** | Data layer | Schema, models, migrations |
| **component-manifest.json** | UI inventory | Components, pages, layouts |
| **test-manifest.json** | Test coverage | What's tested, gaps, commands |
| **security-manifest.json** | Security posture | Auth, encryption, validation |
| **deployment-manifest.json** | Deploy config | Environments, CI/CD, infra |
| **dependencies-manifest.json** | Package tracking | Deps, versions, vulnerabilities |

## Manifest Lifecycle

```mermaid
graph LR
    A[Project Start] --> B[/manifests init]
    B --> C[Development]
    C --> D[/manifests update]
    D --> C
    C --> E[Before Deploy]
    E --> F[/manifests refresh]
    F --> G[Deploy]
    G --> C
```

## Best Practices

### 1. **Keep Manifests Fresh**
```bash
# Weekly update
/manifests status
/manifests update  # If stale
```

### 2. **Manual Additions**
```json
{
  "_manual": {
    "notes": "Custom auth flow documented here",
    "warnings": "Don't modify the legacy API",
    "todo": "Refactor user service by Q4"
  }
}
```

### 3. **Git Integration**
```bash
# Always commit manifest updates
git add .claude/manifests/
git commit -m "Update manifests after feature X"
```

### 4. **CI/CD Validation**
```yaml
- name: Check Manifests
  run: |
    claude /manifests status
    test $? -eq 0 || exit 1
```

## Common Workflows

### New Feature Development
```bash
/2.3feature         # Build feature
/3.2test           # Test it
/manifests update  # Document it
```

### Pre-Deployment Check
```bash
/manifests status  # Check freshness
/manifests update  # Update if needed
/4.1deploy        # Deploy
```

### Onboarding New Developer
```bash
/manifests view project    # Show structure
/manifests view api        # Show endpoints
/manifests view test       # Show how to test
```

### Weekly Maintenance
```bash
/manifests status          # Check health
/manifests update          # Update stale
git commit -am "Weekly manifest update"
```

## Manifest Quality Indicators

### ✅ Good Manifests
- Updated within last 7 days
- Coverage > 80%
- Includes manual notes
- Version controlled
- Used by automation

### ⚠️ Warning Signs
- Last updated > 2 weeks ago
- Coverage < 60%
- Missing key sections
- Not in git
- Never referenced

### ❌ Bad Manifests
- Created once, never updated
- Auto-generated only
- No manual documentation
- Incorrect information
- Ignored by team

## Quick Reference

```bash
# Check if manifests need updating
/manifest-status

# Update all stale manifests
/manifest-update

# Quick refresh everything
/manifest-refresh

# View specific manifest
cat .claude/manifests/api-manifest.json | jq

# Find what changed
git diff .claude/manifests/
```

## Integration with Claude Code

Manifests enhance Claude Code's abilities:
1. **Faster context loading** - Pre-mapped structure
2. **Better suggestions** - Knows your patterns
3. **Smarter testing** - Understands coverage
4. **Accurate updates** - Knows what exists
5. **Safe refactoring** - Understands dependencies

## Philosophy

> "Manifests are not documentation you write once and forget. They're living maps of your codebase that grow with your project."

Keep them fresh, and they'll save you hours of explanation and investigation.

---

**Pro Tip**: Add `/manifest-refresh` to your git pre-commit hook to ensure manifests are always current!