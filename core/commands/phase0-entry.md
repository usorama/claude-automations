# Phase 0 Entry Point Differentiation

## Command: `/phase0` or `/0.0init`

Intelligent Phase 0 initialization that adapts based on project type detection.

## Implementation

```javascript
const ProjectDetector = require('./project-detector');
const fs = require('fs');
const path = require('path');

class Phase0Entry {
  constructor(options = {}) {
    this.brownfield = options.brownfield || false;
    this.autoDetect = options.autoDetect !== false;
    this.projectPath = process.cwd();
  }

  async initialize() {
    // Auto-detect unless explicitly set
    if (!this.brownfield && this.autoDetect) {
      const detector = new ProjectDetector(this.projectPath);
      const result = detector.detect();
      
      if (result.type === 'brownfield' && result.confidence > 70) {
        console.log('🔍 Existing codebase detected. Switching to brownfield mode...\n');
        this.brownfield = true;
      }
    }

    if (this.brownfield) {
      return this.brownfieldEntry();
    } else {
      return this.greenfieldEntry();
    }
  }

  // ===========================================
  // GREENFIELD ENTRY: "What should we build?"
  // ===========================================
  async greenfieldEntry() {
    console.log('🌱 GREENFIELD PROJECT INITIALIZATION');
    console.log('═'.repeat(60));
    console.log('Focus: "What should we build?"\n');

    const questions = {
      discovery: [
        '🎯 What problem are we solving?',
        '👥 Who are the target users?',
        '📊 What are the success metrics?',
        '⚡ What are the performance requirements?',
        '🔒 What are the security requirements?'
      ],
      technical: [
        '💻 Preferred technology stack?',
        '🏗️ Architecture preferences (monolith/microservices)?',
        '☁️ Deployment target (cloud/on-premise)?',
        '📱 Platform targets (web/mobile/desktop)?',
        '🔄 Integration requirements?'
      ],
      constraints: [
        '📅 Timeline constraints?',
        '💰 Budget constraints?',
        '👨‍💻 Team size and expertise?',
        '📝 Compliance requirements?',
        '🚀 MVP vs full product?'
      ]
    };

    // Create greenfield planning structure
    this.createGreenfieldStructure(questions);

    console.log('\n📁 Created planning structure:');
    console.log('   .claude/');
    console.log('   ├── discovery.md');
    console.log('   ├── requirements.md');
    console.log('   ├── constraints.md');
    console.log('   ├── risks.md');
    console.log('   └── decisions.md');

    return {
      mode: 'greenfield',
      nextSteps: [
        '1. Complete discovery questionnaire',
        '2. Define requirements and constraints',
        '3. Document architectural decisions',
        '4. Identify and assess risks',
        '5. Proceed to Phase 1: Architecture Design'
      ]
    };
  }

  // ===========================================
  // BROWNFIELD ENTRY: "What do we have?"
  // ===========================================
  async brownfieldEntry() {
    console.log('🏗️  BROWNFIELD PROJECT ASSESSMENT');
    console.log('═'.repeat(60));
    console.log('Focus: "What do we have?"\n');

    // Analyze existing system
    const analysis = await this.analyzeExistingSystem();
    
    console.log('📊 System Analysis Results:');
    console.log(`   Language: ${analysis.language}`);
    console.log(`   Framework: ${analysis.framework}`);
    console.log(`   Architecture: ${analysis.architecture}`);
    console.log(`   Database: ${analysis.database}`);
    console.log(`   Test Coverage: ${analysis.testCoverage}%`);
    console.log(`   Code Quality: ${analysis.codeQuality}/10`);
    console.log(`   Technical Debt: ${analysis.technicalDebt}`);
    
    const assessment = {
      current_state: [
        '🔍 What works well currently?',
        '⚠️ What are the pain points?',
        '🐛 Known bugs and issues?',
        '📈 Performance bottlenecks?',
        '🔒 Security vulnerabilities?'
      ],
      enhancement_goals: [
        '🎯 Primary enhancement objective?',
        '📊 Success metrics for enhancement?',
        '👥 User impact expectations?',
        '⏱️ Performance improvement targets?',
        '🔄 Integration requirements?'
      ],
      constraints: [
        '🚫 What cannot be changed?',
        '🔌 API compatibility requirements?',
        '💾 Data migration constraints?',
        '👥 User disruption tolerance?',
        '📅 Deployment windows?'
      ]
    };

    // Create brownfield assessment structure
    this.createBrownfieldStructure(analysis, assessment);

    console.log('\n📁 Created assessment structure:');
    console.log('   .claude/');
    console.log('   ├── system-assessment.md');
    console.log('   ├── constraints-inventory.md');
    console.log('   ├── enhancement-plan.md');
    console.log('   ├── risk-assessment.md');
    console.log('   └── technical-debt.md');

    return {
      mode: 'brownfield',
      analysis,
      nextSteps: [
        '1. Review system assessment',
        '2. Document existing constraints',
        '3. Define enhancement objectives',
        '4. Assess integration risks',
        '5. Choose enhancement approach (story/epic/major)'
      ]
    };
  }

  // Helper: Analyze existing system
  async analyzeExistingSystem() {
    const analysis = {
      language: this.detectLanguage(),
      framework: this.detectFramework(),
      architecture: this.detectArchitecture(),
      database: this.detectDatabase(),
      testCoverage: this.calculateTestCoverage(),
      codeQuality: this.assessCodeQuality(),
      technicalDebt: this.assessTechnicalDebt()
    };
    
    return analysis;
  }

  detectLanguage() {
    if (fs.existsSync('package.json')) return 'JavaScript/TypeScript';
    if (fs.existsSync('requirements.txt') || fs.existsSync('Pipfile')) return 'Python';
    if (fs.existsSync('go.mod')) return 'Go';
    if (fs.existsSync('Cargo.toml')) return 'Rust';
    if (fs.existsSync('pom.xml')) return 'Java';
    if (fs.existsSync('Gemfile')) return 'Ruby';
    return 'Unknown';
  }

  detectFramework() {
    try {
      if (fs.existsSync('package.json')) {
        const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        const deps = { ...pkg.dependencies, ...pkg.devDependencies };
        
        if (deps['next']) return 'Next.js';
        if (deps['react']) return 'React';
        if (deps['vue']) return 'Vue';
        if (deps['express']) return 'Express';
        if (deps['@angular/core']) return 'Angular';
      }
      
      if (fs.existsSync('requirements.txt')) {
        const reqs = fs.readFileSync('requirements.txt', 'utf8');
        if (reqs.includes('django')) return 'Django';
        if (reqs.includes('flask')) return 'Flask';
        if (reqs.includes('fastapi')) return 'FastAPI';
      }
    } catch {}
    
    return 'Custom/Unknown';
  }

  detectArchitecture() {
    const patterns = {
      'MVC': ['controllers', 'models', 'views'],
      'Microservices': ['services', 'api-gateway', 'docker-compose.yml'],
      'Serverless': ['serverless.yml', 'functions', 'lambda'],
      'Monolith': ['src', 'app'],
      'Clean Architecture': ['domain', 'application', 'infrastructure', 'presentation']
    };

    for (const [arch, indicators] of Object.entries(patterns)) {
      const matches = indicators.filter(ind => 
        fs.existsSync(path.join(this.projectPath, ind))
      );
      if (matches.length >= 2) return arch;
    }

    return 'Traditional';
  }

  detectDatabase() {
    if (fs.existsSync('prisma')) return 'PostgreSQL/Prisma';
    if (fs.existsSync('migrations')) return 'SQL Database';
    if (fs.existsSync('models/mongodb')) return 'MongoDB';
    
    try {
      const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };
      
      if (deps['pg'] || deps['postgres']) return 'PostgreSQL';
      if (deps['mysql'] || deps['mysql2']) return 'MySQL';
      if (deps['mongodb'] || deps['mongoose']) return 'MongoDB';
      if (deps['redis']) return 'Redis';
    } catch {}
    
    return 'None/Unknown';
  }

  calculateTestCoverage() {
    // Simplified - in reality would run coverage tools
    const testDirs = ['tests', '__tests__', 'test', 'spec'];
    const hasTests = testDirs.some(dir => fs.existsSync(dir));
    
    if (!hasTests) return 0;
    
    // Mock calculation - would use actual coverage tools
    return Math.floor(Math.random() * 40) + 30; // 30-70%
  }

  assessCodeQuality() {
    let score = 5; // Base score
    
    // Check for linting config
    if (fs.existsSync('.eslintrc') || fs.existsSync('.eslintrc.json')) score++;
    if (fs.existsSync('.prettierrc')) score++;
    
    // Check for TypeScript
    if (fs.existsSync('tsconfig.json')) score++;
    
    // Check for tests
    if (this.calculateTestCoverage() > 0) score++;
    
    // Check for documentation
    if (fs.existsSync('README.md')) score++;
    
    return Math.min(score, 10);
  }

  assessTechnicalDebt() {
    const indicators = {
      low: 0,
      medium: 0,
      high: 0
    };

    // Check for outdated dependencies
    try {
      const { execSync } = require('child_process');
      const outdated = execSync('npm outdated --json', { encoding: 'utf8' });
      const deps = JSON.parse(outdated);
      const count = Object.keys(deps).length;
      
      if (count > 20) indicators.high++;
      else if (count > 10) indicators.medium++;
      else if (count > 0) indicators.low++;
    } catch {}

    // Check for TODO/FIXME comments (simplified)
    // In reality, would scan all source files
    
    if (indicators.high > 0) return 'High';
    if (indicators.medium > 0) return 'Medium';
    if (indicators.low > 0) return 'Low';
    return 'Minimal';
  }

  // Create greenfield planning documents
  createGreenfieldStructure(questions) {
    const claudeDir = path.join(this.projectPath, '.claude');
    if (!fs.existsSync(claudeDir)) {
      fs.mkdirSync(claudeDir, { recursive: true });
    }

    // Discovery document
    const discovery = `# Project Discovery

## Problem Statement
${questions.discovery.map(q => `\n### ${q}\n[Your answer here]\n`).join('')}

## Technical Requirements
${questions.technical.map(q => `\n### ${q}\n[Your answer here]\n`).join('')}

## Project Constraints
${questions.constraints.map(q => `\n### ${q}\n[Your answer here]\n`).join('')}

---
Generated: ${new Date().toISOString()}
Mode: Greenfield
`;
    fs.writeFileSync(path.join(claudeDir, 'discovery.md'), discovery);

    // Constraints document (for future reference)
    const constraints = `# Project Constraints & Decisions Log

## Initial Constraints
- **Timeline:** [Define here]
- **Budget:** [Define here]
- **Team:** [Define here]
- **Technology:** [Define here]

## Architectural Decisions

### Decision 1: [Title]
- **Date:** ${new Date().toISOString()}
- **Status:** Proposed
- **Context:** [Why this decision?]
- **Decision:** [What was decided?]
- **Consequences:** [What are the implications?]

## Future Constraints
As we make decisions, they become constraints for future work:
- [ ] Document each major decision
- [ ] Track technology choices
- [ ] Record API contracts
- [ ] Note security requirements

---
Mode: Greenfield - Building constraints as we go
`;
    fs.writeFileSync(path.join(claudeDir, 'constraints.md'), constraints);

    // Risk assessment template
    const risks = `# Risk Assessment - Greenfield Project

## Risk Categories

### Unknown Unknowns
These are the risks we can't predict but should prepare for:

#### Technical Risks
- [ ] New technology learning curve
- [ ] Scalability unknowns
- [ ] Integration surprises
- [ ] Performance uncertainties

#### Business Risks
- [ ] Market changes
- [ ] User adoption
- [ ] Competitor actions
- [ ] Requirement volatility

### Mitigation Strategies

#### Prototype Early
- Build proof of concepts for risky features
- Validate assumptions with users
- Test performance early

#### Plan for Pivots
- Keep architecture flexible
- Avoid over-engineering
- Regular review cycles

#### Knowledge Gaps
- [ ] Identify what we don't know
- [ ] Plan spikes for investigation
- [ ] Budget time for learning

---
Mode: Greenfield - Focus on discovery and flexibility
`;
    fs.writeFileSync(path.join(claudeDir, 'risks.md'), risks);
  }

  // Create brownfield assessment documents
  createBrownfieldStructure(analysis, assessment) {
    const claudeDir = path.join(this.projectPath, '.claude');
    if (!fs.existsSync(claudeDir)) {
      fs.mkdirSync(claudeDir, { recursive: true });
    }

    // System assessment
    const systemAssessment = `# System Assessment - Brownfield Project

## Current State Analysis
- **Language:** ${analysis.language}
- **Framework:** ${analysis.framework}
- **Architecture:** ${analysis.architecture}
- **Database:** ${analysis.database}
- **Test Coverage:** ${analysis.testCoverage}%
- **Code Quality:** ${analysis.codeQuality}/10
- **Technical Debt:** ${analysis.technicalDebt}

## System Evaluation
${assessment.current_state.map(q => `\n### ${q}\n[Your assessment here]\n`).join('')}

## Enhancement Goals
${assessment.enhancement_goals.map(q => `\n### ${q}\n[Your goals here]\n`).join('')}

---
Generated: ${new Date().toISOString()}
Mode: Brownfield
`;
    fs.writeFileSync(path.join(claudeDir, 'system-assessment.md'), systemAssessment);

    // Constraints inventory
    const constraints = `# Constraints Inventory - Brownfield Project

## Hard Constraints (Cannot Change)
${assessment.constraints.map(q => `\n### ${q}\n[Document constraint]\n`).join('')}

## Existing System Constraints

### API Contracts
- **Public APIs:** [List endpoints that cannot change]
- **Internal APIs:** [List services depending on these]
- **Data Formats:** [List formats that must be maintained]

### Database Constraints
- **Schema:** [Tables/collections that cannot change]
- **Data Types:** [Types that must be preserved]
- **Relationships:** [Critical relationships to maintain]

### Integration Points
- **External Services:** [List all external dependencies]
- **Authentication:** [Current auth mechanism]
- **Message Formats:** [Required message formats]

### Deployment Constraints
- **Environment:** [Production environment specs]
- **Dependencies:** [System dependencies]
- **Configuration:** [Config that must be preserved]

## Soft Constraints (Prefer Not to Change)
- **Code Style:** [Current conventions]
- **Folder Structure:** [Existing organization]
- **Build Process:** [Current build pipeline]

---
Mode: Brownfield - Working within existing boundaries
`;
    fs.writeFileSync(path.join(claudeDir, 'constraints-inventory.md'), constraints);

    // Risk assessment for brownfield
    const risks = `# Risk Assessment - Brownfield Project

## Known Risks (Legacy Issues)

### Technical Risks
- [ ] **Breaking Changes:** Risk of breaking existing functionality
- [ ] **Data Corruption:** Risk during migration/updates
- [ ] **Performance Regression:** New code slower than old
- [ ] **Security Vulnerabilities:** Exposed during changes

### Integration Risks
- [ ] **API Compatibility:** Breaking consumer contracts
- [ ] **Data Format Changes:** Breaking downstream systems
- [ ] **Authentication Issues:** User access problems
- [ ] **Third-party Dependencies:** Version conflicts

### Operational Risks
- [ ] **Deployment Failures:** Rollback procedures needed
- [ ] **Monitoring Gaps:** Blind spots during transition
- [ ] **Documentation Drift:** Outdated documentation
- [ ] **Knowledge Loss:** Undocumented behaviors

## Risk Mitigation Plan

### Testing Strategy
- **Regression Testing:** Full suite before deployment
- **Integration Testing:** All external touchpoints
- **Performance Testing:** Baseline comparisons
- **Security Testing:** Vulnerability scanning

### Rollback Plan
- **Database Rollback:** Migration reversal scripts
- **Code Rollback:** Git tags for quick revert
- **Configuration Rollback:** Config backups
- **Communication Plan:** User notification process

### Gradual Rollout
- **Feature Flags:** Progressive enablement
- **Canary Deployment:** Small user group first
- **Monitoring:** Enhanced monitoring during rollout
- **Feedback Loop:** Quick issue detection

---
Mode: Brownfield - Managing known and discovered risks
`;
    fs.writeFileSync(path.join(claudeDir, 'risk-assessment.md'), risks);
  }
}

// Export for use in commands
module.exports = Phase0Entry;

// CLI execution
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {
    brownfield: args.includes('--brownfield'),
    autoDetect: !args.includes('--no-detect')
  };

  const phase0 = new Phase0Entry(options);
  phase0.initialize().then(result => {
    console.log('\n✅ Phase 0 Initialized');
    console.log('\n📋 Next Steps:');
    result.nextSteps.forEach((step, i) => {
      console.log(`   ${step}`);
    });
  });
}