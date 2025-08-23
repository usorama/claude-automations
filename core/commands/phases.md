# Development Phases Guide

## 📋 Complete Phase Sequence (18 Commands)

### 🔍 Phase 0: Discovery & Definition (Foundation)
- **`/0.1discover`** - Business Discovery Framework → Analyzes business context and problem definition
- **`/0.2define`** - Solution Definition Framework → Creates detailed requirements and user stories
- **`/0.3validate`** - Validation & Feasibility Framework → Validates approach and assesses risks

### 🎯 Phase 1: Planning (Architecture)
- **`/1.1arch`** - Architecture Framework → Sets system design foundation
- **`/1.2ux`** - UX Research Framework → Defines user experience strategy  
- **`/1.3security`** - Security Framework → Establishes security requirements

### 🔨 Phase 2: Development (Build Core)
- **`/2.1feature`** - Feature Development → Implements core functionality
- **`/2.2api`** - API Development → Creates service interfaces
- **`/2.3db`** - Database Design → Structures data layer
- **`/2.4ml`** - ML Development → Adds intelligence capabilities *(optional)*

### ✅ Phase 3: Quality (Validate)
- **`/3.1review`** - Code Review & Quality → Ensures code standards
- **`/3.2test`** - Testing Framework → Validates functionality
- **`/3.3docs`** - Documentation → Creates knowledge base

### 🚀 Phase 4: Deployment (Ship)
- **`/4.1deploy`** - Deployment & DevOps → Automates releases
- **`/4.2monitor`** - Monitoring & Observability → Tracks performance
- **`/4.3perf`** - Performance Optimization → Maximizes efficiency

### ⚡ Phase 5: Operations (Scale)
- **`/5.1incident`** - Incident Response → Handles emergencies
- **`/5.2integrate`** - Integration Framework → Connects systems
- **`/5.3data`** - Data Pipeline → Processes information flow

## 🔄 Recommended Activation Order

0. **Start Discovery**: `/0.1discover` → `/0.2define` → `/0.3validate`
1. **Continue Planning**: `/1.1arch` → `/1.2ux` → `/1.3security`
2. **Begin Development**: `/2.1feature` → `/2.2api` → `/2.3db` → `/2.4ml`
3. **Ensure Quality**: `/3.1review` → `/3.2test` → `/3.3docs`
4. **Deploy System**: `/4.1deploy` → `/4.2monitor` → `/4.3perf`
5. **Scale Operations**: `/5.1incident` → `/5.2integrate` → `/5.3data`

## ⚠️ Dependencies & Prerequisites
- **Phase 0** should complete before Phase 1 for optimal results
- **Phase 1** must complete before Phase 2
- **Phase 2** core features before quality validation
- **Phase 3** quality gates before deployment
- **Phase 4** deployment before operations scaling
- **Phase 5** can be activated incrementally

## 🎯 Quick Start Examples
```bash
# Complete discovery phase (recommended)
/0.1discover → /0.2define → /0.3validate

# Complete planning phase
/1.1arch → /1.2ux → /1.3security

# Core development cycle  
/2.1feature → /2.2api → /3.1review → /3.2test

# Production readiness
/4.1deploy → /4.2monitor → /5.1incident
```

**Framework Location**: `~/.claude/process-templates-n-prompts/`