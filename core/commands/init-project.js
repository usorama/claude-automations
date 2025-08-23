#!/usr/bin/env node

/**
 * Unified Project Initialization
 * Smart detection + --brownfield switch support
 */

const ProjectDetector = require('./project-detector');
const Phase0Entry = require('./phase0-entry');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

class ProjectInitializer {
  constructor() {
    this.args = process.argv.slice(2);
    this.options = this.parseArgs();
    this.projectPath = process.cwd();
  }

  parseArgs() {
    return {
      brownfield: this.args.includes('--brownfield'),
      force: this.args.includes('--force'),
      skipDetection: this.args.includes('--skip-detection'),
      help: this.args.includes('--help') || this.args.includes('-h')
    };
  }

  showHelp() {
    console.log(`
Claude Code Project Initializer

Usage: claude init [options]

Options:
  --brownfield      Force brownfield mode (existing project)
  --skip-detection  Skip auto-detection, use greenfield by default
  --force          Skip confirmation prompts
  -h, --help       Show this help message

Examples:
  claude init                    # Auto-detect project type
  claude init --brownfield       # Force brownfield mode
  claude init --skip-detection   # Default to greenfield

Detection Logic:
  - Empty directory → Greenfield
  - Git history with <5 commits → Greenfield
  - Default scaffolding only → Greenfield
  - Custom business logic → Brownfield
  - Multiple contributors → Brownfield
  - Production configs → Brownfield
`);
  }

  async run() {
    if (this.options.help) {
      this.showHelp();
      process.exit(0);
    }

    console.log('🚀 Claude Code Project Initializer');
    console.log('═'.repeat(60));

    let projectType = 'greenfield';
    let confidence = 100;

    // Determine project type
    if (this.options.brownfield) {
      console.log('🏗️  Brownfield mode explicitly set\n');
      projectType = 'brownfield';
    } else if (!this.options.skipDetection) {
      // Run auto-detection
      const detector = new ProjectDetector(this.projectPath);
      const result = detector.detect();
      
      projectType = result.type;
      confidence = result.confidence;

      // Show detection results
      if (projectType === 'brownfield') {
        console.log(`🏗️  Detected: Existing Codebase (confidence: ${confidence}%)`);
      } else {
        console.log(`🌱 Detected: New Project (confidence: ${confidence}%)`);
      }

      if (result.features.length > 0) {
        console.log('\n📋 Key Indicators:');
        result.features.forEach(f => console.log(`   - ${f}`));
      }

      // Ask for confirmation unless forced
      if (!this.options.force && confidence < 90) {
        const confirmed = await this.confirmProjectType(projectType);
        if (!confirmed) {
          projectType = projectType === 'greenfield' ? 'brownfield' : 'greenfield';
          console.log(`\n🔄 Switching to ${projectType} mode...`);
        }
      }
    } else {
      console.log('🌱 Defaulting to greenfield mode (detection skipped)\n');
    }

    console.log('');
    console.log('═'.repeat(60));

    // Initialize Phase 0 with determined type
    const phase0 = new Phase0Entry({
      brownfield: projectType === 'brownfield',
      autoDetect: false // We already detected
    });

    const result = await phase0.initialize();

    // Save project configuration
    this.saveProjectConfig(projectType, confidence);

    // Show summary
    console.log('\n' + '═'.repeat(60));
    console.log('✅ Project Initialized Successfully!');
    console.log('═'.repeat(60));
    
    console.log('\n📊 Summary:');
    console.log(`   Mode: ${projectType}`);
    console.log(`   Focus: ${projectType === 'greenfield' ? 'What should we build?' : 'What do we have?'}`);
    console.log(`   Workflow: ${projectType === 'greenfield' ? 'Plan → Build → Verify' : 'Assess → Enhance → Validate'}`);
    
    console.log('\n📋 Next Steps:');
    result.nextSteps.forEach((step, i) => {
      console.log(`   ${step}`);
    });

    console.log('\n💡 Quick Commands:');
    if (projectType === 'greenfield') {
      console.log('   /0.1discover   - Complete discovery questionnaire');
      console.log('   /0.2define     - Define requirements');
      console.log('   /0.3validate   - Validate approach');
      console.log('   /1.0architect  - Design system architecture');
    } else {
      console.log('   /assess        - Deep system assessment');
      console.log('   /constraints   - Document constraints');
      console.log('   /debt          - Analyze technical debt');
      console.log('   /enhance       - Plan enhancements');
    }

    console.log('\n🎯 Pro Tip:');
    if (projectType === 'greenfield') {
      console.log('   Take time in Phase 0 to define clear requirements.');
      console.log('   Good planning now saves debugging later!');
    } else {
      console.log('   Start small with a single story to understand the codebase.');
      console.log('   Build confidence before attempting major changes!');
    }
  }

  async confirmProjectType(detected) {
    return new Promise((resolve) => {
      const readline = require('readline').createInterface({
        input: process.stdin,
        output: process.stdout
      });

      const question = `\n✅ Proceed with ${detected} workflow? (Y/n): `;
      
      readline.question(question, (answer) => {
        readline.close();
        resolve(answer.toLowerCase() !== 'n');
      });
    });
  }

  saveProjectConfig(projectType, confidence) {
    const config = {
      projectType,
      confidence,
      initialized: new Date().toISOString(),
      version: '1.0.0',
      settings: {
        autoDetect: !this.options.skipDetection,
        explicitMode: this.options.brownfield || false
      }
    };

    const claudeDir = path.join(this.projectPath, '.claude');
    if (!fs.existsSync(claudeDir)) {
      fs.mkdirSync(claudeDir, { recursive: true });
    }

    fs.writeFileSync(
      path.join(claudeDir, 'project-config.json'),
      JSON.stringify(config, null, 2)
    );
  }
}

// Main execution
if (require.main === module) {
  const initializer = new ProjectInitializer();
  initializer.run().catch(error => {
    console.error('❌ Initialization failed:', error.message);
    process.exit(1);
  });
}

module.exports = ProjectInitializer;