---
description: "Master orchestrator for AI-assisted development - guides you through all 6 phases of the development lifecycle"
arguments: project_name [optional_start_phase]
---

# 🚀 AI-Assisted Development Orchestrator

You've initiated the comprehensive AI-assisted development workflow. I'll guide you through all 6 phases to build your product in a structured 7-day cycle.

## 📋 PROJECT INITIALIZATION

Project: **${1:-NewProject}**
Starting Phase: **${2:-discovery}**
Development Cycle: **7 days**
Frameworks Available: **18 specialized frameworks**

Let me check your project configuration and set up the development environment.

```bash
# Check for existing project configuration
if [ -f ".claude/PROJECT_CONFIG.yaml" ]; then
    echo "✅ Found existing project configuration"
    echo "📊 Loading project state..."
else
    echo "🆕 Initializing new project: ${1:-NewProject}"
    echo "📁 Creating .claude directory structure..."
    mkdir -p .claude/{planning,development,quality,deployment,operations}
    
    # Copy master configuration
    cp ~/.claude/process-templates-n-prompts/PROJECT_CONFIG.yaml .claude/
    
    echo "✅ Project structure created"
fi
```

## 🎯 DEVELOPMENT LIFECYCLE PHASES

I'll now guide you through the complete development cycle:

### 🔍 PHASE 0: DISCOVERY & DEFINITION (Days 0-1)
**Goal**: Understand business context, define requirements, validate feasibility

```bash
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 0: DISCOVERY & DEFINITION"
echo "Duration: 1-2 days | Frameworks: 3"
echo "═══════════════════════════════════════════════════════════════"
```

**0.1 Business Discovery** `/0.1discover`
- Business context analysis and problem definition
- Stakeholder identification and alignment
- Initial solution approach validation
- Business objectives and success criteria
- **Deliverables**: Project Brief with complete business context

**0.2 Solution Definition** `/0.2define`
- Transform business needs into detailed requirements
- Create user stories with acceptance criteria
- Define non-functional requirements and constraints
- Establish epic breakdown and roadmap
- **Deliverables**: Product Requirements Document (PRD)

**0.3 Validation & Feasibility** `/0.3validate`
- Multi-dimensional risk assessment
- Technical feasibility validation
- Market opportunity analysis
- Resource requirements planning
- **Deliverables**: Validation Summary, Risk Register, Success Metrics

### 📐 PHASE 1: PLANNING (Days 1-2)
**Goal**: Define architecture, understand users, establish security

```bash
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 1: PLANNING & DESIGN"
echo "Duration: 2 days | Frameworks: 3"
echo "═══════════════════════════════════════════════════════════════"
```

**1.1 Architecture Framework** `/1.1arch`
- Define system components and boundaries
- Select technology stack
- Create high-level design
- Document key decisions (ADRs)
- **Deliverables**: System architecture document, technology decisions

**1.2 UX Research Framework** `/1.2ux`
- Understand user needs and pain points
- Create user personas and journey maps
- Define success metrics
- Design information architecture
- **Deliverables**: User research findings, design system

**1.3 Security Framework** `/1.3security`
- Threat modeling (STRIDE)
- Define security requirements
- Plan authentication/authorization
- Compliance mapping
- **Deliverables**: Security blueprint, compliance matrix

### ⚡ PHASE 2: DEVELOPMENT (Days 2-4)
**Goal**: Build core features with proper APIs and data layer

```bash
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 2: DEVELOPMENT & IMPLEMENTATION"
echo "Duration: 2 days | Frameworks: 4"
echo "═══════════════════════════════════════════════════════════════"
```

**2.1 Feature Development** `/2.1feature`
- Implement user stories
- Build UI components
- Integrate with backend
- **Deliverables**: Working features, component library

**2.2 API Development** `/2.2api`
- Design RESTful/GraphQL APIs
- Implement endpoints
- Add authentication
- **Deliverables**: API documentation, working endpoints

**2.3 Database Design** `/2.3db`
- Design schemas
- Optimize queries
- Set up migrations
- **Deliverables**: Database schema, migration scripts

**2.4 ML Development** `/2.4ml` *(Optional)*
- Data preparation
- Model training
- Evaluation & deployment
- **Deliverables**: Trained models, ML pipeline

### ✅ PHASE 3: QUALITY (Day 5)
**Goal**: Ensure code quality, comprehensive testing, and documentation

```bash
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 3: QUALITY ASSURANCE"
echo "Duration: 1 day | Frameworks: 3"
echo "═══════════════════════════════════════════════════════════════"
```

**3.1 Code Review & Quality** `/3.1review`
- Static analysis
- Code review
- Refactoring
- **Deliverables**: Clean code, review reports

**3.2 Testing** `/3.2test`
- Unit tests
- Integration tests
- E2E tests
- **Deliverables**: Test suites, coverage reports

**3.3 Documentation** `/3.3docs`
- API documentation
- User guides
- Developer docs
- **Deliverables**: Complete documentation

### 🚀 PHASE 4: DEPLOYMENT (Day 6)
**Goal**: Deploy to production with monitoring and optimization

```bash
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 4: DEPLOYMENT & LAUNCH"
echo "Duration: 1 day | Frameworks: 3"
echo "═══════════════════════════════════════════════════════════════"
```

**4.1 Deployment** `/4.1deploy`
- CI/CD pipeline
- Infrastructure setup
- Production deployment
- **Deliverables**: Deployed application, CI/CD pipeline

**4.2 Monitoring** `/4.2monitor`
- Set up observability
- Configure alerts
- Create dashboards
- **Deliverables**: Monitoring dashboards, alert rules

**4.3 Performance** `/4.3perf`
- Performance testing
- Optimization
- Caching strategy
- **Deliverables**: Performance reports, optimizations

### 🔄 PHASE 5: OPERATIONS (Ongoing)
**Goal**: Maintain, scale, and evolve the system

```bash
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 5: OPERATIONS & GROWTH"
echo "Duration: Ongoing | Frameworks: 3"
echo "═══════════════════════════════════════════════════════════════"
```

**5.1 Incident Response** `/5.1incident`
- Incident management
- Root cause analysis
- Runbooks
- **Deliverables**: Incident procedures, postmortems

**5.2 Integration** `/5.2integrate`
- Third-party integrations
- API connections
- Event streaming
- **Deliverables**: Integration documentation

**5.3 Data Pipeline** `/5.3data`
- ETL/ELT processes
- Data quality
- Analytics
- **Deliverables**: Data pipelines, quality reports

## 🎬 GETTING STARTED

Based on your project "${1:-NewProject}", here's your recommended action plan:

### Immediate Next Steps:

1. **Start Discovery Phase** (recommended for new projects):
   ```bash
   /0.1discover # Begin with business discovery
   /0.2define   # Define requirements and user stories
   /0.3validate # Validate feasibility and assess risks
   ```

2. **Start Planning Phase** (if Phase 0 complete):
   ```bash
   /1.1arch     # Begin with architecture design
   /1.2ux       # Understand your users
   /1.3security # Establish security baseline
   ```

3. **Jump to specific phase** (if continuing):
   ```bash
   /${2:-0.1discover}  # Start from specified phase
   ```

4. **View all phases**:
   ```bash
   /phases      # See complete phase guide
   ```

## 📊 PROGRESS TRACKING

Your progress will be tracked in `.claude/PROJECT_CONFIG.yaml`:
- ⏳ **Pending**: Not started
- 🔄 **Active**: Currently working
- ✅ **Completed**: Finished

## 🎯 SUCCESS CRITERIA

Each phase has specific completion criteria:
- **Discovery**: Business context documented, requirements defined, feasibility validated
- **Planning**: Architecture documented, users understood, security planned
- **Development**: Features working, APIs tested, database optimized
- **Quality**: 80%+ test coverage, documentation complete
- **Deployment**: Application live, monitoring active
- **Operations**: Incidents < 1%, integrations working

## 💡 TIPS FOR SUCCESS

1. **Follow the phases** - They build on each other
2. **Don't skip discovery** - Understanding the problem saves time later
3. **Don't skip planning** - Architecture decisions impact everything
4. **Test early and often** - Catch issues before production
5. **Document as you go** - Future you will thank you
6. **Monitor everything** - You can't fix what you can't see

## 🚦 READY TO BEGIN?

Choose your starting point:

**Option 1: Start fresh** (recommended for new projects)
```bash
/0.1discover  # Begin with business discovery
```

**Option 2: Continue from specific phase**
```bash
/${2:-phases}  # View phases or jump to specific one
```

**Option 3: Skip discovery for well-defined projects**
```bash
/1.1arch  # Begin with architecture (if requirements are clear)
```

**Option 4: Quick start for MVPs** (not recommended)
```bash
/2.1feature  # Jump straight to feature development (risky but fast)
```

---

**Remember**: The 7-day cycle is designed to deliver working software quickly while maintaining quality. Phase 0 discovery prevents costly mistakes and ensures you're building the right solution. Each framework provides specialized AI assistance to accelerate your work by 25-30% overall, with some tasks seeing up to 80% time savings.

Let's build something amazing together! 🚀