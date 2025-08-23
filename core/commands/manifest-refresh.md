# /manifest-refresh Command - Quick Manifest Sync

## Purpose
Simple, fast command to refresh all manifests with current codebase state. One command, no options, just works.

## Usage
```bash
/manifest-refresh
```

That's it! No arguments needed.

## What It Does

1. **Scans** entire codebase
2. **Updates** all manifests in `.claude/manifests/`
3. **Preserves** manual additions (marked with `_manual`)
4. **Reports** what changed
5. **Done** in seconds

## Quick Implementation

```javascript
async function refreshManifests() {
  console.log('🔄 Refreshing all manifests...\n');
  
  const manifests = [
    'project',
    'api', 
    'database',
    'component',
    'test',
    'security',
    'deployment',
    'dependencies'
  ];
  
  let totalUpdates = 0;
  
  for (const type of manifests) {
    const updates = await updateManifest(type);
    totalUpdates += updates;
    
    if (updates > 0) {
      console.log(`✅ ${type}-manifest.json: ${updates} updates`);
    } else {
      console.log(`✓  ${type}-manifest.json: current`);
    }
  }
  
  console.log(`\n✨ Refreshed ${manifests.length} manifests with ${totalUpdates} total updates`);
  console.log(`📁 Location: .claude/manifests/`);
}
```

## Example Output

```bash
/manifest-refresh

🔄 Refreshing all manifests...

✅ project-manifest.json: 3 updates
✅ api-manifest.json: 7 updates
✓  database-manifest.json: current
✅ component-manifest.json: 4 updates
✅ test-manifest.json: 12 updates
✓  security-manifest.json: current
✓  deployment-manifest.json: current
✅ dependencies-manifest.json: 2 updates

✨ Refreshed 8 manifests with 28 total updates
📁 Location: .claude/manifests/
```

## When to Use

- **After feature completion** - Capture new additions
- **Before deployment** - Ensure docs are current
- **Weekly routine** - Keep manifests fresh
- **After refactoring** - Update structure changes
- **Before handoff** - Document for team

## Auto-Refresh Integration

Add to your workflow:

```javascript
// After running tests
/3.2test
/manifest-refresh  // Auto-document test changes

// After adding features
/2.3feature
/manifest-refresh  // Capture new components

// Before deployment
/manifest-refresh
/4.1deploy
```

Simple, fast, effective!