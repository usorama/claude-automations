#!/usr/bin/env node

/**
 * Smart Project Type Detection
 * Determines if a project is greenfield (new) or brownfield (existing)
 * with intelligent scaffolding recognition
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class ProjectDetector {
  constructor(projectPath = process.cwd()) {
    this.projectPath = projectPath;
    this.indicators = {
      brownfield: 0,
      greenfield: 0,
      confidence: 0
    };
    this.detectedFeatures = [];
  }

  // Check if directory is empty or only has hidden files
  isEmptyOrMinimal() {
    const files = fs.readdirSync(this.projectPath);
    const visibleFiles = files.filter(f => !f.startsWith('.'));
    
    if (visibleFiles.length === 0) {
      this.detectedFeatures.push('Empty directory');
      return true;
    }
    
    // Only README or LICENSE type files
    const minimalFiles = ['README.md', 'LICENSE', '.gitignore'];
    if (visibleFiles.every(f => minimalFiles.includes(f))) {
      this.detectedFeatures.push('Minimal setup (README/LICENSE only)');
      return true;
    }
    
    return false;
  }

  // Detect common scaffolding patterns
  isScaffolding() {
    const scaffoldingPatterns = {
      nextjs: {
        files: ['next.config.js', 'pages/_app.js', 'pages/index.js'],
        folders: ['pages', 'public', 'styles'],
        indicator: 'Next.js scaffolding'
      },
      'create-react-app': {
        files: ['src/App.js', 'src/index.js', 'public/index.html'],
        folders: ['src', 'public'],
        indicator: 'Create React App scaffolding'
      },
      vite: {
        files: ['vite.config.js', 'index.html', 'src/main.jsx'],
        folders: ['src', 'public'],
        indicator: 'Vite scaffolding'
      },
      express: {
        files: ['app.js', 'bin/www'],
        folders: ['routes', 'views', 'public'],
        indicator: 'Express generator scaffolding'
      },
      django: {
        files: ['manage.py', 'settings.py', 'urls.py'],
        folders: [],
        indicator: 'Django scaffolding'
      },
      rails: {
        files: ['Gemfile', 'Rakefile', 'config.ru'],
        folders: ['app', 'config', 'db'],
        indicator: 'Rails scaffolding'
      }
    };

    for (const [framework, pattern] of Object.entries(scaffoldingPatterns)) {
      let matchCount = 0;
      const totalChecks = pattern.files.length + pattern.folders.length;
      
      // Check files
      for (const file of pattern.files) {
        if (this.fileExists(file)) matchCount++;
      }
      
      // Check folders
      for (const folder of pattern.folders) {
        if (this.folderExists(folder)) matchCount++;
      }
      
      // If we match > 70% of the pattern, it's likely scaffolding
      if (matchCount / totalChecks > 0.7) {
        // But check if there's custom code beyond scaffolding
        const hasCustomCode = this.hasBusinessLogic();
        if (!hasCustomCode) {
          this.detectedFeatures.push(pattern.indicator);
          return true;
        }
      }
    }
    
    return false;
  }

  // Check for actual business logic vs boilerplate
  hasBusinessLogic() {
    const businessIndicators = [
      'models/',
      'services/',
      'controllers/',
      'api/',
      'database/',
      'migrations/',
      'seeds/',
      'utils/',
      'helpers/',
      'lib/',
      'domain/',
      'features/',
      'modules/'
    ];

    let customCodeCount = 0;
    
    for (const indicator of businessIndicators) {
      if (this.folderExists(indicator)) {
        const files = this.countFilesInFolder(indicator);
        if (files > 2) { // More than just index/example files
          customCodeCount++;
        }
      }
    }

    // Check for custom API endpoints
    if (this.folderExists('pages/api') || this.folderExists('routes')) {
      const apiFiles = this.countFilesInFolder('pages/api') || this.countFilesInFolder('routes');
      if (apiFiles > 3) customCodeCount++;
    }

    // Check for real tests (not examples)
    if (this.hasRealTests()) customCodeCount++;

    // Check for environment configuration
    if (this.hasRealConfiguration()) customCodeCount++;

    return customCodeCount >= 2;
  }

  // Check git history depth
  getGitInfo() {
    try {
      const commitCount = execSync('git rev-list --count HEAD', {
        cwd: this.projectPath,
        encoding: 'utf8'
      }).trim();
      
      const contributorCount = execSync('git shortlog -sn --no-merges | wc -l', {
        cwd: this.projectPath,
        encoding: 'utf8'
      }).trim();
      
      const firstCommitDate = execSync('git log --reverse --format=%ci | head -1', {
        cwd: this.projectPath,
        encoding: 'utf8'
      }).trim();
      
      return {
        commits: parseInt(commitCount),
        contributors: parseInt(contributorCount),
        age: this.calculateAge(firstCommitDate),
        hasGit: true
      };
    } catch {
      return { commits: 0, contributors: 0, age: 0, hasGit: false };
    }
  }

  // Check for real tests vs example tests
  hasRealTests() {
    const testFolders = ['tests', '__tests__', 'test', 'spec'];
    
    for (const folder of testFolders) {
      if (this.folderExists(folder)) {
        const testFiles = this.getFilesRecursive(path.join(this.projectPath, folder));
        const realTests = testFiles.filter(f => 
          !f.includes('example') && 
          !f.includes('sample') && 
          !f.includes('.spec.example')
        );
        
        if (realTests.length > 2) {
          this.detectedFeatures.push(`${realTests.length} test files`);
          return true;
        }
      }
    }
    
    return false;
  }

  // Check for real configuration vs defaults
  hasRealConfiguration() {
    const configIndicators = [
      '.env.production',
      '.env.local',
      'config/database.yml',
      'config/secrets.yml',
      'appsettings.json',
      'config/production.json'
    ];

    for (const config of configIndicators) {
      if (this.fileExists(config)) {
        this.detectedFeatures.push('Production configuration');
        return true;
      }
    }

    // Check if .env has real values (not just examples)
    if (this.fileExists('.env')) {
      const content = fs.readFileSync(path.join(this.projectPath, '.env'), 'utf8');
      if (!content.includes('your_') && !content.includes('example_') && !content.includes('CHANGE_ME')) {
        this.detectedFeatures.push('Configured environment');
        return true;
      }
    }

    return false;
  }

  // Main detection logic
  detect() {
    console.log('🔍 Analyzing project structure...\n');

    // Check if empty/minimal
    if (this.isEmptyOrMinimal()) {
      this.indicators.greenfield = 100;
      this.indicators.confidence = 100;
      return this.generateReport('greenfield');
    }

    // Check git history
    const gitInfo = this.getGitInfo();
    if (!gitInfo.hasGit || gitInfo.commits < 5) {
      this.indicators.greenfield += 30;
      this.detectedFeatures.push(gitInfo.hasGit ? `Only ${gitInfo.commits} commits` : 'No git repository');
    } else if (gitInfo.commits > 50) {
      this.indicators.brownfield += 40;
      this.detectedFeatures.push(`${gitInfo.commits} commits, ${gitInfo.contributors} contributors`);
    } else if (gitInfo.commits > 20) {
      this.indicators.brownfield += 20;
      this.detectedFeatures.push(`${gitInfo.commits} commits`);
    }

    // Check if it's just scaffolding
    if (this.isScaffolding()) {
      this.indicators.greenfield += 50;
    }

    // Check for business logic
    if (this.hasBusinessLogic()) {
      this.indicators.brownfield += 40;
      this.detectedFeatures.push('Custom business logic detected');
    }

    // Check for documentation
    const docFiles = this.countDocumentation();
    if (docFiles > 5) {
      this.indicators.brownfield += 20;
      this.detectedFeatures.push(`${docFiles} documentation files`);
    }

    // Check for CI/CD
    if (this.hasCICD()) {
      this.indicators.brownfield += 15;
      this.detectedFeatures.push('CI/CD pipeline configured');
    }

    // Check for database
    if (this.hasDatabase()) {
      this.indicators.brownfield += 25;
      this.detectedFeatures.push('Database/migrations present');
    }

    // Calculate confidence
    const total = this.indicators.brownfield + this.indicators.greenfield;
    const winner = this.indicators.brownfield > this.indicators.greenfield ? 'brownfield' : 'greenfield';
    this.indicators.confidence = Math.round((Math.max(this.indicators.brownfield, this.indicators.greenfield) / total) * 100);

    return this.generateReport(winner);
  }

  // Helper methods
  fileExists(file) {
    return fs.existsSync(path.join(this.projectPath, file));
  }

  folderExists(folder) {
    const fullPath = path.join(this.projectPath, folder);
    return fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory();
  }

  countFilesInFolder(folder) {
    try {
      const fullPath = path.join(this.projectPath, folder);
      return fs.readdirSync(fullPath).filter(f => !f.startsWith('.')).length;
    } catch {
      return 0;
    }
  }

  getFilesRecursive(dir, fileList = []) {
    try {
      const files = fs.readdirSync(dir);
      
      for (const file of files) {
        const filePath = path.join(dir, file);
        if (fs.statSync(filePath).isDirectory()) {
          this.getFilesRecursive(filePath, fileList);
        } else {
          fileList.push(filePath);
        }
      }
    } catch {}
    
    return fileList;
  }

  countDocumentation() {
    const docs = this.getFilesRecursive(this.projectPath)
      .filter(f => f.endsWith('.md') || f.endsWith('.rst') || f.endsWith('.txt'))
      .filter(f => !f.includes('node_modules') && !f.includes('.git'));
    return docs.length;
  }

  hasCICD() {
    return this.folderExists('.github/workflows') || 
           this.fileExists('.gitlab-ci.yml') ||
           this.fileExists('.circleci/config.yml') ||
           this.fileExists('Jenkinsfile') ||
           this.fileExists('.travis.yml');
  }

  hasDatabase() {
    return this.folderExists('migrations') ||
           this.folderExists('db') ||
           this.fileExists('schema.sql') ||
           this.fileExists('database.json') ||
           this.folderExists('prisma');
  }

  calculateAge(dateString) {
    if (!dateString) return 0;
    const date = new Date(dateString);
    const now = new Date();
    return Math.floor((now - date) / (1000 * 60 * 60 * 24));
  }

  generateReport(type) {
    return {
      type,
      confidence: this.indicators.confidence,
      features: this.detectedFeatures,
      recommendation: this.getRecommendation(type)
    };
  }

  getRecommendation(type) {
    if (type === 'greenfield') {
      return {
        mode: 'greenfield',
        entry: 'Phase 0: Discovery & Requirements',
        focus: 'What should we build?',
        workflow: 'Full planning → Architecture → Implementation'
      };
    } else {
      return {
        mode: 'brownfield',
        entry: 'Phase 0: System Assessment',
        focus: 'What do we have?',
        workflow: 'Assessment → Enhancement Planning → Safe Implementation'
      };
    }
  }
}

// CLI Interface
if (require.main === module) {
  const detector = new ProjectDetector();
  const result = detector.detect();
  
  console.log('═'.repeat(60));
  
  if (result.type === 'greenfield') {
    console.log(`🌱 Detected: New Project (confidence: ${result.confidence}%)`);
  } else {
    console.log(`🏗️  Detected: Existing Codebase (confidence: ${result.confidence}%)`);
  }
  
  if (result.features.length > 0) {
    console.log('\n📋 Key Indicators:');
    result.features.forEach(f => console.log(`   - ${f}`));
  }
  
  console.log('\n💡 Recommended Workflow:');
  console.log(`   Mode: ${result.recommendation.mode}`);
  console.log(`   Entry: ${result.recommendation.entry}`);
  console.log(`   Focus: "${result.recommendation.focus}"`);
  console.log(`   Path: ${result.recommendation.workflow}`);
  
  console.log('═'.repeat(60));
  
  // Ask for confirmation
  const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  readline.question(`\n✅ Proceed with ${result.type} workflow? (Y/n): `, (answer) => {
    const proceed = answer.toLowerCase() !== 'n';
    
    if (proceed) {
      console.log(`\n🚀 Initiating ${result.type} workflow...`);
      process.exit(0);
    } else {
      const opposite = result.type === 'greenfield' ? 'brownfield' : 'greenfield';
      console.log(`\n🔄 Switching to ${opposite} workflow...`);
      process.exit(1);
    }
    
    readline.close();
  });
}

module.exports = ProjectDetector;