#!/usr/bin/env node

/**
 * Silent Failure Detector
 * 
 * This script analyzes your codebase to find patterns that indicate
 * silent failures, mock data in production, and other anti-patterns
 * that hide real issues from developers and users.
 * 
 * Usage: npx ts-node silent-failure-detector.ts [directory]
 */

import * as fs from 'fs';
import * as path from 'path';
import { glob } from 'glob';

interface Issue {
  file: string;
  line: number;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  message: string;
  code?: string;
}

class SilentFailureDetector {
  private issues: Issue[] = [];
  private fileCount = 0;
  private patterns = {
    critical: [
      {
        pattern: /catch\s*\([^)]*\)\s*{\s*}/g,
        message: 'Empty catch block - errors are being swallowed',
        type: 'EMPTY_CATCH'
      },
      {
        pattern: /catch\s*\([^)]*\)\s*{\s*console\.(log|warn|error)[^}]*}/g,
        message: 'Catch block only logs - error not re-thrown or handled',
        type: 'LOG_ONLY_CATCH'
      },
      {
        pattern: /return\s+["'].*generic.*response.*["']/gi,
        message: 'Generic/mock response being returned',
        type: 'MOCK_RESPONSE'
      },
      {
        pattern: /return\s+["'].*great question.*["']/gi,
        message: 'AI fallback response detected',
        type: 'AI_FALLBACK'
      },
      {
        pattern: /mockData|fakeData|dummyData|testData/g,
        message: 'Mock/fake data reference in production code',
        type: 'MOCK_DATA'
      }
    ],
    high: [
      {
        pattern: /\|\|\s*["'].*["']|\|\|\s*\[.*\]|\|\|\s*{.*}/g,
        message: 'Fallback to hardcoded value using || operator',
        type: 'HARDCODED_FALLBACK'
      },
      {
        pattern: /\.catch\(\s*\(\)\s*=>\s*null\)/g,
        message: 'Promise catch returning null - hiding failures',
        type: 'NULL_CATCH'
      },
      {
        pattern: /if\s*\(.*\)\s*{\s*return\s+defaultValue/g,
        message: 'Returning default value on condition',
        type: 'DEFAULT_FALLBACK'
      },
      {
        pattern: /process\.env\.\w+\s*\|\|/g,
        message: 'Environment variable with fallback - may hide missing config',
        type: 'ENV_FALLBACK'
      },
      {
        pattern: /localStorage|sessionStorage/g,
        message: 'Browser storage used - may fail silently',
        type: 'BROWSER_STORAGE'
      }
    ],
    medium: [
      {
        pattern: /console\.warn.*continue|console\.warn.*skip/gi,
        message: 'Warning and continuing - potential silent failure',
        type: 'WARN_CONTINUE'
      },
      {
        pattern: /\?\.\w+\(\)/g,
        message: 'Optional chaining on function call - may hide missing service',
        type: 'OPTIONAL_CHAINING'
      },
      {
        pattern: /swallow.*error|ignore.*error|suppress.*error/gi,
        message: 'Code comment suggests error suppression',
        type: 'ERROR_SUPPRESSION_COMMENT'
      },
      {
        pattern: /TODO.*error|FIXME.*error|HACK.*error/gi,
        message: 'TODO/FIXME related to error handling',
        type: 'ERROR_TODO'
      }
    ],
    low: [
      {
        pattern: /setTimeout.*catch/g,
        message: 'Async operation without proper error handling',
        type: 'ASYNC_NO_CATCH'
      },
      {
        pattern: /firebase\.auth\(\).*\|\|/g,
        message: 'Auth check with fallback - may hide auth issues',
        type: 'AUTH_FALLBACK'
      }
    ]
  };

  constructor(private rootDir: string) {}

  async analyze(): Promise<void> {
    console.log(`🔍 Analyzing ${this.rootDir} for silent failures...\n`);
    
    const files = await this.getSourceFiles();
    
    for (const file of files) {
      await this.analyzeFile(file);
    }
    
    this.generateReport();
  }

  private async getSourceFiles(): Promise<string[]> {
    const patterns = [
      '**/*.ts',
      '**/*.tsx',
      '**/*.js',
      '**/*.jsx'
    ];
    
    const ignorePatterns = [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/*.test.*',
      '**/*.spec.*',
      '**/tests/**',
      '**/__tests__/**',
      '**/mock*/**',
      '**/fixture*/**'
    ];
    
    const files: string[] = [];
    
    for (const pattern of patterns) {
      const matches = await glob(pattern, {
        cwd: this.rootDir,
        ignore: ignorePatterns
      });
      files.push(...matches.map(f => path.join(this.rootDir, f)));
    }
    
    return files;
  }

  private async analyzeFile(filePath: string): Promise<void> {
    this.fileCount++;
    
    const content = await fs.promises.readFile(filePath, 'utf-8');
    const lines = content.split('\n');
    
    // Skip test files even if they somehow got through
    if (filePath.includes('.test.') || filePath.includes('.spec.')) {
      return;
    }
    
    // Check each severity level
    for (const [severity, patterns] of Object.entries(this.patterns)) {
      for (const { pattern, message, type } of patterns) {
        const regex = new RegExp(pattern);
        
        lines.forEach((line, index) => {
          const matches = line.match(regex);
          if (matches) {
            this.issues.push({
              file: path.relative(this.rootDir, filePath),
              line: index + 1,
              type,
              severity: severity as Issue['severity'],
              message,
              code: line.trim()
            });
          }
        });
      }
    }
    
    // Special checks that need more context
    this.checkForMissingErrorHandling(filePath, content);
    this.checkForMockServices(filePath, content);
    this.checkForSilentModeFlags(filePath, content);
  }

  private checkForMissingErrorHandling(filePath: string, content: string): void {
    // Check for async functions without try-catch
    const asyncFuncRegex = /async\s+(\w+)\s*\([^)]*\)\s*{([^}]*)}/g;
    let match;
    
    while ((match = asyncFuncRegex.exec(content)) !== null) {
      const functionBody = match[2];
      if (!functionBody.includes('try') && !functionBody.includes('.catch')) {
        const line = content.substring(0, match.index).split('\n').length;
        this.issues.push({
          file: path.relative(this.rootDir, filePath),
          line,
          type: 'ASYNC_NO_ERROR_HANDLING',
          severity: 'medium',
          message: `Async function '${match[1]}' without error handling`
        });
      }
    }
  }

  private checkForMockServices(filePath: string, content: string): void {
    // Check for services that return mock data
    const mockServiceRegex = /class\s+(\w*Mock\w*)|class\s+(\w*Stub\w*)|class\s+(\w*Fake\w*)/g;
    let match;
    
    while ((match = mockServiceRegex.exec(content)) !== null) {
      const line = content.substring(0, match.index).split('\n').length;
      const className = match[1] || match[2] || match[3];
      this.issues.push({
        file: path.relative(this.rootDir, filePath),
        line,
        type: 'MOCK_SERVICE',
        severity: 'critical',
        message: `Mock service class '${className}' found in production code`
      });
    }
  }

  private checkForSilentModeFlags(filePath: string, content: string): void {
    // Check for flags that enable silent modes
    const silentFlagRegex = /silent.*=.*true|quiet.*=.*true|suppress.*=.*true/gi;
    let match;
    
    while ((match = silentFlagRegex.exec(content)) !== null) {
      const line = content.substring(0, match.index).split('\n').length;
      this.issues.push({
        file: path.relative(this.rootDir, filePath),
        line,
        type: 'SILENT_MODE_FLAG',
        severity: 'high',
        message: 'Silent/quiet mode flag detected'
      });
    }
  }

  private generateReport(): void {
    const criticalCount = this.issues.filter(i => i.severity === 'critical').length;
    const highCount = this.issues.filter(i => i.severity === 'high').length;
    const mediumCount = this.issues.filter(i => i.severity === 'medium').length;
    const lowCount = this.issues.filter(i => i.severity === 'low').length;
    
    console.log('📊 SILENT FAILURE DETECTION REPORT');
    console.log('=' .repeat(80));
    console.log(`Files analyzed: ${this.fileCount}`);
    console.log(`Total issues found: ${this.issues.length}`);
    console.log('');
    console.log(`🔴 Critical: ${criticalCount}`);
    console.log(`🟠 High: ${highCount}`);
    console.log(`🟡 Medium: ${mediumCount}`);
    console.log(`🟢 Low: ${lowCount}`);
    console.log('=' .repeat(80));
    console.log('');
    
    // Group issues by severity
    const severities: Issue['severity'][] = ['critical', 'high', 'medium', 'low'];
    
    for (const severity of severities) {
      const severityIssues = this.issues.filter(i => i.severity === severity);
      
      if (severityIssues.length > 0) {
        const emoji = {
          critical: '🔴',
          high: '🟠',
          medium: '🟡',
          low: '🟢'
        }[severity];
        
        console.log(`\n${emoji} ${severity.toUpperCase()} ISSUES:`);
        console.log('-'.repeat(80));
        
        // Group by type
        const typeGroups: { [key: string]: Issue[] } = {};
        severityIssues.forEach(issue => {
          if (!typeGroups[issue.type]) {
            typeGroups[issue.type] = [];
          }
          typeGroups[issue.type].push(issue);
        });
        
        for (const [type, issues] of Object.entries(typeGroups)) {
          console.log(`\n  ${type} (${issues.length} occurrences):`);
          
          // Show first 3 examples
          issues.slice(0, 3).forEach(issue => {
            console.log(`    📍 ${issue.file}:${issue.line}`);
            console.log(`       ${issue.message}`);
            if (issue.code) {
              console.log(`       Code: ${issue.code.substring(0, 60)}...`);
            }
          });
          
          if (issues.length > 3) {
            console.log(`    ... and ${issues.length - 3} more`);
          }
        }
      }
    }
    
    // Generate recommendations
    console.log('\n\n💡 RECOMMENDATIONS:');
    console.log('=' .repeat(80));
    
    if (criticalCount > 0) {
      console.log('❗ CRITICAL: Your application has severe silent failure patterns.');
      console.log('   - Remove ALL mock/fake responses from production code');
      console.log('   - Fix empty catch blocks immediately');
      console.log('   - Implement proper error propagation');
    }
    
    if (highCount > 0) {
      console.log('⚠️  HIGH: Significant issues that hide failures from users.');
      console.log('   - Remove hardcoded fallback values');
      console.log('   - Add proper error handling to promises');
      console.log('   - Validate environment variables at startup');
    }
    
    if (this.issues.length === 0) {
      console.log('✅ Excellent! No silent failure patterns detected.');
    } else {
      console.log('\n📋 Next Steps:');
      console.log('1. Fix all critical issues before deploying to production');
      console.log('2. Add startup validation for required services');
      console.log('3. Implement health checks and monitoring');
      console.log('4. Replace mock responses with proper error handling');
      console.log('5. Add observability (logging, metrics, alerts)');
    }
    
    // Export detailed report
    const reportPath = path.join(process.cwd(), 'silent-failures-report.json');
    fs.writeFileSync(reportPath, JSON.stringify({
      summary: {
        filesAnalyzed: this.fileCount,
        totalIssues: this.issues.length,
        critical: criticalCount,
        high: highCount,
        medium: mediumCount,
        low: lowCount
      },
      issues: this.issues
    }, null, 2));
    
    console.log(`\n📄 Detailed report saved to: ${reportPath}`);
  }
}

// Main execution
async function main() {
  const targetDir = process.argv[2] || process.cwd();
  
  if (!fs.existsSync(targetDir)) {
    console.error(`❌ Directory not found: ${targetDir}`);
    process.exit(1);
  }
  
  const detector = new SilentFailureDetector(targetDir);
  await detector.analyze();
  
  // Exit with error code if critical issues found
  const criticalCount = detector['issues'].filter(i => i.severity === 'critical').length;
  if (criticalCount > 0) {
    process.exit(1);
  }
}

main().catch(error => {
  console.error('❌ Error running silent failure detector:', error);
  process.exit(1);
});