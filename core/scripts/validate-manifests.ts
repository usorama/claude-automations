import * as fs from 'fs';
import * as path from 'path';
import { Project, SourceFile, FunctionDeclaration, MethodDeclaration } from 'ts-morph';
import * as yaml from 'js-yaml';

interface ValidationReport {
  duplicates: DuplicateFunction[];
  incorrectImports: IncorrectImport[];
  patternViolations: PatternViolation[];
  missingExports: MissingExport[];
  summary: {
    total_issues: number;
    duplicates: number;
    imports: number;
    patterns: number;
    missing: number;
    status: 'PASS' | 'WARNING' | 'FAIL';
  };
}

interface DuplicateFunction {
  name: string;
  existing_file: string;
  existing_line: number;
  duplicate_file: string;
  duplicate_line: number;
  signature: string;
}

interface IncorrectImport {
  file: string;
  line: number;
  import_statement: string;
  available_exports: string[];
  suggested_fix: string;
}

interface PatternViolation {
  file: string;
  line: number;
  violation_type: string;
  description: string;
  expected_pattern: string;
  actual_code: string;
}

interface MissingExport {
  function_name: string;
  file: string;
  line: number;
  should_use_existing: string;
}

interface FunctionInfo {
  name: string;
  file: string;
  line: number;
  signature: string;
}

interface ExportInfo {
  name: string;
  kind: string;
  line: number;
}

class ManifestValidator {
  private project: Project;
  private manifestDir: string;
  private functionRegistry: Map<string, FunctionInfo> = new Map();
  private exportRegistry: Map<string, ExportInfo[]> = new Map();
  private codePatterns: any = {};
  
  constructor(projectPath: string = '.') {
    this.project = new Project({
      tsConfigFilePath: path.join(projectPath, 'tsconfig.json'),
      skipAddingFilesFromTsConfig: false,
    });
    
    this.manifestDir = path.join(process.env.HOME || '', '.claude', 'manifests');
    
    // Also check local manifest directory
    const localManifestDir = path.join(projectPath, '.claude', 'manifests');
    if (fs.existsSync(localManifestDir)) {
      this.manifestDir = localManifestDir;
    }
  }
  
  async validateCodeAgainstManifests(): Promise<ValidationReport> {
    console.log('🔍 Loading manifests...');
    await this.loadManifests();
    
    console.log('🔍 Analyzing codebase...');
    const report: ValidationReport = {
      duplicates: [],
      incorrectImports: [],
      patternViolations: [],
      missingExports: [],
      summary: {
        total_issues: 0,
        duplicates: 0,
        imports: 0,
        patterns: 0,
        missing: 0,
        status: 'PASS'
      }
    };
    
    // Get all source files
    const sourceFiles = this.project.getSourceFiles().filter(file => 
      !file.getFilePath().includes('node_modules') &&
      !file.getFilePath().includes('dist') &&
      !file.getFilePath().includes('.git')
    );
    
    // Validate each file
    for (const file of sourceFiles) {
      await this.validateFile(file, report);
    }
    
    // Calculate summary
    this.calculateSummary(report);
    
    return report;
  }
  
  private async loadManifests(): Promise<void> {
    try {
      // Load function registry
      const functionRegistryPath = path.join(this.manifestDir, 'FUNCTION_REGISTRY.md');
      if (fs.existsSync(functionRegistryPath)) {
        this.parseFunctionRegistry(fs.readFileSync(functionRegistryPath, 'utf-8'));
      }
      
      // Load export registry
      const exportRegistryPath = path.join(this.manifestDir, 'EXPORT_REGISTRY.json');
      if (fs.existsSync(exportRegistryPath)) {
        const exportData = JSON.parse(fs.readFileSync(exportRegistryPath, 'utf-8'));
        Object.entries(exportData).forEach(([file, exports]) => {
          this.exportRegistry.set(file, exports as ExportInfo[]);
        });
      }
      
      // Load code patterns
      const codePatternsPath = path.join(this.manifestDir, 'CODE_PATTERNS.md');
      if (fs.existsSync(codePatternsPath)) {
        // Simple pattern extraction from markdown
        const patternsContent = fs.readFileSync(codePatternsPath, 'utf-8');
        this.codePatterns = this.parseCodePatterns(patternsContent);
      }
      
    } catch (error) {
      console.warn('⚠️ Error loading manifests:', error);
    }
  }
  
  private parseFunctionRegistry(content: string): void {
    const lines = content.split('\n');
    let currentFunction: Partial<FunctionInfo> = {};
    
    for (const line of lines) {
      // Parse function headers (### FunctionName)
      const functionMatch = line.match(/^### (.+)/);
      if (functionMatch) {
        if (currentFunction.name) {
          // Save previous function
          this.functionRegistry.set(currentFunction.name, currentFunction as FunctionInfo);
        }
        currentFunction = { name: functionMatch[1] };
        continue;
      }
      
      // Parse location
      const locationMatch = line.match(/- \*\*Location\*\*: `(.+):(\d+)`/);
      if (locationMatch) {
        currentFunction.file = locationMatch[1];
        currentFunction.line = parseInt(locationMatch[2]);
        continue;
      }
      
      // Parse signature
      const signatureMatch = line.match(/```typescript\n(.+)\n```/);
      if (signatureMatch) {
        currentFunction.signature = signatureMatch[1];
        continue;
      }
    }
    
    // Save last function
    if (currentFunction.name) {
      this.functionRegistry.set(currentFunction.name, currentFunction as FunctionInfo);
    }
  }
  
  private parseCodePatterns(content: string): any {
    // Extract key patterns from markdown
    const patterns = {
      errorHandling: [],
      naming: {},
      imports: {},
      exports: {}
    };
    
    // Look for specific pattern indicators
    if (content.includes('Try-Catch blocks')) {
      patterns.errorHandling.push('try_catch_required');
    }
    if (content.includes('Async/Await')) {
      patterns.errorHandling.push('async_await_preferred');
    }
    if (content.includes('camelCase')) {
      patterns.naming = { functions: 'camelCase', files: 'kebab-case' };
    }
    
    return patterns;
  }
  
  private async validateFile(file: SourceFile, report: ValidationReport): Promise<void> {
    const filePath = path.relative(process.cwd(), file.getFilePath());
    
    // Check for duplicate functions
    this.checkDuplicateFunctions(file, filePath, report);
    
    // Check imports
    this.checkIncorrectImports(file, filePath, report);
    
    // Check pattern violations
    this.checkPatternViolations(file, filePath, report);
    
    // Check for missing exports that should use existing ones
    this.checkMissingExports(file, filePath, report);
  }
  
  private checkDuplicateFunctions(file: SourceFile, filePath: string, report: ValidationReport): void {
    const functions = file.getFunctions();
    
    for (const func of functions) {
      const funcName = func.getName();
      if (!funcName) continue;
      
      const existing = this.functionRegistry.get(funcName);
      if (existing && existing.file !== filePath) {
        report.duplicates.push({
          name: funcName,
          existing_file: existing.file,
          existing_line: existing.line,
          duplicate_file: filePath,
          duplicate_line: func.getStartLineNumber(),
          signature: func.getText().split('{')[0].trim()
        });
      }
      
      // Also check class methods
      file.getClasses().forEach(cls => {
        cls.getMethods().forEach(method => {
          const methodName = `${cls.getName()}.${method.getName()}`;
          const existing = this.functionRegistry.get(methodName);
          if (existing && existing.file !== filePath) {
            report.duplicates.push({
              name: methodName,
              existing_file: existing.file,
              existing_line: existing.line,
              duplicate_file: filePath,
              duplicate_line: method.getStartLineNumber(),
              signature: method.getText().split('{')[0].trim()
            });
          }
        });
      });
    }
  }
  
  private checkIncorrectImports(file: SourceFile, filePath: string, report: ValidationReport): void {
    const imports = file.getImportDeclarations();
    
    for (const importDecl of imports) {
      const moduleSpecifier = importDecl.getModuleSpecifierValue();
      
      // Skip external modules
      if (!moduleSpecifier.startsWith('.') && !moduleSpecifier.startsWith('/')) {
        continue;
      }
      
      // Check if imported module exists in export registry
      const availableExports = this.exportRegistry.get(moduleSpecifier);
      if (!availableExports) continue;
      
      const namedImports = importDecl.getNamedImports();
      for (const namedImport of namedImports) {
        const importName = namedImport.getName();
        const isAvailable = availableExports.some(exp => exp.name === importName);
        
        if (!isAvailable) {
          const availableNames = availableExports.map(exp => exp.name);
          const suggestion = this.findClosestMatch(importName, availableNames);
          
          report.incorrectImports.push({
            file: filePath,
            line: importDecl.getStartLineNumber(),
            import_statement: importDecl.getText(),
            available_exports: availableNames,
            suggested_fix: suggestion ? `Use '${suggestion}' instead of '${importName}'` : 'Check available exports'
          });
        }
      }
    }
  }
  
  private checkPatternViolations(file: SourceFile, filePath: string, report: ValidationReport): void {
    const content = file.getText();
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      // Check for console.log in production code (should use logger)
      if (line.includes('console.log') && !line.includes('// eslint-disable')) {
        report.patternViolations.push({
          file: filePath,
          line: index + 1,
          violation_type: 'CONSOLE_LOG_USAGE',
          description: 'Using console.log instead of logger',
          expected_pattern: 'Use logger.debug(), logger.info(), etc.',
          actual_code: line.trim()
        });
      }
      
      // Check for empty catch blocks
      if (/catch\s*\([^)]*\)\s*{\s*}/.test(line)) {
        report.patternViolations.push({
          file: filePath,
          line: index + 1,
          violation_type: 'EMPTY_CATCH_BLOCK',
          description: 'Empty catch block hides errors',
          expected_pattern: 'Log error and handle appropriately',
          actual_code: line.trim()
        });
      }
      
      // Check for TODO comments in main files
      if (line.includes('TODO') && !filePath.includes('test')) {
        report.patternViolations.push({
          file: filePath,
          line: index + 1,
          violation_type: 'TODO_IN_PRODUCTION',
          description: 'TODO comment in production code',
          expected_pattern: 'Complete implementation or create issue',
          actual_code: line.trim()
        });
      }
    });
  }
  
  private checkMissingExports(file: SourceFile, filePath: string, report: ValidationReport): void {
    const functions = file.getFunctions();
    
    for (const func of functions) {
      const funcName = func.getName();
      if (!funcName || func.isExported()) continue;
      
      // Check if a similar function exists in registry that should be used instead
      const existing = this.findSimilarFunction(funcName);
      if (existing && existing.file !== filePath) {
        report.missingExports.push({
          function_name: funcName,
          file: filePath,
          line: func.getStartLineNumber(),
          should_use_existing: `${existing.name} in ${existing.file}:${existing.line}`
        });
      }
    }
  }
  
  private findSimilarFunction(funcName: string): FunctionInfo | undefined {
    // Simple similarity check - look for exact matches or similar names
    for (const [name, info] of this.functionRegistry) {
      if (name === funcName || this.calculateSimilarity(name, funcName) > 0.8) {
        return info;
      }
    }
    return undefined;
  }
  
  private findClosestMatch(target: string, candidates: string[]): string | null {
    let bestMatch = null;
    let bestScore = 0;
    
    for (const candidate of candidates) {
      const score = this.calculateSimilarity(target, candidate);
      if (score > bestScore && score > 0.5) {
        bestScore = score;
        bestMatch = candidate;
      }
    }
    
    return bestMatch;
  }
  
  private calculateSimilarity(str1: string, str2: string): number {
    const len1 = str1.length;
    const len2 = str2.length;
    const matrix = Array(len1 + 1).fill(null).map(() => Array(len2 + 1).fill(null));
    
    for (let i = 0; i <= len1; i++) matrix[i][0] = i;
    for (let j = 0; j <= len2; j++) matrix[0][j] = j;
    
    for (let i = 1; i <= len1; i++) {
      for (let j = 1; j <= len2; j++) {
        const cost = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[i][j] = Math.min(
          matrix[i - 1][j] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j - 1] + cost
        );
      }
    }
    
    const distance = matrix[len1][len2];
    return 1 - distance / Math.max(len1, len2);
  }
  
  private calculateSummary(report: ValidationReport): void {
    report.summary.duplicates = report.duplicates.length;
    report.summary.imports = report.incorrectImports.length;
    report.summary.patterns = report.patternViolations.length;
    report.summary.missing = report.missingExports.length;
    report.summary.total_issues = 
      report.summary.duplicates + 
      report.summary.imports + 
      report.summary.patterns + 
      report.summary.missing;
    
    // Determine status
    if (report.summary.duplicates > 0 || report.summary.patterns > 5) {
      report.summary.status = 'FAIL';
    } else if (report.summary.total_issues > 0) {
      report.summary.status = 'WARNING';
    } else {
      report.summary.status = 'PASS';
    }
  }
  
  generateReport(report: ValidationReport): string {
    let output = '# Manifest Validation Report\n\n';
    
    // Summary
    output += `## Summary\n\n`;
    output += `- **Status**: ${report.summary.status}\n`;
    output += `- **Total Issues**: ${report.summary.total_issues}\n`;
    output += `- **Duplicates**: ${report.summary.duplicates}\n`;
    output += `- **Import Issues**: ${report.summary.imports}\n`;
    output += `- **Pattern Violations**: ${report.summary.patterns}\n`;
    output += `- **Missing Exports**: ${report.summary.missing}\n\n`;
    
    // Duplicate Functions
    if (report.duplicates.length > 0) {
      output += `## 🔄 Duplicate Functions\n\n`;
      report.duplicates.forEach(dup => {
        output += `### ${dup.name}\n`;
        output += `- **Existing**: \`${dup.existing_file}:${dup.existing_line}\`\n`;
        output += `- **Duplicate**: \`${dup.duplicate_file}:${dup.duplicate_line}\`\n`;
        output += `- **Fix**: Remove duplicate and import from existing location\n\n`;
      });
    }
    
    // Incorrect Imports
    if (report.incorrectImports.length > 0) {
      output += `## 📦 Import Issues\n\n`;
      report.incorrectImports.forEach(imp => {
        output += `### ${imp.file}:${imp.line}\n`;
        output += `- **Import**: \`${imp.import_statement}\`\n`;
        output += `- **Issue**: Function not available in module\n`;
        output += `- **Fix**: ${imp.suggested_fix}\n\n`;
      });
    }
    
    // Pattern Violations
    if (report.patternViolations.length > 0) {
      output += `## ⚠️ Pattern Violations\n\n`;
      report.patternViolations.forEach(violation => {
        output += `### ${violation.violation_type} in ${violation.file}:${violation.line}\n`;
        output += `- **Description**: ${violation.description}\n`;
        output += `- **Expected**: ${violation.expected_pattern}\n`;
        output += `- **Actual**: \`${violation.actual_code}\`\n\n`;
      });
    }
    
    return output;
  }
}

// Main execution
async function main() {
  try {
    const validator = new ManifestValidator();
    
    console.log('🔍 Validating code against manifests...');
    const report = await validator.validateCodeAgainstManifests();
    
    // Write JSON report
    fs.writeFileSync('manifest-validation-report.json', JSON.stringify(report, null, 2));
    
    // Write markdown report
    const markdownReport = validator.generateReport(report);
    fs.writeFileSync('manifest-validation-report.md', markdownReport);
    
    // Console output
    console.log('\n📊 Validation Results:');
    console.log(`Status: ${report.summary.status}`);
    console.log(`Total Issues: ${report.summary.total_issues}`);
    
    if (report.summary.status === 'FAIL') {
      console.log('❌ Validation failed - critical issues found');
      process.exit(1);
    } else if (report.summary.status === 'WARNING') {
      console.log('⚠️ Validation passed with warnings');
    } else {
      console.log('✅ Validation passed - no issues found');
    }
    
  } catch (error) {
    console.error('❌ Error during validation:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export { ManifestValidator };