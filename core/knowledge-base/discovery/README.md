# Phase 0 Discovery Framework

A comprehensive business discovery framework that transforms initial ideas into production-ready documentation, providing complete context for Phase 1 (Architecture, UX, Security) teams.

## Framework Overview

**Purpose**: Ensure complete business context gathering before technical implementation begins

**Philosophy**: "Better discovery prevents later rework" - Invest time upfront to save time and cost downstream

**Quality Gate**: No gaps should exist that require returning to discovery during execution phases

## Framework Components

### 📋 Core Files

1. **[discovery-prompt.md](discovery-prompt.md)** - AI context and expertise for business discovery
2. **[discovery-checklist.md](discovery-checklist.md)** - Comprehensive Phase 0 tasks with interactive Q&A option
3. **[discovery-template.md](discovery-template.md)** - Production-ready templates for all outputs
4. **[README.md](README.md)** - This overview and usage guide

### 🎯 Deliverable Framework

#### Minimum Required Outputs (Must Have)
1. **Project Brief** - Executive summary with complete business context
2. **Product Requirements Document (PRD)** - Detailed functional and non-functional requirements

#### Additional Outputs (Recommended)
3. **Market Analysis** - Competition, opportunity, and positioning assessment
4. **Success Metrics** - KPIs, OKRs, and comprehensive measurement plan
5. **Risk Assessment** - Business, technical, and market risks with mitigation strategies
6. **Resource Plan** - Budget, timeline, and team requirements with contingencies

## Input Methods Supported

### 📁 Method 1: Document Import
**Best for**: Existing businesses with documentation
- Import existing business documents, research papers, strategy docs
- Extract and validate business context from materials
- Identify gaps requiring additional discovery
- Transform imported content into standardized outputs

**Supported Formats**: 
- Business strategy documents
- Market research reports
- Technical specifications
- Stakeholder interview notes
- Competitive analysis reports

### 📋 Method 2: Upload/Paste Content
**Best for**: Teams using collaboration tools
- Process content from Notion, Confluence, Google Docs, etc.
- Extract structured information from unstructured content
- Validate completeness against discovery checklist
- Request clarification for missing elements

**Supported Sources**:
- Notion pages and databases
- Confluence spaces
- Google Docs and Sheets
- Slack conversations
- Email threads and meeting notes

### 💬 Method 3: Interactive Discovery
**Best for**: New projects or when no documentation exists
- Guided discovery sessions using structured Q&A
- Advanced elicitation techniques for deeper insights
- Iterative refinement until all elements are complete
- Real-time validation and gap identification

**Process**:
1. Respond with "START INTERACTIVE" in discovery-checklist.md
2. Follow guided questioning for each section
3. Use advanced elicitation for deeper insights
4. Iterate until all critical items completed

## Usage Workflows

### 🚀 Quick Start (2-4 hours)
**For**: Small projects, prototypes, or urgent initiatives

1. **Choose Input Method**: Document import, upload, or interactive
2. **Complete Minimum Outputs**:
   - Project Brief (1-2 hours)
   - PRD (2-3 hours)
3. **Quality Check**: Stakeholder review and approval
4. **Phase 1 Handoff**: Provide outputs to Architecture, UX, Security teams

### 🏗️ Comprehensive Discovery (1-2 weeks)
**For**: Strategic initiatives, complex projects, high-risk ventures

1. **Discovery Planning** (1 day):
   - Stakeholder identification and scheduling
   - Information gathering and document collection
   - Discovery approach selection

2. **Information Gathering** (2-3 days):
   - Stakeholder interviews and workshops
   - Market research and competitive analysis
   - Technical feasibility assessment
   - Risk identification sessions

3. **Analysis and Documentation** (3-5 days):
   - Complete all 6 discovery outputs
   - Validate with stakeholders
   - Refine based on feedback
   - Final quality assurance

4. **Stakeholder Review** (1-2 days):
   - Present findings and recommendations
   - Address concerns and questions
   - Obtain formal approvals
   - Plan Phase 1 transition

### 🔄 Iterative Discovery (Ongoing)
**For**: Evolving projects, agile environments, uncertain requirements

1. **Initial Discovery**: Complete minimum outputs quickly
2. **Incremental Enhancement**: Add detail over time as new information emerges
3. **Regular Updates**: Maintain discovery documents as project evolves
4. **Continuous Validation**: Regular stakeholder check-ins and updates

## Quality Standards

### ✅ Completeness Criteria
- All chosen template sections fully completed
- No "TBD" or placeholder content in final outputs
- Every requirement traceable to business value
- All assumptions documented and validated where possible

### 🎯 Clarity Standards
- Technical and business stakeholders can understand all content
- Requirements are unambiguous and testable
- Success metrics are specific, measurable, and time-bound
- Risk assessments include clear impact and probability ratings

### 🔗 Strategic Alignment
- All outputs align with stated business objectives
- Requirements prioritization reflects business value
- Resource allocation aligns with strategic priorities
- Success metrics connect to business outcomes

## Integration with BMAD Workflow

### 📈 Relationship to BMAD-METHOD
This discovery framework serves as **Phase 0** in the BMAD workflow:
- **Before BMAD**: Complete comprehensive business discovery
- **BMAD Planning**: Use discovery outputs as authoritative input
- **BMAD Execution**: Reference discovery for context and validation

### 🔄 Phase Transitions

#### To Phase 1 Architecture
**Handoff Package**:
- Complete technical requirements from PRD
- Performance and scalability requirements
- Integration constraints and dependencies
- Success criteria for technical implementation

#### To Phase 1 UX Research
**Handoff Package**:
- User personas and journey maps from Project Brief
- UI/UX goals from PRD
- Accessibility and usability requirements
- User success metrics and validation criteria

#### To Phase 1 Security
**Handoff Package**:
- Compliance requirements from Risk Assessment
- Data sensitivity and protection requirements
- Security success metrics and validation approach
- Regulatory constraints and audit requirements

## Template Selection Guide

### 📊 Project Complexity Assessment

**Low Complexity** (Minimum outputs only):
- Simple feature additions
- Well-understood problem domains
- Limited stakeholder groups
- Low technical risk
- Small team and budget

**Medium Complexity** (Add Market Analysis + Success Metrics):
- New product features
- Competitive markets
- Multiple stakeholder groups
- Moderate technical complexity
- Medium team and budget

**High Complexity** (All 6 outputs):
- New product launches
- Strategic initiatives
- Complex stakeholder environments
- High technical or business risk
- Large team and significant budget

### 🏭 Industry Adaptations

#### AI/ML Products
**Additional Considerations**:
- Data requirements and availability
- Model performance and accuracy requirements
- Ethical AI and bias mitigation
- Explainability and interpretability needs

#### SaaS Applications
**Additional Considerations**:
- Multi-tenancy and scalability requirements
- Subscription and billing model complexity
- Integration ecosystem requirements
- Customer onboarding and success metrics

#### Mobile Applications
**Additional Considerations**:
- Platform-specific requirements (iOS/Android)
- App store guidelines and approval process
- Device capabilities and constraints
- Offline functionality requirements

#### Enterprise Systems
**Additional Considerations**:
- Enterprise integration requirements
- Security and compliance frameworks
- Change management and training needs
- Legacy system migration requirements

## Success Metrics

### 📈 Discovery Phase Success
- **Completeness**: 100% of chosen template sections completed
- **Quality**: Zero critical gaps identified in Phase 1
- **Stakeholder Satisfaction**: >90% approval rating
- **Timeline Adherence**: Discovery completed within planned timeframe

### 🎯 Downstream Impact
- **Phase 1 Efficiency**: Minimal rework due to missing requirements
- **Implementation Speed**: Faster development due to clear requirements
- **Quality Outcomes**: Higher product quality due to comprehensive planning
- **Stakeholder Alignment**: Reduced scope changes during execution

## Best Practices

### 🎨 Discovery Facilitation
- **Start with Why**: Always begin with business objectives and user value
- **Think in Systems**: Consider how the solution fits into broader business processes
- **Validate Early**: Test assumptions with stakeholders before finalizing
- **Document Decisions**: Record the rationale behind key decisions

### 🔍 Requirements Engineering
- **User-Centric**: Frame requirements in terms of user value
- **Testable**: Every requirement should have clear acceptance criteria
- **Prioritized**: Not everything can be equally important
- **Traced**: Connect requirements to business objectives

### ⚡ Risk Management
- **Think Pessimistically**: What could go wrong?
- **Quantify Impact**: Use data to assess risk severity
- **Plan Mitigation**: Every risk needs a response strategy
- **Monitor Continuously**: Risks change as projects evolve

### 📊 Success Measurement
- **Leading Indicators**: Metrics that predict success
- **Lagging Indicators**: Metrics that confirm success
- **Actionable Metrics**: Metrics that drive specific actions
- **Balanced Scorecard**: Business, user, technical, and operational metrics

## Troubleshooting

### 🚨 Common Issues

**"Stakeholders can't agree on requirements"**
- Use facilitated workshops with structured decision-making
- Create requirement prioritization matrices
- Document areas of disagreement and escalation paths
- Consider phased approach with MVP focus

**"Requirements keep changing"**
- Implement formal change control process
- Focus on core requirements first
- Use timeboxing for requirements gathering
- Regular stakeholder communication and expectation setting

**"Too much complexity to document"**
- Start with minimum outputs and iterate
- Use progressive disclosure (high-level first, then details)
- Focus on decisions that can't be changed later
- Consider breaking into smaller, more manageable projects

**"Technical team says requirements aren't implementable"**
- Include technical stakeholders in discovery process
- Conduct technical feasibility spikes during discovery
- Document technical constraints and trade-offs
- Plan architecture review as part of Phase 1

### 💡 Quick Fixes

**Accelerate Discovery**:
- Use existing documentation as starting point
- Focus on minimum outputs first
- Parallel workstreams where possible
- Time-box discovery activities

**Improve Quality**:
- Peer review all outputs
- Stakeholder validation at each stage
- Use templates and checklists consistently
- Learn from previous project retrospectives

**Enhance Stakeholder Engagement**:
- Clear communication about discovery value
- Regular updates and progress sharing
- Interactive workshops vs. document reviews
- Celebrate discovery milestones

## Getting Started

### 🏁 Immediate Next Steps

1. **Assess Your Project**:
   - Determine complexity level (low/medium/high)
   - Identify available input materials
   - Choose appropriate input method

2. **Plan Your Discovery**:
   - Schedule stakeholder time
   - Gather available documentation
   - Set discovery timeline and milestones

3. **Begin Discovery**:
   - Start with discovery-checklist.md for systematic approach
   - OR use discovery-prompt.md for AI-assisted guidance
   - Use discovery-template.md for structured outputs

4. **Execute and Iterate**:
   - Work through chosen sections systematically
   - Validate with stakeholders regularly
   - Refine based on feedback
   - Obtain formal approvals before Phase 1

### 🎯 Success Indicators

You'll know discovery is complete when:
- [ ] All stakeholders agree on problem and solution approach
- [ ] Requirements are clear, complete, and prioritized
- [ ] Success metrics are defined and measurable
- [ ] Risks are identified with mitigation strategies
- [ ] Resource requirements are understood and approved
- [ ] Phase 1 teams have clear handoff packages

---

## Support and Feedback

**Framework Evolution**: This discovery framework improves based on usage and feedback. Please document lessons learned and suggest improvements.

**Integration**: Adapt templates and processes to fit your organization's tools, standards, and culture.

**Quality**: Remember that discovery quality directly impacts all downstream phases. Invest the time upfront to prevent costly rework later.

**Success**: The ultimate measure of discovery success is whether Phase 1 teams can work efficiently without gaps or unclear requirements.

---

*"Perfect discovery is impossible, but comprehensive discovery is achievable. Better discovery prevents later rework, reduces project risk, and increases the probability of successful outcomes."*