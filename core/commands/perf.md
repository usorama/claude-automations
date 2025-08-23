---
description: Execute comprehensive performance optimization using the performance framework
argument-hint: [project-path]
---

# Performance Optimization Framework Execution

## Initialize Performance Framework

Use the comprehensive performance framework from ~/.claude/process-templates-n-prompts/performance/

### Step 1: Check for Existing Performance Infrastructure
First, check if `.claude/performance/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If performance framework doesn't exist in the project:
```bash
mkdir -p .claude/performance
cp ~/.claude/process-templates-n-prompts/performance/*.md .claude/performance/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read performance-prompt.md** - Understand the performance optimization philosophy and methodology
   - Focus on performance budgets, core web vitals, and user experience metrics
   - Review profiling, benchmarking, and optimization strategies
   - Understand load testing and capacity planning approaches

2. **Load performance-template.md** - Use as the structure for performance documentation
   - Reference for performance test configurations
   - Use benchmarking and profiling templates
   - Follow optimization implementation templates
   - Use performance monitoring and reporting formats

3. **Follow performance-checklist.md** - Execute phases systematically
   - Start with Phase 0: Performance Baseline & Assessment
   - Check off items as completed
   - Document optimization implementations
   - Track performance metrics and improvements

## Execution Instructions

### Phase 0: Performance Baseline & Assessment (MANDATORY FIRST)
- Establish current performance baselines and metrics
- Identify performance bottlenecks and critical paths
- Document user experience requirements and expectations
- Map system architecture and potential optimization points
- Review existing performance tools and monitoring
- Set performance budgets and optimization targets

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Performance Profiling & Analysis
- Phase 2: Frontend Optimization & Core Web Vitals
- Phase 3: Backend Optimization & Database Tuning
- Phase 4: Caching Strategy & Implementation
- Phase 5: Load Testing & Capacity Planning
- Phase 6: Performance Monitoring & Alerting
- Phase 7: Continuous Performance Optimization

## Key Principles

1. **ALWAYS measure before optimizing to establish baselines**
2. **Focus on user-perceived performance and core web vitals**
3. **Optimize the critical path and highest-impact bottlenecks**
4. **Implement caching at multiple levels strategically**
5. **Test performance under realistic load conditions**
6. **Monitor performance continuously and alert on regressions**

## Performance Goals
- Meet or exceed core web vitals thresholds (LCP, FID, CLS)
- Achieve target response times for critical user journeys
- Optimize resource utilization and system efficiency
- Implement effective caching strategies
- Pass load testing under peak traffic scenarios
- Maintain performance SLAs with proactive monitoring

## Progress Tracking
Update the performance-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. performance-baseline.md - Current performance metrics and benchmarks
2. profiling-results/ - Performance profiling data and analysis
3. optimization-implementations.md - Applied performance improvements
4. caching-strategy.md - Multi-level caching implementation
5. load-testing-reports/ - Load testing results and capacity analysis
6. performance-monitoring.md - Continuous performance monitoring setup
7. performance-budget.md - Performance budgets and alerting thresholds
8. CHANGELOG.md - Document all performance changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: Performance is a feature, not an afterthought. Measure first, optimize systematically, monitor continuously, never stop improving.