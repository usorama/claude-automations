# /manifest-update Command - Smart Manifest Refresh

## Purpose
Intelligently update all project manifests by detecting changes since last update and merging new discoveries while preserving manual additions.

## Usage
```bash
/manifest-update         # Update all stale manifests
/manifest-update all     # Force update all manifests
/manifest-update api     # Update specific manifest
/manifest-update --check # Dry run - show what would change
```

## How It Works

### 1. **Change Detection**
```javascript
// Detects what changed since last manifest update
const changes = {
  newFiles: [],       // Files created after manifest
  deletedFiles: [],   // Files removed
  modifiedFiles: [],  // Files significantly changed
  newDependencies: [], // New packages added
  newEndpoints: [],   // New API routes
  newComponents: []   // New UI components
};
```

### 2. **Smart Merging**
- Preserves manual documentation
- Updates auto-generated sections
- Adds new discoveries
- Removes obsolete entries
- Maintains custom notes

### 3. **Manifest Types Updated**

#### **project-manifest.json**
```json
{
  "_metadata": {
    "lastUpdated": "2024-08-22T10:00:00Z",
    "version": 3,
    "changesSinceLastUpdate": 47
  },
  "structure": {
    "src/": "Source code",
    "tests/": "Test files",
    "docs/": "Documentation"
  },
  "newSinceLastUpdate": [
    "src/api/chat.ts",
    "src/components/MetricsDashboard.tsx"
  ]
}
```

#### **api-manifest.json**
```json
{
  "endpoints": [
    {
      "path": "/api/chat",
      "method": "POST",
      "added": "2024-08-22",
      "status": "new",
      "tested": false
    }
  ],
  "coverage": {
    "documented": 45,
    "total": 52,
    "percentage": 86.5
  }
}
```

#### **test-manifest.json**
```json
{
  "coverage": {
    "current": 84.3,
    "lastUpdate": 79.2,
    "improvement": 5.1
  },
  "newTests": [
    "tests/chat.spec.ts",
    "tests/metrics.spec.ts"
  ],
  "missingTests": [
    "src/utils/analytics.ts",
    "src/api/export.ts"
  ]
}
```

## Implementation Pattern

```javascript
class ManifestUpdater {
  async update(specificManifest = null) {
    console.log('🔄 MANIFEST UPDATE PROCESS');
    console.log('═'.repeat(60));
    
    // 1. Detect changes since last update
    const changes = await this.detectChanges();
    
    if (changes.total === 0) {
      console.log('✅ All manifests are up to date!');
      return;
    }
    
    console.log(`📊 Found ${changes.total} changes to process:`);
    console.log(`   • New files: ${changes.newFiles.length}`);
    console.log(`   • Modified: ${changes.modifiedFiles.length}`);
    console.log(`   • Deleted: ${changes.deletedFiles.length}`);
    
    // 2. Update each manifest
    const manifests = specificManifest 
      ? [`${specificManifest}-manifest.json`]
      : this.getAllManifests();
    
    for (const manifest of manifests) {
      await this.updateManifest(manifest, changes);
    }
    
    // 3. Generate update report
    this.generateUpdateReport(changes);
  }
  
  async detectChanges() {
    const lastUpdate = this.getLastUpdateTime();
    const changes = {
      newFiles: [],
      modifiedFiles: [],
      deletedFiles: [],
      newEndpoints: [],
      newComponents: [],
      newTests: [],
      total: 0
    };
    
    // Use git to find changes
    const gitDiff = execSync(
      `git diff --name-status ${lastUpdate}..HEAD`,
      { encoding: 'utf8' }
    );
    
    // Parse git output
    gitDiff.split('\n').forEach(line => {
      const [status, file] = line.split('\t');
      if (status === 'A') changes.newFiles.push(file);
      if (status === 'M') changes.modifiedFiles.push(file);
      if (status === 'D') changes.deletedFiles.push(file);
    });
    
    // Analyze changes for specific types
    changes.newEndpoints = this.findNewEndpoints(changes.newFiles);
    changes.newComponents = this.findNewComponents(changes.newFiles);
    changes.newTests = this.findNewTests(changes.newFiles);
    
    changes.total = changes.newFiles.length + 
                   changes.modifiedFiles.length + 
                   changes.deletedFiles.length;
    
    return changes;
  }
  
  async updateManifest(manifestFile, changes) {
    console.log(`\n📝 Updating ${manifestFile}...`);
    
    const manifestPath = path.join('.claude/manifests', manifestFile);
    const existing = fs.existsSync(manifestPath) 
      ? JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
      : {};
    
    // Update based on manifest type
    const manifestType = manifestFile.split('-')[0];
    const updated = await this.updateByType(manifestType, existing, changes);
    
    // Merge intelligently
    const final = this.smartMerge(existing, updated);
    
    // Add metadata
    final._metadata = {
      lastUpdated: new Date().toISOString(),
      version: (existing._metadata?.version || 0) + 1,
      changesSinceLastUpdate: changes.total,
      autoUpdated: true
    };
    
    // Save
    fs.writeFileSync(manifestPath, JSON.stringify(final, null, 2));
    
    console.log(`   ✅ Updated with ${changes.total} changes`);
  }
  
  smartMerge(existing, updated) {
    const merged = { ...existing };
    
    // Preserve manual sections
    if (existing._manual) {
      merged._manual = existing._manual;
    }
    
    // Update auto-generated sections
    for (const [key, value] of Object.entries(updated)) {
      if (!key.startsWith('_manual')) {
        merged[key] = value;
      }
    }
    
    // Keep custom notes
    if (existing.notes) {
      merged.notes = existing.notes;
    }
    
    return merged;
  }
}
```

## Automated Update Triggers

### Option 1: Git Hooks
```bash
# .git/hooks/post-commit
#!/bin/bash
echo "Checking manifest freshness..."
claude /manifest-status --quiet
if [ $? -ne 0 ]; then
  echo "Manifests need updating. Run: /manifest-update"
fi
```

### Option 2: Scheduled Updates
```javascript
// In your project's automation
schedule.weekly(() => {
  execSync('claude /manifest-update all');
});
```

### Option 3: CI/CD Integration
```yaml
# .github/workflows/manifest-update.yml
name: Update Manifests
on:
  push:
    branches: [main]
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npx claude /manifest-update --check
```

## Benefits

1. **Always Current** - Manifests reflect actual code
2. **Change Tracking** - See what's new since last update
3. **Smart Preservation** - Keeps manual documentation
4. **Coverage Metrics** - Track documentation completeness
5. **Version History** - Know when/what changed

## Example Output

```bash
/manifest-update

🔄 MANIFEST UPDATE PROCESS
════════════════════════════════════════════════════════════

📊 Found 23 changes to process:
   • New files: 8
   • Modified: 12
   • Deleted: 3

📝 Updating project-manifest.json...
   ✅ Updated with 23 changes

📝 Updating api-manifest.json...
   ✅ Updated with 4 new endpoints

📝 Updating test-manifest.json...
   ✅ Updated with 6 new test files

📝 Updating component-manifest.json...
   ✅ Updated with 3 new components

════════════════════════════════════════════════════════════
✅ MANIFEST UPDATE COMPLETE

📊 Summary:
   • 4 manifests updated
   • 23 changes processed
   • Coverage improved from 76% to 84%
   
📁 Updated manifests in: .claude/manifests/
💡 Tip: Review changes with `git diff .claude/manifests/`
```

This provides the manual trigger you need while also showing what's changed!