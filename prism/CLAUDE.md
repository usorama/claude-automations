# PRISM - Proactive Real-time Intelligence System for Manifests
## Claude Code Context Optimization System

---

## 🎯 What is PRISM?

PRISM is an LLM-driven context engineering system built **exclusively for Claude Code**. It transforms how Claude Code agents receive context - from loading 200KB+ of mostly irrelevant manifests to receiving intelligently selected, task-specific context through MCP (Model Context Protocol).

**Think of it this way**: 
- **Before PRISM**: Agents are given an entire library when they need one book
- **With PRISM**: Agents receive exactly the chapters they need, when they need them

---

## 🚀 Core Purpose

**PRISM exists for ONE reason**: Make Claude Code agents more effective by giving them precisely the context they need through intelligent LLM-based selection rather than dumping everything.

### The Problem PRISM Solves
- Agents currently load 200KB+ of context
- Only ~10% is actually relevant to their task
- Context window gets bloated with unnecessary information
- Agents struggle to find what they need in the noise

### The PRISM Solution
- LLM analyzes task intent and selects relevant manifests
- Context engineered specifically for each agent and task
- Quality prioritized over arbitrary size constraints
- Continuous learning from usage patterns

---

## 📊 SIPOC Architecture

```
SUPPLIER → INPUT → PROCESS → OUTPUT → CUSTOMER
```

- **SUPPLIER**: Claude Code hooks collecting manifest data
- **INPUT**: Manifests stored in SQLite database
- **PROCESS**: LLM (Ollama) + MCP tools for context optimization
- **OUTPUT**: Optimally engineered context package
- **CUSTOMER**: Claude Code Agents (100+ specialists)

---

## 🔧 How PRISM Works

### 1. Interception
When you invoke an agent with the Task tool, PRISM intercepts via PreToolUse hook

### 2. Analysis
PRISM analyzes your task description using Ollama LLM to understand intent

### 3. Selection
Based on intent, PRISM queries SQLite for relevant manifests

### 4. Engineering
LLM engineers optimal context - not constrained by size, focused on quality

### 5. Delivery
Context delivered to agent via MCP tools

### 6. Learning
PRISM tracks what worked and continuously improves

---

## 📁 Key Documents

### Essential Reading
1. **[PRISM_PRD.md](./docs/PRISM_PRD.md)** - Product Requirements Document (START HERE)
2. **[EPIC_CLAUDE_CODE_INTEGRATION.md](./EPIC_CLAUDE_CODE_INTEGRATION.md)** - Detailed implementation plan
3. **[REALITY_CHECK_REPORT.md](./docs/REALITY_CHECK_REPORT.md)** - What actually exists vs claims

### Implementation Guides
- **[INTEGRATION_GUIDE.md](./docs/INTEGRATION_GUIDE.md)** - How to integrate PRISM
- **[QUICK_START.md](./QUICK_START.md)** - Get started quickly

---

## 🏗️ Current Status

### ✅ What's Built (60%)
- Context DNA Profiler - Agent learning profiles
- Context Router - Intent analysis
- Manifest Updater - Real-time updates
- Documentation Syncer - Auto-sync docs
- PRISM Orchestrator - Component coordination
- Dashboard - Monitoring & observability

### 🔧 What's Needed (40%)
- MCP Server implementation
- SQLite intelligence database
- Ollama LLM integration
- Claude Code hook integration
- Agent communication protocol

---

## 💡 For Claude Code Agents

**If you're a Claude Code agent reading this**, here's what you need to know:

1. **PRISM is being built FOR YOU** - Every feature serves agent effectiveness
2. **You'll access PRISM via MCP tools** - No file manipulation needed
3. **Your context will be optimized automatically** - No action required
4. **Quality over quantity** - You'll get what you need, not everything
5. **It learns from you** - The more you use it, the better it gets

### How to Use PRISM (Once Deployed)

```python
# As an agent, you'll be able to:
prism_tools.get_optimal_context(
    agent_type="frontend-developer",
    task="implement user authentication"
)
# Returns: Only auth-related manifests, not entire codebase
```

---

## 🎯 Success Metrics

### What We're Optimizing For
- **Context Relevance**: >95% (from ~10% currently)
- **Agent Success Rate**: +20% improvement
- **Response Time**: <1 second
- **Continuous Learning**: Gets smarter with use

### What We're NOT Optimizing For
- Arbitrary size limits (like <20KB)
- Speed at the cost of quality
- One-size-fits-all solutions

---

## 🛠️ Technical Components

### Core Modules
```
prism/src/
├── prism_orchestrator.py    # Master coordinator
├── context_router.py        # Intent analyzer
├── manifest_updater.py      # Real-time updates
├── documentation_syncer.py  # Doc sync
└── prism_dashboard.py      # Monitoring

git-intelligence/src/
└── context_dna.py          # Agent profiles & learning
```

### Integration Points
```
~/.claude-code/mcp/global.json  # MCP server registration
~/.claude/settings.json         # Hook configuration
~/.claude/prism/intelligence.db # SQLite database
```

---

## 🚦 Quick Status Check

To check PRISM status:
```bash
# Test PRISM components
python3 ~/claude-automations/prism/test_prism.py

# View dashboard
python3 ~/claude-automations/prism/src/prism_dashboard.py

# Check orchestrator health
python3 ~/claude-automations/prism/src/prism_orchestrator.py --health
```

---

## 📈 Vision

**The End Goal**: Every Claude Code agent receives perfectly tailored context for their specific task, leading to:
- Faster task completion
- Higher success rates
- Less token usage
- Better code quality
- Happier developers

---

## ⚠️ Important Notes

1. **PRISM is Claude Code specific** - Not a general-purpose tool
2. **Quality > Size** - We don't constrain to arbitrary limits
3. **LLM-driven** - Uses Ollama for intelligent decisions
4. **Learning system** - Improves with every use
5. **MCP-based** - Clean integration via Model Context Protocol

---

## 🤝 Contributing

PRISM is part of the claude-automations ecosystem. To contribute:
1. Read the PRD and Epic first
2. Ensure changes align with Claude Code architecture
3. Test with actual Claude Code agents
4. Document your changes

---

**Remember**: PRISM exists to make YOU (Claude Code agents) more effective. Every line of code, every optimization, every feature serves this single purpose.

---

*Last Updated: August 25, 2025*  
*PRISM Version: 2.0 (SIPOC Architecture)*  
*Status: 60% Complete, MCP Integration In Progress*