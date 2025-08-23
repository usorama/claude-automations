# /manifest-status Command - Manifest Health Check & Update

## Purpose
Check, validate, and update all project manifests to ensure they accurately reflect the current state of your codebase. Identifies stale manifests and missing coverage.

## Usage
```bash
/manifest-status          # Check all manifests
/manifest-status update   # Update all manifests
/manifest-status check    # Validation only
/manifest-status create   # Create missing manifests
```

## What It Checks

### 1. **Manifest Freshness**
```yaml
Checks:
- Last modified date vs codebase changes
- New files/features not in manifests
- Deleted items still in manifests
- Version mismatches
- Dependency updates
```

### 2. **Manifest Coverage**
```yaml
Required Manifests:
- project-manifest.json     # Overall project structure
- api-manifest.json         # API endpoints & contracts
- database-manifest.json    # Schema & migrations
- component-manifest.json   # UI components inventory
- test-manifest.json        # Test coverage mapping
- security-manifest.json    # Security policies & checks
- deployment-manifest.json  # Deployment configuration
- dependencies-manifest.json # Package dependencies
```

### 3. **Manifest Accuracy**
- Routes match actual implementation
- Database schema matches models
- API documentation matches code
- Component props match usage
- Test coverage matches reality

## Implementation

```javascript
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class ManifestManager {
  constructor() {
    this.manifestDir = '.claude/manifests';
    this.projectRoot = process.cwd();
    this.manifests = {
      'project-manifest.json': this.analyzeProject,
      'api-manifest.json': this.analyzeAPIs,
      'database-manifest.json': this.analyzeDatabase,
      'component-manifest.json': this.analyzeComponents,
      'test-manifest.json': this.analyzeTests,
      'security-manifest.json': this.analyzeSecurity,
      'deployment-manifest.json': this.analyzeDeployment,
      'dependencies-manifest.json': this.analyzeDependencies
    };
  }

  async checkStatus() {
    console.log('📊 MANIFEST STATUS CHECK');
    console.log('═'.repeat(60));
    
    const status = {
      total: Object.keys(this.manifests).length,
      exists: 0,
      stale: 0,
      missing: 0,
      current: 0,
      coverage: {}
    };

    for (const [manifestFile, analyzer] of Object.entries(this.manifests)) {
      const manifestPath = path.join(this.manifestDir, manifestFile);
      
      if (fs.existsSync(manifestPath)) {
        status.exists++;
        const freshness = await this.checkFreshness(manifestPath);
        
        if (freshness.isStale) {
          status.stale++;
          console.log(`⚠️  ${manifestFile}: STALE (${freshness.daysSinceUpdate} days old)`);
          console.log(`   Missing: ${freshness.missingItems.join(', ')}`);
        } else {
          status.current++;
          console.log(`✅ ${manifestFile}: CURRENT`);
        }
        
        status.coverage[manifestFile] = freshness.coverage;
      } else {
        status.missing++;
        console.log(`❌ ${manifestFile}: MISSING`);
      }
    }
    
    this.printSummary(status);
    return status;
  }

  async checkFreshness(manifestPath) {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    const stats = fs.statSync(manifestPath);
    const daysSinceUpdate = Math.floor((Date.now() - stats.mtime) / (1000 * 60 * 60 * 24));
    
    // Check for recent code changes
    const recentChanges = this.getRecentChanges(daysSinceUpdate);
    const missingItems = this.findMissingItems(manifest, recentChanges);
    
    return {
      isStale: missingItems.length > 0 || daysSinceUpdate > 7,
      daysSinceUpdate,
      missingItems,
      coverage: this.calculateCoverage(manifest)
    };
  }

  getRecentChanges(days) {
    try {
      const gitLog = execSync(
        `git log --since="${days} days ago" --name-only --pretty=format: | sort -u | grep -E "\\.(js|ts|jsx|tsx|py|go)$"`,
        { encoding: 'utf8' }
      );
      return gitLog.split('\n').filter(Boolean);
    } catch {
      return [];
    }
  }

  findMissingItems(manifest, recentChanges) {
    const missing = [];
    
    // Check if recent changes are reflected in manifest
    for (const file of recentChanges) {
      const inManifest = this.isFileInManifest(file, manifest);
      if (!inManifest) {
        missing.push(file);
      }
    }
    
    return missing;
  }

  calculateCoverage(manifest) {
    // Calculate what percentage of codebase is documented
    const totalFiles = this.countProjectFiles();
    const documentedItems = this.countManifestItems(manifest);
    
    return Math.round((documentedItems / totalFiles) * 100);
  }

  async updateManifests() {
    console.log('🔄 UPDATING ALL MANIFESTS');
    console.log('═'.repeat(60));
    
    for (const [manifestFile, analyzer] of Object.entries(this.manifests)) {
      console.log(`\n📝 Updating ${manifestFile}...`);
      
      const manifestPath = path.join(this.manifestDir, manifestFile);
      const currentManifest = fs.existsSync(manifestPath) 
        ? JSON.parse(fs.readFileSync(manifestPath, 'utf8'))
        : {};
      
      const updatedManifest = await analyzer.call(this, currentManifest);
      
      // Merge with existing, preserving manual additions
      const finalManifest = this.mergeManifests(currentManifest, updatedManifest);
      
      // Save with metadata
      finalManifest._metadata = {
        lastUpdated: new Date().toISOString(),
        version: (currentManifest._metadata?.version || 0) + 1,
        autoGenerated: true,
        manualEdits: currentManifest._metadata?.manualEdits || []
      };
      
      fs.writeFileSync(
        manifestPath,
        JSON.stringify(finalManifest, null, 2)
      );
      
      console.log(`   ✅ Updated with ${Object.keys(updatedManifest).length} entries`);
    }
  }

  // Analyzer functions for each manifest type
  async analyzeProject(current) {
    const projectStructure = {
      name: this.getProjectName(),
      type: this.detectProjectType(),
      structure: this.analyzeDirectoryStructure(),
      entryPoints: this.findEntryPoints(),
      configuration: this.findConfigFiles(),
      scripts: this.getPackageScripts()
    };
    
    return projectStructure;
  }

  async analyzeAPIs(current) {
    const apis = {
      endpoints: [],
      graphql: {},
      websockets: [],
      authentication: {}
    };
    
    // Find all API routes
    const routeFiles = this.findFiles(['**/routes/**', '**/api/**', '**/controllers/**']);
    
    for (const file of routeFiles) {
      const endpoints = this.extractEndpoints(file);
      apis.endpoints.push(...endpoints);
    }
    
    return apis;
  }

  async analyzeDatabase(current) {
    const database = {
      type: this.detectDatabaseType(),
      schemas: this.findSchemas(),
      migrations: this.findMigrations(),
      models: this.findModels(),
      seeds: this.findSeeds()
    };
    
    return database;
  }

  async analyzeComponents(current) {
    const components = {
      ui: this.findUIComponents(),
      pages: this.findPages(),
      layouts: this.findLayouts(),
      hooks: this.findHooks(),
      utilities: this.findUtilities()
    };
    
    return components;
  }

  async analyzeTests(current) {
    const tests = {
      unit: this.findTests('unit'),
      integration: this.findTests('integration'),
      e2e: this.findTests('e2e'),
      coverage: this.getTestCoverage(),
      commands: this.getTestCommands()
    };
    
    return tests;
  }

  async analyzeSecurity(current) {
    const security = {
      authentication: this.findAuthImplementation(),
      authorization: this.findAuthzImplementation(),
      encryption: this.findEncryption(),
      validation: this.findValidation(),
      dependencies: await this.checkVulnerabilities()
    };
    
    return security;
  }

  async analyzeDeployment(current) {
    const deployment = {
      environments: this.findEnvironments(),
      cicd: this.findCICDConfig(),
      docker: this.findDockerConfig(),
      infrastructure: this.findInfrastructure(),
      monitoring: this.findMonitoring()
    };
    
    return deployment;
  }

  async analyzeDependencies(current) {
    const deps = {
      production: {},
      development: {},
      peer: {},
      outdated: [],
      vulnerabilities: []
    };
    
    // Read package.json or equivalent
    if (fs.existsSync('package.json')) {
      const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      deps.production = pkg.dependencies || {};
      deps.development = pkg.devDependencies || {};
      deps.peer = pkg.peerDependencies || {};
      
      // Check for outdated
      try {
        const outdated = execSync('npm outdated --json', { encoding: 'utf8' });
        deps.outdated = JSON.parse(outdated);
      } catch {}
    }
    
    return deps;
  }

  printSummary(status) {
    console.log('\n' + '═'.repeat(60));
    console.log('📊 MANIFEST SUMMARY');
    console.log('═'.repeat(60));
    console.log(`Total Manifests: ${status.total}`);
    console.log(`✅ Current: ${status.current}`);
    console.log(`⚠️  Stale: ${status.stale}`);
    console.log(`❌ Missing: ${status.missing}`);
    
    if (status.stale > 0 || status.missing > 0) {
      console.log('\n💡 Recommendation: Run `/manifest-status update` to refresh');
    }
    
    console.log('\n📈 Coverage by Manifest:');
    for (const [manifest, coverage] of Object.entries(status.coverage)) {
      const bar = '█'.repeat(Math.floor(coverage / 10)) + '░'.repeat(10 - Math.floor(coverage / 10));
      console.log(`   ${manifest.padEnd(30)} ${bar} ${coverage}%`);
    }
  }
}

module.exports = ManifestManager;
```

## Output Example

```bash
/manifest-status

📊 MANIFEST STATUS CHECK
════════════════════════════════════════════════════════════

✅ project-manifest.json: CURRENT
⚠️  api-manifest.json: STALE (12 days old)
   Missing: src/api/chat.ts, src/api/metrics.ts
✅ database-manifest.json: CURRENT
❌ component-manifest.json: MISSING
⚠️  test-manifest.json: STALE (8 days old)
   Missing: tests/chat.spec.ts
✅ security-manifest.json: CURRENT
✅ deployment-manifest.json: CURRENT
❌ dependencies-manifest.json: MISSING

════════════════════════════════════════════════════════════
📊 MANIFEST SUMMARY
════════════════════════════════════════════════════════════
Total Manifests: 8
✅ Current: 4
⚠️  Stale: 2
❌ Missing: 2

💡 Recommendation: Run `/manifest-status update` to refresh

📈 Coverage by Manifest:
   project-manifest.json          ████████░░ 82%
   api-manifest.json              ██████░░░░ 65%
   database-manifest.json         █████████░ 91%
   test-manifest.json             ███████░░░ 73%
   security-manifest.json         ████████░░ 88%
   deployment-manifest.json       █████████░ 94%
```

## Features

### 1. **Automatic Staleness Detection**
- Checks git history for recent changes
- Compares manifest age with code changes
- Identifies missing new files

### 2. **Coverage Calculation**
- Shows what % of codebase is documented
- Identifies gaps in documentation
- Tracks improvement over time

### 3. **Smart Merging**
- Preserves manual additions
- Updates automatic content
- Version tracking

### 4. **Comprehensive Analysis**
- Scans entire codebase
- Detects project type
- Finds all relevant files

## Integration with Workflow

```bash
# During development
/manifest-status         # Check if manifests are current

# After major changes
/manifest-status update  # Update all manifests

# Before deployment
/manifest-status check   # Validate everything is documented

# For new projects
/manifest-status create  # Create initial manifests
```

## Best Practices

1. **Run weekly** - Keep manifests fresh
2. **After features** - Update after new functionality
3. **Before releases** - Ensure documentation is complete
4. **Git hooks** - Auto-check on commits
5. **CI/CD integration** - Validate in pipeline

This ensures manifests stay current and actually useful!