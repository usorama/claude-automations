# 🚀 AI Developer Rules & Guidelines

**Version 2.0** | Last Updated: August 23, 2025  
**Compliance**: NIST AI Framework, EU AI Act 2024-2025, Industry Best Practices

---

## 🎯 Purpose

These rules ensure AI developers build secure, reliable, and compliant digital products while mitigating risks inherent in AI-assisted development. These guidelines are **mandatory** for all development work and are based on NIST AI Risk Management Framework, EU AI Act requirements, and industry best practices.

---

## 📋 Rule Categories

### 1. 🔍 **Planning & Discovery Rules**

#### **Always Research First**
Research existing codebase architecture, patterns, and implementations thoroughly before writing any new code. Use context7 MCP server and web search to understand current solutions, dependencies, and architectural decisions.

**Safety**: Do not start coding without completing discovery phase and understanding existing implementations.

---

#### **Plan Implementation Before Execution**  
Create detailed implementation plans that include architecture decisions, dependency analysis, testing strategy, and integration approach. Document your approach before beginning development.

**Safety**: Do not begin implementation without a clear, documented plan approved through proper channels.

---

#### **Analyze Dependencies and Manifests**
Review all package.json, requirements.txt, Cargo.toml, and other manifest files to understand existing dependencies, versions, and potential conflicts before adding new dependencies.

**Safety**: Do not add dependencies without analyzing existing ones for conflicts, security vulnerabilities, or duplication.

---

#### **Validate Project Structure**
Understand the existing project structure, coding standards, frameworks, and architectural patterns before making changes. Follow established conventions consistently.

**Safety**: Do not violate existing architectural patterns or create inconsistent code structures.

---

### 2. 🔒 **Code Quality & Security Rules**

#### **Implement Secure Development Practices (NIST SP 800-218A)**
Follow NIST secure software development framework specifically tailored for generative AI systems. This includes securing model weights, training data, and integration points throughout the development lifecycle.

**Safety**: Do not deploy code that hasn't undergone security review for AI-specific vulnerabilities including data poisoning, model tampering, and inference attacks.

---

#### **Apply Risk-Based Development Approach**
Assess and document risks associated with AI features using NIST AI Risk Management Framework. Categorize systems based on risk levels (prohibited, high-risk, limited-risk) and apply appropriate safeguards.

**Safety**: Do not implement AI features without proper risk assessment and mitigation strategies.

---

#### **Maintain Comprehensive Documentation**
Document all AI-generated code with clear attribution, modification history, and rationale for integration. Include training data sources, model capabilities, and known limitations.

**Safety**: Do not deploy AI features without complete documentation of capabilities, limitations, and safety measures.

---

#### **Ensure Human Oversight Capabilities**
Build systems that allow meaningful human supervision and intervention. Include override mechanisms, audit trails, and clear escalation paths for AI-assisted decisions.

**Safety**: Do not create AI systems that operate without human oversight capabilities or clear accountability chains.

---

### 3. ⚡ **Workflow & Process Rules**

#### **Review Before Deploy Methodology**
Implement mandatory code review for all AI-generated code with enhanced focus on logic errors, integration issues, and security vulnerabilities. Use systematic review checklists.

**Safety**: Do not deploy AI-generated code without thorough human review and validation by qualified developers.

---

#### **Practice Test-Driven Development with AI**
Write comprehensive tests first, then use AI to generate implementation code. Tests should strongly define business requirements, schemas, and implementation assumptions.

**Safety**: Do not generate implementation code without comprehensive test coverage that validates expected behavior.

---

#### **Validate Context and Requirements**
Ensure AI tools receive complete context about business requirements, existing architecture, and integration constraints. Provide detailed, specific prompts with relevant technical details.

**Safety**: Do not use AI tools without providing complete context about requirements, constraints, and existing system architecture.

---

#### **Implement Continuous Quality Monitoring**
Establish automated monitoring for code quality, security vulnerabilities, and performance degradation. Include AI-specific metrics for model drift and output quality.

**Safety**: Do not deploy AI systems without comprehensive monitoring and alerting mechanisms.

---

### 4. 🧪 **Testing & Validation Rules**

#### **Comprehensive Test Coverage Requirements**
Achieve minimum 80% code coverage with focus on edge cases, error conditions, and integration points. Include AI-specific tests for hallucination detection and output validation.

**Safety**: Do not consider features complete without comprehensive test suites that cover normal, edge, and failure scenarios.

---

#### **AI-Specific Testing Protocols**
Test for AI-specific vulnerabilities including prompt injection, data leakage, bias amplification, and adversarial inputs. Include red teaming exercises for high-risk systems.

**Safety**: Do not deploy AI features without testing for AI-specific attack vectors and failure modes.

---

#### **Integration and End-to-End Testing**
Verify that AI-generated code integrates correctly with existing systems and doesn't introduce regressions or security vulnerabilities.

**Safety**: Do not deploy changes without full integration testing that validates system-wide behavior.

---

#### **Performance and Scalability Validation**
Test AI features under realistic load conditions and validate performance characteristics. Include monitoring for resource usage and response times.

**Safety**: Do not deploy AI systems without validating performance and scalability requirements under realistic conditions.

---

### 5. 📚 **Documentation & Compliance Rules**

#### **EU AI Act Compliance (2024-2025)**
Ensure compliance with EU AI Act requirements including risk categorization, transparency obligations, and audit trail maintenance. Document compliance measures and evidence.

**Safety**: Do not deploy AI systems in EU markets without documented compliance with AI Act requirements and risk assessments.

---

#### **NIST Framework Adherence**
Follow NIST AI Risk Management Framework guidelines for responsible AI development, including governance structures, risk assessment, and continuous monitoring.

**Safety**: Do not develop AI systems without implementing NIST-recommended risk management practices and governance structures.

---

#### **Clear AI Attribution and Labeling**
Label all AI-generated content, code, and outputs clearly. Maintain records of AI tool usage, generated content, and human modifications.

**Safety**: Do not deploy AI-generated content without clear attribution and user awareness of AI involvement.

---

#### **Maintain Comprehensive Audit Trails**
Document all development decisions, AI tool usage, code modifications, and review processes. Include version control with clear commit messages for AI-assisted changes.

**Safety**: Do not make changes without maintaining comprehensive audit trails that enable accountability and rollback capabilities.

---

### 6. 🏗️ **Dependency & Architecture Rules**

#### **Eliminate Duplicate Implementations**
Identify and consolidate duplicate code, conflicting implementations, and redundant dependencies. Choose the best implementation and refactor others to use it.

**Safety**: Do not introduce new implementations without first identifying and addressing existing duplicate or conflicting code.

---

#### **Proper Dependency Management**
Use dependency scanning tools to identify vulnerabilities, outdated packages, and license conflicts. Maintain up-to-date dependencies with security patches.

**Safety**: Do not add dependencies without security scanning and vulnerability assessment of the entire dependency chain.

---

#### **Architecture Consistency Requirements**
Follow established architectural patterns and design principles. Ensure new features integrate coherently with existing system design.

**Safety**: Do not implement features that violate established architectural principles or create inconsistent system design.

---

#### **Package Documentation Verification**
Use context7 and official documentation to verify correct usage of libraries and frameworks. Follow established patterns and best practices.

**Safety**: Do not implement features using unofficial documentation or unverified implementation patterns.

---

### 7. 🤖 **AI-Specific Development Rules**

#### **Responsible AI Code Generation**
Use AI coding tools as assistants, not replacements for human judgment. Always review, understand, and validate AI-generated code before integration.

**Safety**: Do not integrate AI-generated code without thorough understanding and validation of its functionality and implications.

---

#### **Context-Aware AI Usage**
Provide AI tools with complete context about existing codebase, requirements, and constraints. Use specific, detailed prompts that include technical specifications.

**Safety**: Do not use AI tools without providing complete context about existing systems and integration requirements.

---

#### **AI Output Validation and Testing**
Implement specific validation for AI-generated outputs including logic verification, security scanning, and integration testing. Test for AI-specific failure modes.

**Safety**: Do not trust AI-generated code without comprehensive validation and testing for correctness and security.

---

#### **Governance and Approval Processes**
Follow established approval processes for AI tool usage, especially for high-risk or production systems. Include security review and compliance verification.

**Safety**: Do not use AI tools for critical systems without proper governance, approval, and oversight processes.

---

## 🚨 **Critical Safety Reminders**

### **Non-Negotiable Requirements**
- **Planning First**: Always plan before implementing
- **Security by Design**: Integrate security throughout development lifecycle  
- **Human Oversight**: Maintain human control and accountability
- **Complete Testing**: Comprehensive validation before deployment
- **Documentation**: Full audit trails and compliance documentation
- **Risk Assessment**: Evaluate and mitigate all identified risks

### **Red Flags - Stop and Escalate**
- Unvetted AI-generated code in production systems
- Missing or incomplete security reviews
- Lack of rollback or override capabilities
- Insufficient testing coverage
- Missing compliance documentation
- Unknown or unmanaged dependencies

---

## 📈 **Enforcement and Monitoring**

### **Mandatory Reviews**
- Architecture Review (for system changes)
- Security Review (for all AI features)
- Compliance Review (for regulated environments)
- Code Review (for all implementations)

### **Automated Enforcement**
- Pre-commit hooks for security scanning
- CI/CD pipelines with comprehensive testing
- Dependency vulnerability scanning
- Code quality and coverage monitoring

### **Continuous Improvement**
- Regular rule updates based on new threats and regulations
- Lessons learned integration from incidents and near-misses
- Industry best practice adoption and compliance monitoring

---

## 📞 **Resources and Support**

### **Documentation**
- NIST AI Risk Management Framework: [nist.gov/itl/ai-risk-management-framework](https://nist.gov/itl/ai-risk-management-framework)
- EU AI Act Implementation: [artificialintelligenceact.eu](https://artificialintelligenceact.eu)
- NIST SP 800-218A: Secure Software Development for AI

### **Tools and Services**
- Context7 MCP Server for package documentation
- Dependency scanning and vulnerability assessment tools
- AI code review and validation platforms
- Compliance monitoring and audit trail systems

### **Training and Certification**
- AI Safety and Security Training
- Secure Development Lifecycle (SDL) for AI
- Regulatory Compliance Training (EU AI Act, NIST)

---

**🔄 This document is a living guide. Rules will be updated as AI technology, regulations, and industry best practices evolve.**

**⚠️ Violation of these rules may result in security vulnerabilities, regulatory non-compliance, and significant business risks.**

**✅ Following these rules ensures safe, secure, and responsible AI development that protects users and organizations.**