# 📋 AI Development Rules - Switches & Commands Reference

## 🚀 Quick Usage

### **Switches (Inline with any prompt)**
```bash
# Add --rules to any prompt to enforce mandatory AI development rules
"Implement user authentication --rules"
"Fix the bug in payment processing --rules -u"  # Combine with other switches
```

### **Slash Commands**
```bash
/rules           # Display comprehensive AI development rules
/xrules [task]   # Execute task with mandatory rules enforcement
/xrule [task]    # Shorthand for /xrules
```

## 🎯 Combined Switch Commands

### **Rules + Other Switches**
```bash
/xur [task]    # Ultrathink + Research + Rules
/xuor [task]   # Ultrathink + Optimize + Rules  
/xpr [task]    # Plan + Rules
/xall [task]   # ALL switches including Rules (maximum enforcement)
```

## 📚 Available Switches

### **Core Switches**
- `-u` or `--ultra`: Deep thinking and analysis
- `-r` or `--research`: Thorough research
- `-o` or `--optimize`: Performance optimization
- `-t` or `--think`: Step-by-step reasoning
- `-p` or `--plan`: Detailed planning

### **NEW: Rules Switch**
- `--rules`: **MANDATORY AI development rules enforcement**

## ⚠️ What --rules Enforces

When you use `--rules` or any rules-based command, Claude MUST:

1. **Planning & Discovery**
   - Research existing codebase BEFORE starting
   - Plan implementation BEFORE coding
   - Analyze dependencies and architecture FIRST

2. **Code Quality & Security**
   - NIST SP 800-218A compliance
   - Security by design
   - Risk-based approach

3. **Workflow & Process**
   - Review before deploy
   - Test-driven development
   - Mandatory code reviews

4. **Testing & Validation**
   - Write tests FIRST
   - Comprehensive coverage
   - AI-specific testing

5. **Documentation & Compliance**
   - EU AI Act compliance
   - Audit trails
   - Clear AI attribution

6. **Dependency & Architecture**
   - Eliminate duplicates
   - Proper dependency management
   - Architecture consistency

7. **AI-Specific Development**
   - Responsible AI practices
   - Human oversight
   - Validation requirements

## 💡 Examples

### **Simple Rules Enforcement**
```bash
"Create a new API endpoint --rules"
# Claude will research first, plan, write tests, then implement
```

### **Combined Switches**
```bash
"Refactor the authentication system --rules -u -o"
# Rules + Ultrathink + Optimize
```

### **Using Slash Commands**
```bash
/xrules implement payment processing with Stripe
# Full rules enforcement for the task

/xall design a microservices architecture
# ALL switches including rules - maximum analysis
```

## 📖 Full Documentation

Complete rules documentation: `~/claude-automations/rules.md`

Based on:
- NIST AI Risk Management Framework (2024-2025)
- EU AI Act Compliance requirements
- Industry Security Best Practices
- Claude Code Integration Standards

---

**Remember: When in doubt, add `--rules` to ensure compliance!**