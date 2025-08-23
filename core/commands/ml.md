---
description: Execute comprehensive ML development using the machine learning framework
argument-hint: [project-path]
---

# ML Development Framework Execution

## Initialize ML Development Framework

Use the comprehensive ML development framework from ~/.claude/process-templates-n-prompts/ml-development/

### Step 1: Check for Existing ML Infrastructure
First, check if `.claude/ml/` exists in the project directory (use $ARGUMENTS if provided, otherwise current directory).

### Step 2: Setup Framework Files
If ML framework doesn't exist in the project:
```bash
mkdir -p .claude/ml
cp ~/.claude/process-templates-n-prompts/ml-development/*.md .claude/ml/
```

If it does exist, note what's already there and proceed to update/extend rather than replace.

### Step 3: Load Framework Components

1. **Read ml-prompt.md** - Understand the ML development philosophy and methodology
   - Focus on data-driven development and experimentation
   - Review MLOps best practices and model lifecycle management
   - Understand ethical AI and responsible ML practices

2. **Load ml-template.md** - Use as the structure for ML project organization
   - Reference for experiment tracking structures
   - Use naming conventions from template
   - Follow model development templates
   - Use evaluation and monitoring formats

3. **Follow ml-checklist.md** - Execute phases systematically
   - Start with Phase 0: Problem Definition & Data Discovery
   - Check off items as completed
   - Document experiments and model performance
   - Track ML metrics and model quality

## Execution Instructions

### Phase 0: Problem Definition & Data Discovery (MANDATORY FIRST)
- Define ML problem type and success criteria
- Assess data availability, quality, and requirements
- Identify features, labels, and target variables
- Document baseline performance and benchmarks
- Review existing models or similar solutions
- Establish ethical considerations and bias assessment

### Subsequent Phases
Continue through all phases in order:
- Phase 1: Data Preparation & Feature Engineering
- Phase 2: Model Development & Experimentation
- Phase 3: Model Training & Hyperparameter Tuning
- Phase 4: Model Evaluation & Validation
- Phase 5: Model Deployment & Serving
- Phase 6: Monitoring & Maintenance
- Phase 7: Model Evolution & Improvement

## Key Principles

1. **ALWAYS start with problem definition and data understanding**
2. **Follow rigorous experimentation and version control practices**
3. **Implement comprehensive model evaluation and validation**
4. **Ensure reproducibility and experiment tracking**
5. **Plan for model monitoring and drift detection**
6. **Address bias, fairness, and ethical considerations**

## ML Goals
- Clear problem definition with measurable success criteria
- Robust data pipeline with quality assurance
- Reproducible experiments with proper version control
- Comprehensive model evaluation and validation
- Production-ready deployment with monitoring
- Ethical and responsible AI implementation

## Progress Tracking
Update the ml-checklist.md with progress markers:
- [ ] Not started
- [~] In progress
- [x] Complete
- [!] Blocked

## Output Artifacts
Ensure these are created/updated:
1. problem-definition.md - ML problem statement and requirements
2. data-analysis.ipynb - Exploratory data analysis
3. feature-engineering.md - Feature creation and selection documentation
4. model-experiments/ - Experiment tracking and results
5. model-evaluation.md - Performance metrics and validation results
6. deployment-guide.md - Model serving and deployment instructions
7. monitoring-dashboard.md - Model performance monitoring setup
8. CHANGELOG.md - Document all model and pipeline changes

## Project Path
Working directory: ${ARGUMENTS:-.}

Remember: In ML, data is king, experiments are your compass, and monitoring is your safety net. Build responsibly, evaluate thoroughly, deploy confidently.