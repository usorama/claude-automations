import { Project, Node, SyntaxKind, SourceFile, FunctionDeclaration, MethodDeclaration, ArrowFunction } from 'ts-morph';
import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

interface ProjectManifest {
  project: {
    name: string;
    version: string;
    language: string;
    framework: string;
  };
  statistics: {
    total_functions: number;
    total_exports: number;
    async_functions: number;
    total_files: number;
    total_classes: number;
    total_interfaces: number;
  };
  key_modules: Array<{
    path: string;
    exports: number;
    imports: number;
    functions: number;
  }>;
  patterns: {
    error_handling: string[];
    state_management: string[];
    data_flow: string[];
  };
  references: {
    functions: string;
    exports: string;
    decisions: string;
    import_graph: string;
    tech_stack: string;
  };
}

interface FunctionInfo {
  name: string;
  file: string;
  line: number;
  signature: string;
  isAsync: boolean;
  isExported: boolean;
  parameters: string[];
  returnType: string;
}

interface ExportInfo {
  name: string;
  kind: string;
  line: number;
}

class ManifestGenerator {
  private project: Project;
  private manifestDir: string;
  
  constructor(projectPath: string = '.') {
    // Initialize ts-morph project
    const tsConfigPath = path.join(projectPath, 'tsconfig.json');
    
    this.project = new Project({
      tsConfigFilePath: fs.existsSync(tsConfigPath) ? tsConfigPath : undefined,
      skipAddingFilesFromTsConfig: false,
    });
    
    // Add source files if no tsconfig
    if (!fs.existsSync(tsConfigPath)) {
      this.project.addSourceFilesAtPaths([
        path.join(projectPath, '**/*.ts'),
        path.join(projectPath, '**/*.tsx'),
        '!**/node_modules/**',
        '!**/dist/**',
        '!**/*.d.ts'
      ]);
    }
    
    // Set manifest directory
    this.manifestDir = path.join(process.env.HOME || '', '.claude', 'manifests');
    
    // Ensure manifest directory exists
    if (!fs.existsSync(this.manifestDir)) {
      fs.mkdirSync(this.manifestDir, { recursive: true });
    }
  }
  
  async generateAll(): Promise<void> {
    console.log('🔍 Analyzing codebase...');
    
    const manifest = await this.generateMainManifest();
    
    console.log('📝 Generating manifests...');
    
    // Write main manifest
    fs.writeFileSync(
      path.join(this.manifestDir, 'CODEBASE_MANIFEST.yaml'),
      yaml.dump(manifest, { indent: 2 })
    );
    
    // Generate specialized manifests
    await this.generateFunctionRegistry();
    await this.generateExportRegistry();
    await this.generateImportGraph();
    await this.generateTechStack();
    await this.generateCodePatterns();
    await this.generateAPISurface();
    
    console.log('✅ Manifests generated successfully!');
    console.log(`📁 Location: ${this.manifestDir}`);
  }
  
  private async generateMainManifest(): Promise<ProjectManifest> {
    const packageJson = this.getPackageJson();
    const sourceFiles = this.project.getSourceFiles();
    
    // Calculate statistics
    const stats = {
      total_functions: this.countAllFunctions(),
      total_exports: this.countAllExports(),
      async_functions: this.countAsyncFunctions(),
      total_files: sourceFiles.length,
      total_classes: this.countClasses(),
      total_interfaces: this.countInterfaces(),
    };
    
    // Analyze key modules
    const keyModules = this.analyzeKeyModules();
    
    // Detect patterns
    const patterns = this.detectPatterns();
    
    return {
      project: {
        name: packageJson.name || 'unknown',
        version: packageJson.version || '0.0.0',
        language: 'TypeScript',
        framework: this.detectFramework(),
      },
      statistics: stats,
      key_modules: keyModules,
      patterns,
      references: {
        functions: '@.claude/manifests/FUNCTION_REGISTRY.md',
        exports: '@.claude/manifests/EXPORT_REGISTRY.json',
        decisions: '@.claude/manifests/DECISIONS_LOG.md',
        import_graph: '@.claude/manifests/IMPORT_GRAPH.yaml',
        tech_stack: '@.claude/manifests/TECH_STACK.json',
      },
    };
  }
  
  private async generateFunctionRegistry(): Promise<void> {
    let markdown = '# Function Registry\n\n';
    markdown += 'Complete registry of all functions in the codebase.\n\n';
    
    const sourceFiles = this.project.getSourceFiles();
    const functionsByFile = new Map<string, FunctionInfo[]>();
    
    for (const file of sourceFiles) {
      const functions = this.extractFunctions(file);
      if (functions.length > 0) {
        const relativePath = path.relative(process.cwd(), file.getFilePath());
        functionsByFile.set(relativePath, functions);
      }
    }
    
    // Sort files alphabetically
    const sortedFiles = Array.from(functionsByFile.keys()).sort();
    
    for (const filePath of sortedFiles) {
      const functions = functionsByFile.get(filePath)!;
      markdown += `## ${filePath}\n\n`;
      
      for (const func of functions) {
        markdown += `### ${func.name}\n`;
        markdown += `- **Location**: \`${func.file}:${func.line}\`\n`;
        markdown += `- **Async**: ${func.isAsync}\n`;
        markdown += `- **Exported**: ${func.isExported}\n`;
        markdown += `- **Parameters**: ${func.parameters.join(', ') || 'none'}\n`;
        markdown += `- **Return Type**: ${func.returnType}\n`;
        markdown += `- **Signature**:\n\`\`\`typescript\n${func.signature}\n\`\`\`\n\n`;
      }
    }
    
    fs.writeFileSync(
      path.join(this.manifestDir, 'FUNCTION_REGISTRY.md'),
      markdown
    );
  }
  
  private async generateExportRegistry(): Promise<void> {
    const exports: Record<string, ExportInfo[]> = {};
    
    for (const file of this.project.getSourceFiles()) {
      const relativePath = path.relative(process.cwd(), file.getFilePath());
      const fileExports: ExportInfo[] = [];
      
      file.getExportedDeclarations().forEach((declarations, name) => {
        if (declarations.length > 0) {
          const decl = declarations[0];
          fileExports.push({
            name: name,
            kind: decl.getKindName(),
            line: decl.getStartLineNumber(),
          });
        }
      });
      
      if (fileExports.length > 0) {
        exports[relativePath] = fileExports;
      }
    }
    
    fs.writeFileSync(
      path.join(this.manifestDir, 'EXPORT_REGISTRY.json'),
      JSON.stringify(exports, null, 2)
    );
  }
  
  private async generateImportGraph(): Promise<void> {
    const importGraph: Record<string, string[]> = {};
    
    for (const file of this.project.getSourceFiles()) {
      const relativePath = path.relative(process.cwd(), file.getFilePath());
      const imports = file.getImportDeclarations();
      
      if (imports.length > 0) {
        importGraph[relativePath] = imports
          .map(imp => imp.getModuleSpecifierValue())
          .filter(spec => !spec.startsWith('node:') && !spec.includes('node_modules'));
      }
    }
    
    fs.writeFileSync(
      path.join(this.manifestDir, 'IMPORT_GRAPH.yaml'),
      yaml.dump(importGraph, { indent: 2 })
    );
  }
  
  private async generateTechStack(): Promise<void> {
    const packageJson = this.getPackageJson();
    
    const techStack = {
      language: 'TypeScript',
      runtime: 'Node.js',
      packageManager: this.detectPackageManager(),
      dependencies: Object.keys(packageJson.dependencies || {}),
      devDependencies: Object.keys(packageJson.devDependencies || {}),
      scripts: Object.keys(packageJson.scripts || {}),
      typescript: {
        version: packageJson.devDependencies?.typescript || 'unknown',
        strict: this.isStrictMode(),
      },
      testing: this.detectTestingFramework(),
      bundler: this.detectBundler(),
      linter: this.detectLinter(),
    };
    
    fs.writeFileSync(
      path.join(this.manifestDir, 'TECH_STACK.json'),
      JSON.stringify(techStack, null, 2)
    );
  }
  
  private async generateCodePatterns(): Promise<void> {
    let markdown = '# Code Patterns\n\n';
    markdown += 'Detected patterns and conventions in the codebase.\n\n';
    
    const patterns = this.detectPatterns();
    
    markdown += '## Error Handling Patterns\n\n';
    patterns.error_handling.forEach(pattern => {
      markdown += `- ${pattern}\n`;
    });
    
    markdown += '\n## State Management Patterns\n\n';
    patterns.state_management.forEach(pattern => {
      markdown += `- ${pattern}\n`;
    });
    
    markdown += '\n## Data Flow Patterns\n\n';
    patterns.data_flow.forEach(pattern => {
      markdown += `- ${pattern}\n`;
    });
    
    markdown += '\n## Naming Conventions\n\n';
    markdown += this.detectNamingConventions();
    
    fs.writeFileSync(
      path.join(this.manifestDir, 'CODE_PATTERNS.md'),
      markdown
    );
  }
  
  private async generateAPISurface(): Promise<void> {
    const apiSurface = {
      public_exports: [] as any[],
      entry_points: [] as string[],
      cli_commands: [] as any[],
      rest_endpoints: [] as any[],
    };
    
    // Find main entry points
    const packageJson = this.getPackageJson();
    if (packageJson.main) {
      apiSurface.entry_points.push(packageJson.main);
    }
    if (packageJson.bin) {
      apiSurface.cli_commands = Object.entries(packageJson.bin).map(([name, path]) => ({
        name,
        path,
      }));
    }
    
    // Find public exports from index files
    const indexFiles = this.project.getSourceFiles().filter(f => 
      f.getBaseName() === 'index.ts' || f.getBaseName() === 'index.tsx'
    );
    
    for (const file of indexFiles) {
      const exports = Array.from(file.getExportedDeclarations().keys());
      if (exports.length > 0) {
        apiSurface.public_exports.push({
          file: path.relative(process.cwd(), file.getFilePath()),
          exports,
        });
      }
    }
    
    fs.writeFileSync(
      path.join(this.manifestDir, 'API_SURFACE.json'),
      JSON.stringify(apiSurface, null, 2)
    );
  }
  
  // Helper methods
  
  private getPackageJson(): any {
    const packagePath = path.join(process.cwd(), 'package.json');
    if (fs.existsSync(packagePath)) {
      return JSON.parse(fs.readFileSync(packagePath, 'utf-8'));
    }
    return {};
  }
  
  private detectFramework(): string {
    const packageJson = this.getPackageJson();
    const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    if (deps.react) return 'React';
    if (deps.vue) return 'Vue';
    if (deps.angular) return 'Angular';
    if (deps.express) return 'Express';
    if (deps.fastify) return 'Fastify';
    if (deps.next) return 'Next.js';
    if (deps.nuxt) return 'Nuxt';
    
    return 'Node.js';
  }
  
  private detectPackageManager(): string {
    if (fs.existsSync('bun.lock')) return 'bun';
    if (fs.existsSync('pnpm-lock.yaml')) return 'pnpm';
    if (fs.existsSync('yarn.lock')) return 'yarn';
    return 'npm';
  }
  
  private detectTestingFramework(): string {
    const packageJson = this.getPackageJson();
    const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    if (deps.vitest) return 'Vitest';
    if (deps.jest) return 'Jest';
    if (deps.mocha) return 'Mocha';
    if (deps['@testing-library/react']) return 'React Testing Library';
    
    return 'none';
  }
  
  private detectBundler(): string {
    const packageJson = this.getPackageJson();
    const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    if (deps.vite) return 'Vite';
    if (deps.webpack) return 'Webpack';
    if (deps.esbuild) return 'esbuild';
    if (deps.rollup) return 'Rollup';
    if (deps.tsdown) return 'tsdown';
    if (deps.parcel) return 'Parcel';
    
    return 'none';
  }
  
  private detectLinter(): string {
    const packageJson = this.getPackageJson();
    const deps = { ...packageJson.dependencies, ...packageJson.devDependencies };
    
    if (deps.eslint) return 'ESLint';
    if (deps.tslint) return 'TSLint';
    if (deps.biome) return 'Biome';
    
    return 'none';
  }
  
  private isStrictMode(): boolean {
    try {
      const tsConfig = JSON.parse(fs.readFileSync('tsconfig.json', 'utf-8'));
      return tsConfig.compilerOptions?.strict === true;
    } catch {
      return false;
    }
  }
  
  private countAllFunctions(): number {
    let count = 0;
    for (const file of this.project.getSourceFiles()) {
      count += file.getFunctions().length;
      file.getClasses().forEach(cls => {
        count += cls.getMethods().length;
      });
    }
    return count;
  }
  
  private countAllExports(): number {
    let count = 0;
    for (const file of this.project.getSourceFiles()) {
      count += file.getExportedDeclarations().size;
    }
    return count;
  }
  
  private countAsyncFunctions(): number {
    let count = 0;
    for (const file of this.project.getSourceFiles()) {
      file.getFunctions().forEach(func => {
        if (func.isAsync()) count++;
      });
      file.getClasses().forEach(cls => {
        cls.getMethods().forEach(method => {
          if (method.isAsync()) count++;
        });
      });
    }
    return count;
  }
  
  private countClasses(): number {
    let count = 0;
    for (const file of this.project.getSourceFiles()) {
      count += file.getClasses().length;
    }
    return count;
  }
  
  private countInterfaces(): number {
    let count = 0;
    for (const file of this.project.getSourceFiles()) {
      count += file.getInterfaces().length;
    }
    return count;
  }
  
  private analyzeKeyModules(): Array<any> {
    const modules: Array<any> = [];
    
    for (const file of this.project.getSourceFiles()) {
      const relativePath = path.relative(process.cwd(), file.getFilePath());
      
      // Skip test files and node_modules
      if (relativePath.includes('test') || relativePath.includes('node_modules')) {
        continue;
      }
      
      const exports = file.getExportedDeclarations().size;
      const imports = file.getImportDeclarations().length;
      const functions = file.getFunctions().length;
      
      // Consider it a key module if it has significant exports or functions
      if (exports > 3 || functions > 5) {
        modules.push({
          path: relativePath,
          exports,
          imports,
          functions,
        });
      }
    }
    
    // Sort by number of exports (descending)
    return modules.sort((a, b) => b.exports - a.exports).slice(0, 10);
  }
  
  private detectPatterns(): any {
    const patterns = {
      error_handling: [] as string[],
      state_management: [] as string[],
      data_flow: [] as string[],
    };
    
    let hasTryCatch = false;
    let hasAsyncAwait = false;
    let hasPromises = false;
    let hasObservables = false;
    let hasRedux = false;
    let hasContextAPI = false;
    
    for (const file of this.project.getSourceFiles()) {
      const text = file.getText();
      
      if (text.includes('try') && text.includes('catch')) hasTryCatch = true;
      if (text.includes('async') && text.includes('await')) hasAsyncAwait = true;
      if (text.includes('Promise')) hasPromises = true;
      if (text.includes('Observable')) hasObservables = true;
      if (text.includes('useReducer') || text.includes('redux')) hasRedux = true;
      if (text.includes('useContext') || text.includes('createContext')) hasContextAPI = true;
    }
    
    // Error handling patterns
    if (hasTryCatch) patterns.error_handling.push('Try-Catch blocks');
    if (hasPromises) patterns.error_handling.push('Promise rejection handling');
    if (hasAsyncAwait) patterns.error_handling.push('Async/Await error handling');
    
    // State management patterns
    if (hasRedux) patterns.state_management.push('Redux state management');
    if (hasContextAPI) patterns.state_management.push('React Context API');
    
    // Data flow patterns
    if (hasAsyncAwait) patterns.data_flow.push('Async/Await');
    if (hasPromises) patterns.data_flow.push('Promises');
    if (hasObservables) patterns.data_flow.push('Observables/RxJS');
    
    return patterns;
  }
  
  private detectNamingConventions(): string {
    let conventions = '';
    
    // Analyze file naming
    const files = this.project.getSourceFiles();
    const hasKebabCase = files.some(f => f.getBaseName().includes('-'));
    const hasCamelCase = files.some(f => /[a-z][A-Z]/.test(f.getBaseName()));
    
    conventions += '- **Files**: ';
    if (hasKebabCase) conventions += 'kebab-case';
    else if (hasCamelCase) conventions += 'camelCase';
    else conventions += 'lowercase';
    conventions += '\n';
    
    // Analyze function naming
    conventions += '- **Functions**: camelCase\n';
    conventions += '- **Classes**: PascalCase\n';
    conventions += '- **Constants**: UPPER_SNAKE_CASE\n';
    conventions += '- **Interfaces**: PascalCase with "I" prefix or without\n';
    
    return conventions;
  }
  
  private extractFunctions(file: SourceFile): FunctionInfo[] {
    const functions: FunctionInfo[] = [];
    const relativePath = path.relative(process.cwd(), file.getFilePath());
    
    // Get standalone functions
    file.getFunctions().forEach(func => {
      functions.push(this.getFunctionInfo(func, relativePath));
    });
    
    // Get class methods
    file.getClasses().forEach(cls => {
      cls.getMethods().forEach(method => {
        functions.push(this.getMethodInfo(method, relativePath, cls.getName() || 'anonymous'));
      });
    });
    
    // Get arrow functions assigned to variables
    file.getVariableDeclarations().forEach(varDecl => {
      const initializer = varDecl.getInitializer();
      if (Node.isArrowFunction(initializer)) {
        functions.push(this.getArrowFunctionInfo(initializer, varDecl.getName(), relativePath));
      }
    });
    
    return functions;
  }
  
  private getFunctionInfo(func: FunctionDeclaration, filePath: string): FunctionInfo {
    return {
      name: func.getName() || 'anonymous',
      file: filePath,
      line: func.getStartLineNumber(),
      signature: func.getText().split('{')[0].trim(),
      isAsync: func.isAsync(),
      isExported: func.isExported(),
      parameters: func.getParameters().map(p => p.getName()),
      returnType: func.getReturnType().getText(),
    };
  }
  
  private getMethodInfo(method: MethodDeclaration, filePath: string, className: string): FunctionInfo {
    return {
      name: `${className}.${method.getName()}`,
      file: filePath,
      line: method.getStartLineNumber(),
      signature: method.getText().split('{')[0].trim(),
      isAsync: method.isAsync(),
      isExported: method.getParent()?.getParent()?.getKind() === SyntaxKind.SourceFile,
      parameters: method.getParameters().map(p => p.getName()),
      returnType: method.getReturnType().getText(),
    };
  }
  
  private getArrowFunctionInfo(arrow: ArrowFunction, name: string, filePath: string): FunctionInfo {
    return {
      name: name,
      file: filePath,
      line: arrow.getStartLineNumber(),
      signature: arrow.getText().split('=>')[0].trim() + ' =>',
      isAsync: arrow.isAsync(),
      isExported: false, // Would need more complex logic to determine
      parameters: arrow.getParameters().map(p => p.getName()),
      returnType: arrow.getReturnType().getText(),
    };
  }
}

// Main execution
async function main() {
  try {
    const generator = new ManifestGenerator();
    await generator.generateAll();
  } catch (error) {
    console.error('❌ Error generating manifests:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export { ManifestGenerator };