# Phase 0 Discovery Templates

This file contains comprehensive templates for all Phase 0 Discovery outputs. Each template is designed to be production-ready and provides complete context for Phase 1 (Architecture, UX, Security).

---

## Template 1: Project Brief

### Template Overview
- **Purpose**: Executive summary providing complete business context
- **Audience**: Executive sponsors, project stakeholders, Phase 1 teams
- **Completion Time**: 2-4 hours for comprehensive version
- **Dependencies**: Business objectives, problem statement, initial requirements

### Project Brief Template

```markdown
# Project Brief: {{PROJECT_NAME}}

**Document Version**: 1.0  
**Date**: {{DATE}}  
**Author**: {{AUTHOR}}  
**Status**: {{DRAFT|REVIEW|APPROVED}}

## Executive Summary

**Project Vision**: {{One sentence project vision}}

**Business Problem**: {{2-3 sentence problem statement}}

**Proposed Solution**: {{2-3 sentence solution approach}}

**Success Metrics**: {{Primary success metrics}}

**Investment Required**: {{Budget range}} over {{timeline}}

**Expected ROI**: {{Return on investment summary}}

## Problem Statement

### Current State Analysis
{{Detailed description of current situation, pain points, and inefficiencies}}

### Impact Quantification
- **Cost of Current Problems**: {{Quantified costs (time, money, opportunity)}}
- **Affected Stakeholders**: {{Who is impacted and how}}
- **Business Impact**: {{Revenue, efficiency, competitive implications}}
- **Urgency Factors**: {{Why this needs to be solved now}}

### Root Cause Analysis
{{Analysis of why current solutions are inadequate}}

## Proposed Solution

### Solution Approach
{{High-level description of proposed solution}}

### Key Differentiators
- {{Differentiator 1: Why this approach is better}}
- {{Differentiator 2: Competitive advantages}}
- {{Differentiator 3: Unique value proposition}}

### Success Criteria
{{Clear, measurable criteria for solution success}}

## Target Users & Stakeholders

### Primary User Segment: {{SEGMENT_NAME}}
- **Profile**: {{Demographics/firmographics}}
- **Current Workflow**: {{How they work today}}
- **Pain Points**: {{Specific problems they face}}
- **Goals**: {{What they want to achieve}}
- **Success Metrics**: {{How they'll measure success}}

### Secondary User Segment: {{SEGMENT_NAME}} *(if applicable)*
- **Profile**: {{Demographics/firmographics}}
- **Relationship to Primary**: {{How they interact}}
- **Specific Needs**: {{Unique requirements}}

### Key Stakeholders
| Stakeholder Group | Interest Level | Influence Level | Success Criteria |
|-------------------|----------------|------------------|------------------|
| {{Group 1}} | {{High/Med/Low}} | {{High/Med/Low}} | {{Their definition of success}} |
| {{Group 2}} | {{High/Med/Low}} | {{High/Med/Low}} | {{Their definition of success}} |

## Business Objectives & Success Metrics

### Primary Business Objectives
1. **{{Objective 1}}**: {{Description and rationale}}
   - **Metric**: {{How to measure}}
   - **Target**: {{Specific target value}}
   - **Timeline**: {{When to achieve}}

2. **{{Objective 2}}**: {{Description and rationale}}
   - **Metric**: {{How to measure}}
   - **Target**: {{Specific target value}}
   - **Timeline**: {{When to achieve}}

### Key Performance Indicators (KPIs)
| KPI | Definition | Target | Measurement Method | Owner |
|-----|------------|--------|--------------------|-------|
| {{KPI 1}} | {{Clear definition}} | {{Specific target}} | {{How measured}} | {{Responsible person}} |
| {{KPI 2}} | {{Clear definition}} | {{Specific target}} | {{How measured}} | {{Responsible person}} |

## Scope Definition

### MVP Scope (Phase 1)
**MVP Goal**: {{What the MVP will achieve}}

#### Core Features (Must Have)
- **{{Feature 1}}**: {{Description and business justification}}
- **{{Feature 2}}**: {{Description and business justification}}
- **{{Feature 3}}**: {{Description and business justification}}

#### MVP Success Criteria
{{Specific, measurable criteria for MVP success}}

### Out of Scope for MVP
- {{Feature or capability not included in MVP}}
- {{Feature or capability not included in MVP}}
- {{Feature or capability not included in MVP}}

### Post-MVP Vision

#### Phase 2 Priorities
{{Features and capabilities for next phase}}

#### Long-term Vision (1-2 years)
{{Strategic vision for product evolution}}

## Technical Considerations

### Platform Requirements
- **Target Platforms**: {{Web, mobile, desktop, etc.}}
- **Browser/OS Support**: {{Specific requirements}}
- **Performance Requirements**: {{Response times, throughput, etc.}}
- **Scalability Requirements**: {{User load, data volume expectations}}

### Technology Constraints
- **Existing Systems**: {{Integration requirements}}
- **Technology Stack**: {{Preferred or required technologies}}
- **Infrastructure**: {{Hosting, cloud, on-premise requirements}}
- **Compliance**: {{Security, regulatory requirements}}

### Architecture Principles
{{High-level architectural guidance for Phase 1 Architecture team}}

## Resource Requirements

### Budget Estimation
| Category | Estimated Cost | Justification |
|----------|----------------|---------------|
| Development Team | {{Cost range}} | {{Team size and duration}} |
| Technology/Infrastructure | {{Cost range}} | {{Tools, services, hosting}} |
| Third-party Services | {{Cost range}} | {{APIs, licenses, vendors}} |
| **Total Project Cost** | **{{Total range}}** | **{{Overall justification}}** |

### Timeline Estimation
| Phase | Duration | Key Milestones |
|-------|----------|----------------|
| Discovery (Phase 0) | {{Duration}} | {{Key deliverables}} |
| Architecture & Design (Phase 1) | {{Duration}} | {{Key deliverables}} |
| Development & Testing | {{Duration}} | {{Key deliverables}} |
| Deployment & Launch | {{Duration}} | {{Key deliverables}} |
| **Total Project Duration** | **{{Total duration}}** | **{{Launch date}}** |

### Team Requirements
- **Core Team Size**: {{Number of people}}
- **Key Roles Needed**: {{List of roles and skills}}
- **External Resources**: {{Contractors, consultants, vendors}}
- **Stakeholder Commitment**: {{Time requirements from business}}

## Risk Assessment

### High-Priority Risks
| Risk | Probability | Impact | Mitigation Strategy | Owner |
|------|-------------|--------|-------------------|-------|
| {{Risk 1}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} | {{Responsible person}} |
| {{Risk 2}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} | {{Responsible person}} |

### Assumptions
- {{Key assumption 1 and validation approach}}
- {{Key assumption 2 and validation approach}}
- {{Key assumption 3 and validation approach}}

### Dependencies
- {{External dependency 1 and contingency plan}}
- {{External dependency 2 and contingency plan}}

## Next Steps

### Immediate Actions (Next 2 Weeks)
1. {{Action item with owner and deadline}}
2. {{Action item with owner and deadline}}
3. {{Action item with owner and deadline}}

### Phase 1 Readiness Criteria
- [ ] Stakeholder approval of project brief
- [ ] Budget approval and resource allocation
- [ ] Product Requirements Document (PRD) completed
- [ ] Phase 1 team identified and available

### Handoff to Product Manager
**Instructions**: Use this Project Brief as input to create a comprehensive Product Requirements Document (PRD). Focus on translating the business objectives into detailed functional and non-functional requirements, user stories, and acceptance criteria.

---

## Appendices

### A. Market Research Summary
{{Summary of competitive analysis, market sizing, customer research}}

### B. Stakeholder Interview Summary
{{Key insights from stakeholder conversations}}

### C. Technical Feasibility Analysis
{{Initial technical validation and constraints}}

### D. References
- {{Relevant documents, links, research sources}}
```

---

## Template 2: Product Requirements Document (PRD)

### Template Overview
- **Purpose**: Detailed product requirements for development teams
- **Audience**: Architects, developers, designers, QA teams
- **Completion Time**: 4-8 hours for comprehensive version
- **Dependencies**: Completed Project Brief, stakeholder input, technical constraints

### PRD Template

```markdown
# {{PROJECT_NAME}} Product Requirements Document (PRD)

**Document Version**: 1.0  
**Date**: {{DATE}}  
**Author**: {{AUTHOR}}  
**Status**: {{DRAFT|REVIEW|APPROVED}}

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| {{Date}} | 1.0 | Initial version | {{Author}} |

## Goals and Background Context

### Goals
- {{Goal 1: Business outcome the PRD will deliver}}
- {{Goal 2: User value to be created}}
- {{Goal 3: Technical capability to be built}}
- {{Goal 4: Success metric to be achieved}}

### Background Context
{{1-2 paragraphs summarizing the business context, problem being solved, and why this solution approach was chosen. Reference the Project Brief for detailed context.}}

## Requirements

### Functional Requirements

1. **FR1: {{Requirement Title}}**
   {{Detailed description of functional requirement with acceptance criteria}}

2. **FR2: {{Requirement Title}}**
   {{Detailed description of functional requirement with acceptance criteria}}

3. **FR3: {{Requirement Title}}**
   {{Detailed description of functional requirement with acceptance criteria}}

*Continue numbering for all functional requirements...*

### Non-Functional Requirements

1. **NFR1: {{Requirement Category}} - {{Requirement Title}}**
   {{Detailed description with measurable criteria}}
   - **Target**: {{Specific measurable target}}
   - **Measurement Method**: {{How to verify compliance}}

2. **NFR2: {{Requirement Category}} - {{Requirement Title}}**
   {{Detailed description with measurable criteria}}
   - **Target**: {{Specific measurable target}}
   - **Measurement Method**: {{How to verify compliance}}

*Continue numbering for all non-functional requirements...*

#### Common Non-Functional Requirement Categories:
- **Performance**: Response times, throughput, latency
- **Scalability**: User load, data volume, concurrent users
- **Security**: Authentication, authorization, data protection
- **Availability**: Uptime, disaster recovery, maintenance windows
- **Usability**: User experience standards, accessibility
- **Compatibility**: Browser support, device compatibility
- **Compliance**: Regulatory requirements, industry standards

## User Interface Design Goals

### Overall UX Vision
{{Description of the desired user experience, interaction paradigms, and design principles that will guide the UI/UX design process}}

### Key Interaction Paradigms
- {{Interaction pattern 1: e.g., "Progressive disclosure for complex workflows"}}
- {{Interaction pattern 2: e.g., "Real-time collaboration and feedback"}}
- {{Interaction pattern 3: e.g., "Mobile-first responsive design"}}

### Core Screens and Views
*(Conceptual high-level screens needed to deliver PRD value)*

1. **{{Screen Name}}**: {{Purpose and key functionality}}
2. **{{Screen Name}}**: {{Purpose and key functionality}}
3. **{{Screen Name}}**: {{Purpose and key functionality}}
4. **{{Screen Name}}**: {{Purpose and key functionality}}

### Accessibility Requirements
**Level**: {{None | WCAG 2.1 AA | WCAG 2.1 AAA | Custom Requirements}}

{{If custom, specify detailed accessibility requirements}}

### Branding and Visual Design
{{Any specific branding requirements, style guide references, or visual design principles}}

### Target Device and Platforms
**Primary**: {{Web Responsive | Mobile iOS | Mobile Android | Desktop | etc.}}
**Secondary**: {{Additional platforms if applicable}}

{{Specific requirements for each platform}}

## Technical Assumptions

### Repository Structure
**Approach**: {{Monorepo | Polyrepo | Multi-repo}}

**Rationale**: {{Why this approach fits the project requirements}}

### Service Architecture
**Approach**: {{Monolith | Microservices | Serverless | Hybrid}}

**Rationale**: {{Why this architecture supports the business and technical requirements}}

**Service Breakdown** *(if applicable)*:
- {{Service 1}}: {{Responsibilities}}
- {{Service 2}}: {{Responsibilities}}

### Testing Requirements
**Approach**: {{Unit Only | Unit + Integration | Full Testing Pyramid | Custom}}

**Testing Strategy**:
- **Unit Tests**: {{Coverage and approach}}
- **Integration Tests**: {{Scope and approach}}
- **End-to-End Tests**: {{Critical user journeys to test}}
- **Performance Tests**: {{Load and stress testing requirements}}
- **Security Tests**: {{Security validation approach}}

### Technology Stack Assumptions
*(These become constraints for the Architecture team)*

#### Frontend Technology
- **Framework**: {{React | Vue | Angular | etc.}} - {{Rationale}}
- **State Management**: {{Redux | Zustand | Context | etc.}} - {{Rationale}}
- **Styling**: {{CSS-in-JS | Tailwind | SCSS | etc.}} - {{Rationale}}

#### Backend Technology
- **Language**: {{JavaScript/Node.js | Python | Java | etc.}} - {{Rationale}}
- **Framework**: {{Express | FastAPI | Spring | etc.}} - {{Rationale}}
- **Database**: {{PostgreSQL | MongoDB | MySQL | etc.}} - {{Rationale}}

#### Infrastructure and Deployment
- **Cloud Provider**: {{AWS | Azure | GCP | etc.}} - {{Rationale}}
- **Containerization**: {{Docker | None}} - {{Rationale}}
- **CI/CD**: {{GitHub Actions | Jenkins | etc.}} - {{Rationale}}

### Additional Technical Assumptions
{{Any other technical decisions, constraints, or preferences that will guide the Architect}}

## Epic List

*High-level epics that deliver significant, end-to-end functionality. Each epic should be logically sequential and build upon previous epics.*

### Epic 1: {{Epic Title}}
**Goal**: {{1-2 sentence description of epic objective and value}}

### Epic 2: {{Epic Title}}
**Goal**: {{1-2 sentence description of epic objective and value}}

### Epic 3: {{Epic Title}}
**Goal**: {{1-2 sentence description of epic objective and value}}

*Continue for all epics...*

## Epic Details

### Epic 1: {{Epic Title}}

**Epic Goal**: {{2-3 sentences describing the objective and value all stories in this epic will achieve}}

#### Story 1.1: {{Story Title}}
**User Story**: 
As a {{user type}},
I want {{action/capability}},
so that {{benefit/value}}.

**Acceptance Criteria**:
1. {{Specific, testable criterion}}
2. {{Specific, testable criterion}}
3. {{Specific, testable criterion}}

**Definition of Done**:
- [ ] All acceptance criteria met
- [ ] Code reviewed and approved
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Deployed to staging environment
- [ ] User acceptance testing completed

#### Story 1.2: {{Story Title}}
**User Story**: 
As a {{user type}},
I want {{action/capability}},
so that {{benefit/value}}.

**Acceptance Criteria**:
1. {{Specific, testable criterion}}
2. {{Specific, testable criterion}}
3. {{Specific, testable criterion}}

*Continue for all stories in Epic 1...*

### Epic 2: {{Epic Title}}

**Epic Goal**: {{2-3 sentences describing the objective and value}}

*Repeat story format for all stories in Epic 2...*

*Continue for all epics...*

## Quality Gates and Validation

### Definition of Ready (for Development)
- [ ] All functional requirements clearly defined
- [ ] All non-functional requirements have measurable targets
- [ ] User stories have clear acceptance criteria
- [ ] Technical assumptions validated by Architecture team
- [ ] Dependencies and integration points identified
- [ ] Success metrics and measurement approach defined

### Definition of Done (for PRD)
- [ ] All sections completed with no TBD items
- [ ] Requirements traceability to business objectives verified
- [ ] Stakeholder review and approval obtained
- [ ] Architecture team review and technical validation
- [ ] UX team review and user experience validation
- [ ] Delivery estimates and resource planning completed

## Next Steps

### UX Research and Design Phase
**Handoff Package**: This PRD provides the complete product context for UX research and design. Please use the User Interface Design Goals section and user stories to:
- Create detailed user journey maps
- Design wireframes and user interface mockups
- Validate design concepts with target users
- Create design system and component library

### Architecture Phase
**Handoff Package**: This PRD provides the complete technical requirements for architecture design. Please use the Technical Assumptions and Requirements sections to:
- Design system architecture and component structure
- Define API specifications and data models
- Create deployment and infrastructure architecture
- Validate technical feasibility and provide implementation estimates

### Security Review Phase
**Handoff Package**: This PRD provides security and compliance requirements. Please use the Non-Functional Requirements and Technical Assumptions to:
- Conduct security architecture review
- Define authentication and authorization approach
- Create security testing and validation plan
- Ensure compliance with regulatory requirements

---

## Appendices

### A. Requirements Traceability Matrix
| Requirement ID | Business Objective | User Story | Epic | Priority |
|----------------|-------------------|------------|------|----------|
| FR1 | {{Objective}} | {{Story}} | {{Epic}} | {{High/Med/Low}} |
| FR2 | {{Objective}} | {{Story}} | {{Epic}} | {{High/Med/Low}} |

### B. User Research Summary
{{Summary of user interviews, surveys, usability testing that informed requirements}}

### C. Technical Research and Validation
{{Summary of technical spikes, proof-of-concepts, feasibility analysis}}

### D. Competitive Feature Analysis
{{Analysis of how competitors solve similar problems, feature gaps and opportunities}}
```

---

## Template 3: Market Analysis

### Template Overview
- **Purpose**: Comprehensive market intelligence and competitive positioning
- **Audience**: Business stakeholders, product strategy, marketing teams
- **Completion Time**: 6-12 hours for thorough analysis
- **Dependencies**: Market research, competitive intelligence, customer data

### Market Analysis Template

```markdown
# Market Analysis Report: {{PROJECT_NAME}}

**Document Version**: 1.0  
**Date**: {{DATE}}  
**Author**: {{AUTHOR}}  
**Status**: {{DRAFT|REVIEW|APPROVED}}

## Executive Summary

**Market Opportunity**: {{High-level market size and opportunity}}

**Competitive Position**: {{Our positioning relative to competitors}}

**Key Recommendations**: {{Top 3 strategic recommendations}}

**Investment Justification**: {{Why the market opportunity justifies investment}}

## Research Objectives & Methodology

### Research Objectives
- {{Objective 1: What market decisions this research will inform}}
- {{Objective 2: Specific questions to be answered}}
- {{Objective 3: Success criteria for market entry}}

### Research Methodology
- **Data Sources**: {{Primary sources, secondary research, industry reports}}
- **Analysis Frameworks**: {{TAM/SAM/SOM, Porter's Five Forces, PESTEL, etc.}}
- **Data Collection Timeframe**: {{Research period}}
- **Limitations**: {{Assumptions and data limitations}}

## Market Overview

### Market Definition
- **Product/Service Category**: {{Clear definition of market category}}
- **Geographic Scope**: {{Target geographic markets}}
- **Customer Segments**: {{Included customer types}}
- **Value Chain Position**: {{Where we fit in the value chain}}

### Market Size & Growth

#### Total Addressable Market (TAM)
**Size**: {{Market size in revenue/units}}
**Calculation Method**: {{Top-down, bottom-up, or value theory approach}}
**Key Assumptions**: {{Critical assumptions in calculation}}

#### Serviceable Addressable Market (SAM)
**Size**: {{Realistic addressable portion of TAM}}
**Constraints**: {{Geographic, regulatory, competitive constraints}}
**Justification**: {{Why this portion is serviceable}}

#### Serviceable Obtainable Market (SOM)
**Size**: {{Realistic market share we can capture}}
**Market Share Assumption**: {{Percentage and timeframe}}
**Competitive Factors**: {{Barriers and advantages affecting capture}}

### Market Trends & Drivers

#### Key Market Trends
1. **{{Trend 1}}**: {{Description and impact on market}}
   - **Impact**: {{How this affects market size and opportunity}}
   - **Timeframe**: {{When this trend will peak/mature}}
   - **Our Position**: {{How we can leverage this trend}}

2. **{{Trend 2}}**: {{Description and impact on market}}
   - **Impact**: {{How this affects market size and opportunity}}
   - **Timeframe**: {{When this trend will peak/mature}}
   - **Our Position**: {{How we can leverage this trend}}

#### Growth Drivers
- {{Driver 1: Factor accelerating market growth}}
- {{Driver 2: Factor accelerating market growth}}
- {{Driver 3: Factor accelerating market growth}}

#### Market Inhibitors
- {{Inhibitor 1: Factor constraining market growth}}
- {{Inhibitor 2: Factor constraining market growth}}
- {{Inhibitor 3: Factor constraining market growth}}

## Customer Analysis

### Primary Customer Segment: {{SEGMENT_NAME}}

#### Segment Profile
- **Size**: {{Number of potential customers}}
- **Demographics/Firmographics**: {{Key characteristics}}
- **Geographic Distribution**: {{Where they are located}}
- **Growth Rate**: {{How fast this segment is growing}}

#### Needs and Pain Points
- **Primary Need**: {{Most important need we address}}
- **Secondary Needs**: {{Additional needs we could address}}
- **Current Pain Points**: {{Problems with existing solutions}}
- **Unmet Needs**: {{Gaps in current market offerings}}

#### Buying Behavior
- **Decision Process**: {{How they evaluate and purchase solutions}}
- **Decision Criteria**: {{What factors drive their decisions}}
- **Budget Authority**: {{Who controls purchasing decisions}}
- **Purchase Cycle**: {{How long from evaluation to purchase}}

#### Customer Success Metrics
- {{How customers measure success with solutions like ours}}
- {{KPIs they track and report on}}
- {{ROI expectations and measurement methods}}

### Secondary Customer Segment: {{SEGMENT_NAME}} *(if applicable)*

*Repeat customer analysis format for secondary segments...*

## Competitive Landscape

### Direct Competitors

#### Competitor 1: {{COMPANY_NAME}}
- **Market Position**: {{Market share and positioning}}
- **Key Strengths**: {{What they do well}}
- **Key Weaknesses**: {{Where they fall short}}
- **Product Offering**: {{Description of their solution}}
- **Pricing Model**: {{How they price their solution}}
- **Target Customers**: {{Who they serve}}
- **Differentiation Strategy**: {{How they differentiate}}

#### Competitor 2: {{COMPANY_NAME}}
*Repeat analysis format for each direct competitor...*

### Indirect Competitors and Alternatives

#### Alternative Solution Categories
- **{{Category 1}}**: {{Description and competitive threat level}}
- **{{Category 2}}**: {{Description and competitive threat level}}
- **Status Quo**: {{Cost and risk of customers doing nothing}}

### Competitive Positioning Map

```
[Create a 2x2 matrix showing competitive positioning across two key dimensions]

          High {{Dimension 1}}
                 |
Low {{Dimension 2}}  |  High {{Dimension 2}}
                 |
          Low {{Dimension 1}}

{{Dimension 1}}: {{e.g., "Price Point"}}
{{Dimension 2}}: {{e.g., "Feature Richness"}}
```

### Our Competitive Advantages
1. **{{Advantage 1}}**: {{How we're better and why it matters}}
2. **{{Advantage 2}}**: {{How we're better and why it matters}}
3. **{{Advantage 3}}**: {{How we're better and why it matters}}

### Competitive Risks
1. **{{Risk 1}}**: {{Potential competitive threats and mitigation}}
2. **{{Risk 2}}**: {{Potential competitive threats and mitigation}}
3. **{{Risk 3}}**: {{Potential competitive threats and mitigation}}

## Market Entry Strategy

### Target Customer Priority
**Primary Target**: {{Most attractive customer segment to target first}}
**Rationale**: {{Why this segment offers the best entry opportunity}}
**Entry Strategy**: {{How to reach and convert this segment}}

### Value Proposition
**Core Value Proposition**: {{Clear statement of unique value we provide}}

**Value Pillars**:
1. **{{Pillar 1}}**: {{Specific value and proof points}}
2. **{{Pillar 2}}**: {{Specific value and proof points}}
3. **{{Pillar 3}}**: {{Specific value and proof points}}

### Go-to-Market Approach
- **Sales Model**: {{Direct, partner, self-service, hybrid}}
- **Marketing Channels**: {{How to reach target customers}}
- **Pricing Strategy**: {{Pricing model and rationale}}
- **Partnership Strategy**: {{Key partnerships for market entry}}

## Market Opportunity Assessment

### Opportunity Scoring
| Factor | Weight | Score (1-10) | Weighted Score |
|--------|--------|--------------|----------------|
| Market Size | {{%}} | {{Score}} | {{Calculation}} |
| Growth Rate | {{%}} | {{Score}} | {{Calculation}} |
| Competitive Intensity | {{%}} | {{Score}} | {{Calculation}} |
| Our Fit/Advantage | {{%}} | {{Score}} | {{Calculation}} |
| Resource Requirements | {{%}} | {{Score}} | {{Calculation}} |
| **Total Opportunity Score** | **100%** | **N/A** | **{{Total}}** |

### Investment Recommendation
**Recommendation**: {{Invest | Don't Invest | Conditional Investment}}

**Justification**: {{Why this is the right decision based on analysis}}

**Success Probability**: {{Estimated probability of achieving business objectives}}

**Key Success Factors**: {{What needs to go right for success}}

## Strategic Recommendations

### Immediate Actions (0-6 months)
1. {{Action 1: Specific recommendation with owner and timeline}}
2. {{Action 2: Specific recommendation with owner and timeline}}
3. {{Action 3: Specific recommendation with owner and timeline}}

### Medium-term Strategy (6-18 months)
1. {{Strategy 1: Market expansion or capability building}}
2. {{Strategy 2: Competitive positioning and differentiation}}
3. {{Strategy 3: Partnership and ecosystem development}}

### Long-term Vision (18+ months)
{{Strategic vision for market leadership and expansion}}

## Risk Assessment

### Market Risks
| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|--------------------|
| {{Market Risk 1}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} |
| {{Market Risk 2}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} |

### Competitive Risks
| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|--------------------|
| {{Competitive Risk 1}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} |
| {{Competitive Risk 2}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} |

## Appendices

### A. Market Research Data Sources
{{List of reports, surveys, interviews, and data sources used}}

### B. Competitive Intelligence Details
{{Detailed competitive analysis, feature comparisons, pricing research}}

### C. Customer Interview Summaries
{{Key insights from customer research and validation}}

### D. Market Sizing Calculations
{{Detailed TAM/SAM/SOM calculations with assumptions}}
```

---

## Template 4: Success Metrics Framework

### Template Overview
- **Purpose**: Comprehensive measurement and success tracking framework
- **Audience**: Project stakeholders, executives, operational teams
- **Completion Time**: 3-6 hours for complete framework
- **Dependencies**: Business objectives, user research, competitive analysis

### Success Metrics Template

```markdown
# Success Metrics Framework: {{PROJECT_NAME}}

**Document Version**: 1.0  
**Date**: {{DATE}}  
**Author**: {{AUTHOR}}  
**Status**: {{DRAFT|REVIEW|APPROVED}}

## Executive Summary

**Success Philosophy**: {{High-level approach to measuring success}}

**Primary Success Metric**: {{The one metric that best indicates project success}}

**Measurement Cadence**: {{How often we'll review and report on metrics}}

**Success Criteria**: {{Clear definition of what constitutes project success}}

## Measurement Framework Overview

### Success Metric Categories
1. **Business Impact Metrics**: {{Metrics that measure business value creation}}
2. **User Success Metrics**: {{Metrics that measure user value and satisfaction}}
3. **Product Performance Metrics**: {{Metrics that measure product functionality and adoption}}
4. **Operational Metrics**: {{Metrics that measure system performance and efficiency}}

### Measurement Principles
- **Actionable**: Every metric must drive specific actions when targets aren't met
- **Leading and Lagging**: Balance between predictive indicators and outcome measures
- **Baseline-driven**: All metrics have documented baseline measurements
- **Stakeholder-aligned**: Metrics matter to the people who need to act on them

## Key Performance Indicators (KPIs)

### Tier 1 KPIs (Executive Dashboard)
*These are the most critical metrics that executives and key stakeholders monitor*

#### KPI 1: {{KPI_NAME}}
- **Definition**: {{Clear, unambiguous definition}}
- **Rationale**: {{Why this is critical to project success}}
- **Target**: {{Specific target value and timeframe}}
- **Baseline**: {{Current state measurement}}
- **Measurement Method**: {{How data is collected and calculated}}
- **Reporting Frequency**: {{How often this is measured and reported}}
- **Owner**: {{Person responsible for this metric}}
- **Action Triggers**: {{What happens if metric is off-target}}

#### KPI 2: {{KPI_NAME}}
*Repeat format for all Tier 1 KPIs...*

### Tier 2 KPIs (Operational Dashboard)
*Important metrics that teams monitor for operational insights*

#### KPI 1: {{KPI_NAME}}
- **Definition**: {{Clear, unambiguous definition}}
- **Target**: {{Specific target value and timeframe}}
- **Measurement Method**: {{How data is collected}}
- **Owner**: {{Responsible person or team}}

*Continue for all Tier 2 KPIs...*

## Objectives and Key Results (OKRs)

### Quarter 1 Objectives ({{DATE_RANGE}})

#### Objective 1: {{OBJECTIVE_STATEMENT}}
**Rationale**: {{Why this objective is important now}}

**Key Results**:
1. {{Key Result 1}}: {{Specific, measurable outcome with target}}
   - **Measurement**: {{How to measure}}
   - **Owner**: {{Responsible person}}
   - **Target Date**: {{When to achieve}}

2. {{Key Result 2}}: {{Specific, measurable outcome with target}}
   - **Measurement**: {{How to measure}}
   - **Owner**: {{Responsible person}}
   - **Target Date**: {{When to achieve}}

3. {{Key Result 3}}: {{Specific, measurable outcome with target}}
   - **Measurement**: {{How to measure}}
   - **Owner**: {{Responsible person}}
   - **Target Date**: {{When to achieve}}

#### Objective 2: {{OBJECTIVE_STATEMENT}}
*Repeat format for all Q1 objectives...*

### Quarter 2 Objectives ({{DATE_RANGE}})
*Repeat OKR format for subsequent quarters...*

## Business Impact Metrics

### Revenue Metrics
| Metric | Definition | Target | Measurement Method | Owner | Reporting Frequency |
|--------|------------|--------|-------------------|-------|-----------------|
| {{Revenue Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |
| {{Revenue Metric 2}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |

### Cost and Efficiency Metrics
| Metric | Definition | Target | Measurement Method | Owner | Reporting Frequency |
|--------|------------|--------|-------------------|-------|-----------------|
| {{Cost Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |
| {{Cost Metric 2}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |

### Market and Competitive Metrics
| Metric | Definition | Target | Measurement Method | Owner | Reporting Frequency |
|--------|------------|--------|-------------------|-------|-----------------|
| {{Market Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |
| {{Market Metric 2}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |

## User Success Metrics

### User Adoption and Engagement
| Metric | Definition | Target | Measurement Method | Owner | Reporting Frequency |
|--------|------------|--------|-------------------|-------|-----------------|
| {{Adoption Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |
| {{Engagement Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |

### User Satisfaction and Value
| Metric | Definition | Target | Measurement Method | Owner | Reporting Frequency |
|--------|------------|--------|-------------------|-------|-----------------|
| {{Satisfaction Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |
| {{Value Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |

### User Journey and Experience
| Metric | Definition | Target | Measurement Method | Owner | Reporting Frequency |
|--------|------------|--------|-------------------|-------|-----------------|
| {{Journey Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |
| {{Experience Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |

## Product Performance Metrics

### Feature Usage and Adoption
| Feature | Usage Metric | Adoption Target | Measurement Method | Success Criteria |
|---------|-------------|----------------|-------------------|------------------|
| {{Feature 1}} | {{Metric}} | {{Target}} | {{Method}} | {{Success definition}} |
| {{Feature 2}} | {{Metric}} | {{Target}} | {{Method}} | {{Success definition}} |

### Product Quality and Reliability
| Metric | Definition | Target | Measurement Method | Owner | Action Threshold |
|--------|------------|--------|-------------------|-------|--------------|
| {{Quality Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{When to act}} |
| {{Reliability Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{When to act}} |

## Operational Metrics

### System Performance
| Metric | Definition | Target | SLA | Measurement Method | Alert Threshold |
|--------|------------|--------|----|-------------------|----------------|
| {{Performance Metric 1}} | {{Definition}} | {{Target}} | {{SLA}} | {{Method}} | {{Alert level}} |
| {{Performance Metric 2}} | {{Definition}} | {{Target}} | {{SLA}} | {{Method}} | {{Alert level}} |

### Support and Maintenance
| Metric | Definition | Target | Measurement Method | Owner | Reporting Frequency |
|--------|------------|--------|-------------------|-------|-----------------|
| {{Support Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |
| {{Maintenance Metric 1}} | {{Definition}} | {{Target}} | {{Method}} | {{Owner}} | {{Frequency}} |

## Baseline Measurements

### Current State Baselines
| Metric | Baseline Value | Measurement Date | Measurement Method | Notes |
|--------|----------------|------------------|-------------------|-------|
| {{Metric 1}} | {{Current value}} | {{Date}} | {{Method}} | {{Context}} |
| {{Metric 2}} | {{Current value}} | {{Date}} | {{Method}} | {{Context}} |

### Benchmark Comparisons
| Metric | Our Baseline | Industry Benchmark | Competitor Benchmark | Gap Analysis |
|--------|--------------|-------------------|-------------------|-------------|
| {{Metric 1}} | {{Our value}} | {{Industry avg}} | {{Competitor value}} | {{Gap and implications}} |
| {{Metric 2}} | {{Our value}} | {{Industry avg}} | {{Competitor value}} | {{Gap and implications}} |

## Measurement Implementation

### Data Collection Plan
| Metric | Data Source | Collection Method | Collection Frequency | Data Owner |
|--------|-------------|------------------|-------------------|------------|
| {{Metric 1}} | {{Source}} | {{Method}} | {{Frequency}} | {{Owner}} |
| {{Metric 2}} | {{Source}} | {{Method}} | {{Frequency}} | {{Owner}} |

### Analytics and Reporting Tools
- **Primary Analytics Platform**: {{Tool name and purpose}}
- **Business Intelligence Tool**: {{Tool for executive reporting}}
- **User Analytics Tool**: {{Tool for user behavior tracking}}
- **Performance Monitoring Tool**: {{Tool for system performance}}

### Dashboard and Reporting Structure

#### Executive Dashboard
- **Audience**: {{Who sees this dashboard}}
- **Frequency**: {{How often updated}}
- **Key Metrics**: {{Top 5-7 metrics displayed}}
- **Format**: {{Email, web dashboard, presentation, etc.}}

#### Operational Dashboard
- **Audience**: {{Who sees this dashboard}}
- **Frequency**: {{How often updated}}
- **Key Metrics**: {{Metrics for day-to-day operations}}
- **Format**: {{Real-time dashboard, daily reports, etc.}}

## Success Criteria and Milestones

### Short-term Success (0-6 months)
**Success Definition**: {{What constitutes success in first 6 months}}

**Key Milestones**:
- **Month 1**: {{Milestone and success criteria}}
- **Month 3**: {{Milestone and success criteria}}
- **Month 6**: {{Milestone and success criteria}}

### Medium-term Success (6-18 months)
**Success Definition**: {{What constitutes success at this stage}}

**Key Milestones**:
- **Month 9**: {{Milestone and success criteria}}
- **Month 12**: {{Milestone and success criteria}}
- **Month 18**: {{Milestone and success criteria}}

### Long-term Success (18+ months)
**Success Definition**: {{What constitutes long-term success}}

**Strategic Milestones**:
- **Year 2**: {{Major milestone and impact}}
- **Year 3**: {{Major milestone and impact}}

## Review and Optimization Process

### Metric Review Cadence
- **Daily**: {{Metrics reviewed daily and by whom}}
- **Weekly**: {{Metrics reviewed weekly and by whom}}
- **Monthly**: {{Metrics reviewed monthly and by whom}}
- **Quarterly**: {{Comprehensive review process}}

### Performance Analysis Process
1. **Data Collection**: {{How data is gathered and validated}}
2. **Trend Analysis**: {{How trends and patterns are identified}}
3. **Root Cause Analysis**: {{Process for investigating metric deviations}}
4. **Action Planning**: {{How corrective actions are determined and implemented}}
5. **Follow-up**: {{How action effectiveness is measured}}

### Metric Evolution and Optimization
- **Metric Retirement**: {{Process for retiring outdated metrics}}
- **New Metric Addition**: {{Process for adding new metrics}}
- **Target Adjustment**: {{Process for adjusting targets based on learning}}
- **Measurement Improvement**: {{Process for improving data accuracy and timeliness}}

## Risk and Contingency Planning

### Metric-Based Risk Indicators
| Risk Indicator | Threshold | Probability | Impact | Response Plan |
|----------------|-----------|-------------|--------|---------------|
| {{Risk Metric 1}} below {{threshold}} | {{When to worry}} | {{H/M/L}} | {{H/M/L}} | {{What to do}} |
| {{Risk Metric 2}} above {{threshold}} | {{When to worry}} | {{H/M/L}} | {{H/M/L}} | {{What to do}} |

### Contingency Actions
- **Scenario 1**: {{If metrics show X, then we will Y}}
- **Scenario 2**: {{If metrics show X, then we will Y}}
- **Scenario 3**: {{If metrics show X, then we will Y}}

## Appendices

### A. Metric Definitions Glossary
{{Detailed definitions of all metrics to ensure consistent understanding}}

### B. Calculation Methodologies
{{Detailed formulas and calculation methods for complex metrics}}

### C. Data Sources and Validation
{{Information about data sources, accuracy, and validation procedures}}

### D. Historical Performance Data
{{Baseline data and any available historical trends}}
```

---

## Template 5: Risk Assessment

### Template Overview
- **Purpose**: Comprehensive risk identification and mitigation planning
- **Audience**: Project stakeholders, executives, risk management teams
- **Completion Time**: 4-8 hours for thorough analysis
- **Dependencies**: Business objectives, technical requirements, market analysis

### Risk Assessment Template

```markdown
# Risk Assessment: {{PROJECT_NAME}}

**Document Version**: 1.0  
**Date**: {{DATE}}  
**Author**: {{AUTHOR}}  
**Status**: {{DRAFT|REVIEW|APPROVED}}

## Executive Summary

**Overall Risk Level**: {{High | Medium | Low}}

**Critical Risks**: {{Number}} risks rated as High probability and High impact

**Key Mitigation Investments**: {{Budget/resources recommended for risk mitigation}}

**Risk Monitoring Approach**: {{How risks will be tracked and managed}}

**Go/No-Go Recommendation**: {{Based on risk analysis}}

## Risk Assessment Framework

### Risk Categories
1. **Business Risks**: Market, financial, strategic, and organizational risks
2. **Technical Risks**: Implementation, integration, and technology risks
3. **Operational Risks**: Process, resource, and execution risks
4. **External Risks**: Regulatory, competitive, and environmental risks

### Risk Scoring Methodology

#### Probability Scale (1-5)
- **1 - Very Low**: 0-10% chance of occurring
- **2 - Low**: 11-30% chance of occurring
- **3 - Medium**: 31-50% chance of occurring
- **4 - High**: 51-80% chance of occurring
- **5 - Very High**: 81-100% chance of occurring

#### Impact Scale (1-5)
- **1 - Very Low**: Minimal impact, easy to recover
- **2 - Low**: Minor delays or cost increases
- **3 - Medium**: Significant impact on timeline/budget
- **4 - High**: Major impact, may threaten project success
- **5 - Very High**: Critical impact, project failure likely

#### Risk Priority Matrix
```
Impact →
↓ Probability   Low(1-2)  Medium(3)  High(4-5)
Very High(5)      Med      High      Critical
High(4)           Low      Med       High
Medium(3)         Low      Med       Med
Low(2)            Low      Low       Low
Very Low(1)       Low      Low       Low
```

## Business Risks

### Market and Competitive Risks

#### BR1: {{Risk Title}}
- **Description**: {{Detailed description of the risk}}
- **Probability**: {{1-5}} ({{Probability label}})
- **Impact**: {{1-5}} ({{Impact label}})
- **Risk Score**: {{Probability × Impact}}
- **Priority**: {{Critical | High | Medium | Low}}
- **Root Causes**: {{What could cause this risk}}
- **Early Warning Indicators**: {{How to detect this risk emerging}}
- **Impact Assessment**: {{Detailed impact if risk occurs}}
- **Mitigation Strategy**: {{How to prevent or reduce risk}}
- **Contingency Plan**: {{What to do if risk occurs}}
- **Owner**: {{Person responsible for monitoring and mitigating}}
- **Review Frequency**: {{How often to reassess}}

#### BR2: {{Risk Title}}
*Repeat format for all business risks...*

### Financial and Budget Risks

#### BR3: Budget Overrun Risk
- **Description**: {{Project costs exceed approved budget}}
- **Probability**: {{1-5}}
- **Impact**: {{1-5}}
- **Risk Score**: {{Calculation}}
- **Priority**: {{Level}}
- **Potential Overrun**: {{Estimated additional costs}}
- **Cost Categories at Risk**: {{Which budget areas are most vulnerable}}
- **Mitigation Strategy**: {{Budget controls and monitoring}}
- **Contingency Plan**: {{Additional funding sources or scope reduction}}
- **Owner**: {{Project Manager/Finance}}

*Continue for all financial risks...*

### Organizational and Resource Risks

#### BR4: Key Personnel Unavailability
- **Description**: {{Critical team members become unavailable}}
- **Probability**: {{1-5}}
- **Impact**: {{1-5}}
- **Critical Roles**: {{Which roles are single points of failure}}
- **Knowledge Transfer Plan**: {{How to mitigate knowledge loss}}
- **Backup Resource Plan**: {{Alternative resources and cross-training}}
- **Owner**: {{HR/Team Lead}}

*Continue for all organizational risks...*

## Technical Risks

### Implementation and Development Risks

#### TR1: {{Technical Risk Title}}
- **Description**: {{Detailed technical risk description}}
- **Probability**: {{1-5}}
- **Impact**: {{1-5}}
- **Technical Complexity**: {{What makes this technically challenging}}
- **Dependencies**: {{What this risk depends on}}
- **Proof of Concept Needed**: {{Yes/No and scope}}
- **Technical Mitigation**: {{How to reduce technical risk}}
- **Alternative Approaches**: {{Backup technical solutions}}
- **Owner**: {{Technical Lead/Architect}}

*Continue for all technical implementation risks...*

### Integration and Compatibility Risks

#### TR2: Third-party Integration Failures
- **Description**: {{Integration with external systems fails}}
- **Affected Integrations**: {{List of critical integrations}}
- **Failure Scenarios**: {{How integrations might fail}}
- **Testing Strategy**: {{How to validate integrations}}
- **Fallback Options**: {{What to do if integrations fail}}
- **Owner**: {{Integration Lead}}

*Continue for all integration risks...*

### Technology and Platform Risks

#### TR3: Technology Obsolescence
- **Description**: {{Chosen technologies become outdated}}
- **Technology Components**: {{Which technologies are at risk}}
- **Obsolescence Timeline**: {{When risk might materialize}}
- **Migration Complexity**: {{Difficulty of changing technologies}}
- **Future-proofing Strategy**: {{How to minimize obsolescence risk}}
- **Owner**: {{Technical Architect}}

*Continue for all technology risks...*

## Operational Risks

### Project Execution Risks

#### OR1: Scope Creep
- **Description**: {{Project scope expands beyond original plan}}
- **Probability**: {{1-5}}
- **Impact**: {{1-5}}
- **Scope Change Drivers**: {{What typically causes scope changes}}
- **Change Control Process**: {{How to manage scope changes}}
- **Stakeholder Management**: {{How to manage expectations}}
- **Owner**: {{Project Manager}}

*Continue for all execution risks...*

### Quality and Performance Risks

#### OR2: Quality Standards Not Met
- **Description**: {{Delivered solution doesn't meet quality requirements}}
- **Quality Dimensions**: {{Performance, reliability, usability, etc.}}
- **Testing Strategy**: {{How to ensure quality}}
- **Quality Gates**: {{Checkpoints to validate quality}}
- **Remediation Plan**: {{How to fix quality issues}}
- **Owner**: {{QA Lead}}

*Continue for all quality risks...*

## External Risks

### Regulatory and Compliance Risks

#### ER1: Regulatory Changes
- **Description**: {{New regulations affect project requirements}}
- **Regulatory Areas**: {{Which regulations are relevant}}
- **Change Probability**: {{Likelihood of regulatory changes}}
- **Compliance Monitoring**: {{How to track regulatory changes}}
- **Adaptation Strategy**: {{How to respond to changes}}
- **Owner**: {{Compliance Officer}}

*Continue for all regulatory risks...*

### Vendor and Partnership Risks

#### ER2: Vendor Performance Issues
- **Description**: {{Third-party vendors fail to deliver}}
- **Critical Vendors**: {{Which vendors are essential}}
- **Performance Metrics**: {{How to measure vendor performance}}
- **Alternative Vendors**: {{Backup vendor options}}
- **Contract Protections**: {{Legal protections and penalties}}
- **Owner**: {{Procurement/Vendor Manager}}

*Continue for all vendor risks...*

## Risk Mitigation Plan

### High-Priority Risk Mitigation

#### Critical Risks (Risk Score 16-25)
| Risk ID | Risk Title | Mitigation Investment | Timeline | Expected Reduction |
|---------|------------|---------------------|----------|--------------------|
| {{ID}} | {{Title}} | {{Budget/resources}} | {{Timeline}} | {{Risk score reduction}} |

#### High Risks (Risk Score 12-15)
| Risk ID | Risk Title | Mitigation Investment | Timeline | Expected Reduction |
|---------|------------|---------------------|----------|--------------------|
| {{ID}} | {{Title}} | {{Budget/resources}} | {{Timeline}} | {{Risk score reduction}} |

### Risk Mitigation Budget
| Category | Mitigation Cost | Justification |
|----------|----------------|---------------|
| Business Risk Mitigation | {{Cost}} | {{Why this investment is needed}} |
| Technical Risk Mitigation | {{Cost}} | {{Why this investment is needed}} |
| Operational Risk Mitigation | {{Cost}} | {{Why this investment is needed}} |
| External Risk Mitigation | {{Cost}} | {{Why this investment is needed}} |
| **Total Mitigation Investment** | **{{Total}}** | **{{Overall justification}}** |

### Risk Monitoring Plan

#### Risk Review Schedule
- **Daily**: {{Risks monitored daily}}
- **Weekly**: {{Weekly risk review process}}
- **Monthly**: {{Monthly comprehensive risk assessment}}
- **Quarterly**: {{Quarterly risk strategy review}}

#### Risk Escalation Process
1. **Risk Detection**: {{How risks are identified and reported}}
2. **Initial Assessment**: {{Who does initial risk evaluation}}
3. **Escalation Criteria**: {{When to escalate risks}}
4. **Decision Authority**: {{Who makes risk decisions at each level}}
5. **Communication Plan**: {{How risks are communicated}}

## Contingency Planning

### Critical Risk Scenarios

#### Scenario 1: {{High-Impact Risk Scenario}}
**Trigger Events**: {{What would cause this scenario}}
**Impact Assessment**: {{Full impact if scenario occurs}}
**Response Plan**: 
1. {{Immediate action 1}}
2. {{Immediate action 2}}
3. {{Recovery action 1}}
4. {{Recovery action 2}}
**Resource Requirements**: {{Additional resources needed}}
**Recovery Timeline**: {{How long to recover}}

#### Scenario 2: {{Another High-Impact Scenario}}
*Repeat format for each critical scenario...*

### Contingency Budget
**Recommended Contingency**: {{Percentage}} of project budget
**Justification**: {{Why this contingency level is appropriate}}
**Contingency Allocation**:
- {{Risk Category 1}}: {{Budget allocation}}
- {{Risk Category 2}}: {{Budget allocation}}
- {{Risk Category 3}}: {{Budget allocation}}
- General Contingency: {{Buffer amount}}

## Risk Communication Plan

### Stakeholder Risk Communication
| Stakeholder Group | Risk Information Needed | Communication Method | Frequency |
|------------------|------------------------|-------------------|----------|
| {{Executive Sponsors}} | {{High-level risk status}} | {{Method}} | {{Frequency}} |
| {{Project Team}} | {{Operational risk details}} | {{Method}} | {{Frequency}} |
| {{Business Users}} | {{Impact and timeline risks}} | {{Method}} | {{Frequency}} |

### Risk Reporting Format
- **Executive Summary**: {{One-page risk status for executives}}
- **Detailed Risk Register**: {{Comprehensive risk tracking}}
- **Risk Dashboard**: {{Visual risk monitoring tool}}
- **Risk Alerts**: {{Immediate communication for critical risks}}

## Success Criteria for Risk Management

### Risk Management KPIs
- **Risk Identification Rate**: {{Target for identifying risks early}}
- **Mitigation Effectiveness**: {{Target for risk score reduction}}
- **Contingency Usage**: {{Target for staying within contingency}}
- **Risk Response Time**: {{Target for addressing new risks}}

### Risk Management Success Definition
**Success**: {{What constitutes successful risk management}}
**Failure Criteria**: {{What would indicate risk management failure}}
**Review and Improvement**: {{How to improve risk management over time}}

## Appendices

### A. Complete Risk Register
{{Comprehensive list of all identified risks with full details}}

### B. Risk Assessment Worksheets
{{Templates and tools used for risk assessment}}

### C. Historical Risk Data
{{Lessons learned from similar projects}}

### D. Risk Mitigation Cost-Benefit Analysis
{{Detailed analysis of mitigation investment returns}}
```

---

## Template 6: Resource Plan

### Template Overview
- **Purpose**: Comprehensive resource planning and budget justification
- **Audience**: Executive sponsors, finance, project management, HR
- **Completion Time**: 4-6 hours for detailed planning
- **Dependencies**: Project scope, timeline estimates, technical architecture

### Resource Plan Template

```markdown
# Resource Plan: {{PROJECT_NAME}}

**Document Version**: 1.0  
**Date**: {{DATE}}  
**Author**: {{AUTHOR}}  
**Status**: {{DRAFT|REVIEW|APPROVED}}

## Executive Summary

**Total Project Investment**: {{Total budget range}}
**Project Duration**: {{Timeline}}
**Core Team Size**: {{Number of FTEs}}
**Peak Resource Requirement**: {{Maximum concurrent resources}}
**ROI Projection**: {{Expected return on investment}}
**Resource Risk Level**: {{High/Medium/Low}}

## Resource Planning Methodology

### Estimation Approach
- **Bottom-up Estimation**: {{Work breakdown structure based}}
- **Analogous Estimation**: {{Comparison to similar projects}}
- **Parametric Estimation**: {{Model-based estimation}}
- **Three-point Estimation**: {{Best/most likely/worst case}}

### Planning Assumptions
- {{Assumption 1 about resource availability}}
- {{Assumption 2 about skill levels and productivity}}
- {{Assumption 3 about external dependencies}}
- {{Assumption 4 about timeline and scope stability}}

## Budget Breakdown

### Development Budget

#### Personnel Costs
| Role | FTE | Duration | Rate | Total Cost | Justification |
|------|-----|----------|------|------------|---------------|
| {{Role 1}} | {{FTE}} | {{Months}} | {{$/month}} | {{Total}} | {{Why needed}} |
| {{Role 2}} | {{FTE}} | {{Months}} | {{$/month}} | {{Total}} | {{Why needed}} |
| {{Role 3}} | {{FTE}} | {{Months}} | {{$/month}} | {{Total}} | {{Why needed}} |
| **Subtotal Personnel** | | | | **{{Total}}** | |

#### Technology and Infrastructure
| Category | Item | Cost | Duration | Total | Justification |
|----------|------|------|----------|-------|--------------|
| Development Tools | {{Tool/License}} | {{$/month}} | {{Months}} | {{Total}} | {{Why needed}} |
| Cloud Infrastructure | {{Service}} | {{$/month}} | {{Months}} | {{Total}} | {{Why needed}} |
| Third-party Services | {{API/Service}} | {{$/month}} | {{Months}} | {{Total}} | {{Why needed}} |
| **Subtotal Technology** | | | | **{{Total}}** | |

#### External Services
| Service Type | Provider | Cost | Justification |
|-------------|----------|------|---------------|
| {{Service 1}} | {{Vendor}} | {{Cost}} | {{Why needed}} |
| {{Service 2}} | {{Vendor}} | {{Cost}} | {{Why needed}} |
| **Subtotal External** | | **{{Total}}** | |

### Operational Budget (Post-Launch)

#### Ongoing Personnel
| Role | FTE | Annual Cost | Responsibilities |
|------|-----|-------------|------------------|
| {{Role 1}} | {{FTE}} | {{Cost}} | {{Ongoing duties}} |
| {{Role 2}} | {{FTE}} | {{Cost}} | {{Ongoing duties}} |
| **Subtotal Personnel** | | **{{Total}}** | |

#### Infrastructure and Services
| Category | Annual Cost | Growth Factor | 3-Year Projection |
|----------|-------------|---------------|-------------------|
| Hosting/Cloud | {{Cost}} | {{%}} | {{Projection}} |
| Third-party APIs | {{Cost}} | {{%}} | {{Projection}} |
| Monitoring/Tools | {{Cost}} | {{%}} | {{Projection}} |
| **Subtotal Infrastructure** | **{{Total}}** | | **{{Projection}}** |

### Total Budget Summary
| Category | Year 0 (Development) | Year 1 | Year 2 | Year 3 | Total 3-Year |
|----------|---------------------|--------|--------|--------|---------------|
| Personnel | {{Cost}} | {{Cost}} | {{Cost}} | {{Cost}} | {{Total}} |
| Technology | {{Cost}} | {{Cost}} | {{Cost}} | {{Cost}} | {{Total}} |
| External Services | {{Cost}} | {{Cost}} | {{Cost}} | {{Cost}} | {{Total}} |
| **Total** | **{{Cost}}** | **{{Cost}}** | **{{Cost}}** | **{{Cost}}** | **{{Total}}** |

## Timeline and Milestones

### Project Phases

#### Phase 0: Discovery ({{Duration}})
- **Duration**: {{Start date}} to {{End date}}
- **Resource Requirements**: {{FTEs and roles}}
- **Key Deliverables**: {{Major outputs}}
- **Milestone**: {{Completion criteria}}
- **Budget**: {{Phase budget}}

#### Phase 1: Architecture & Design ({{Duration}})
- **Duration**: {{Start date}} to {{End date}}
- **Resource Requirements**: {{FTEs and roles}}
- **Key Deliverables**: {{Major outputs}}
- **Milestone**: {{Completion criteria}}
- **Budget**: {{Phase budget}}

#### Phase 2: Development ({{Duration}})
- **Duration**: {{Start date}} to {{End date}}
- **Resource Requirements**: {{FTEs and roles}}
- **Key Deliverables**: {{Major outputs}}
- **Milestone**: {{Completion criteria}}
- **Budget**: {{Phase budget}}

#### Phase 3: Testing & Deployment ({{Duration}})
- **Duration**: {{Start date}} to {{End date}}
- **Resource Requirements**: {{FTEs and roles}}
- **Key Deliverables**: {{Major outputs}}
- **Milestone**: {{Completion criteria}}
- **Budget**: {{Phase budget}}

### Critical Path Analysis

#### Critical Path Dependencies
1. {{Dependency 1}}: {{Impact on timeline}}
2. {{Dependency 2}}: {{Impact on timeline}}
3. {{Dependency 3}}: {{Impact on timeline}}

#### Timeline Risk Factors
- **Resource Availability**: {{Risk to timeline}}
- **Technical Complexity**: {{Risk to timeline}}
- **External Dependencies**: {{Risk to timeline}}
- **Scope Changes**: {{Risk to timeline}}

### Buffer and Contingency Planning
- **Schedule Buffer**: {{Percentage}} added to each phase
- **Resource Buffer**: {{Percentage}} additional resources
- **Budget Contingency**: {{Percentage}} for unforeseen costs

## Team Structure and Organization

### Core Team Structure

#### Leadership Team
- **Project Manager**: {{Name/TBD}} - {{Responsibilities}}
- **Technical Lead**: {{Name/TBD}} - {{Responsibilities}}
- **Product Owner**: {{Name/TBD}} - {{Responsibilities}}
- **UX Lead**: {{Name/TBD}} - {{Responsibilities}}

#### Development Team
| Role | Count | Seniority Level | Key Responsibilities |
|------|--------|----------------|---------------------|
| {{Role 1}} | {{#}} | {{Level}} | {{Responsibilities}} |
| {{Role 2}} | {{#}} | {{Level}} | {{Responsibilities}} |
| {{Role 3}} | {{#}} | {{Level}} | {{Responsibilities}} |

#### Supporting Roles
| Role | Allocation | When Needed | Responsibilities |
|------|------------|-------------|------------------|
| {{Role 1}} | {{% time}} | {{Phase}} | {{Support provided}} |
| {{Role 2}} | {{% time}} | {{Phase}} | {{Support provided}} |

### Organizational Structure

```
Project Sponsor
       |
Project Manager
       |
   Core Team
   /   |   \
Dev  UX  QA  Ops
```

### Team Communication Plan
- **Daily Standups**: {{Who, when, format}}
- **Weekly Status**: {{Who, when, format}}
- **Monthly Reviews**: {{Who, when, format}}
- **Quarterly Planning**: {{Who, when, format}}

## Resource Requirements Analysis

### Skill Requirements

#### Technical Skills Needed
| Skill | Criticality | Current Gap | Acquisition Plan |
|-------|-------------|-------------|------------------|
| {{Skill 1}} | {{High/Med/Low}} | {{Gap level}} | {{Hire/train/contract}} |
| {{Skill 2}} | {{High/Med/Low}} | {{Gap level}} | {{Hire/train/contract}} |
| {{Skill 3}} | {{High/Med/Low}} | {{Gap level}} | {{Hire/train/contract}} |

#### Business Skills Needed
| Skill | Criticality | Current Gap | Acquisition Plan |
|-------|-------------|-------------|------------------|
| {{Skill 1}} | {{High/Med/Low}} | {{Gap level}} | {{Hire/train/contract}} |
| {{Skill 2}} | {{High/Med/Low}} | {{Gap level}} | {{Hire/train/contract}} |

### Resource Acquisition Plan

#### Internal Resource Allocation
- **Available Internal Resources**: {{Who and when}}
- **Internal Resource Gaps**: {{What's missing}}
- **Training Requirements**: {{What training is needed}}
- **Internal Timeline**: {{When resources are available}}

#### External Resource Requirements
- **Contractor Needs**: {{Specific contractor requirements}}
- **Vendor Services**: {{What services to outsource}}
- **Consultant Expertise**: {{Where we need expert help}}
- **Procurement Timeline**: {{When to engage external resources}}

### Resource Allocation Schedule

#### Resource Ramping Plan
| Phase | Month | {{Role 1}} | {{Role 2}} | {{Role 3}} | Total FTE |
|-------|--------|-----------|-----------|-----------|----------|
| Discovery | 1 | {{FTE}} | {{FTE}} | {{FTE}} | {{Total}} |
| | 2 | {{FTE}} | {{FTE}} | {{FTE}} | {{Total}} |
| Architecture | 3 | {{FTE}} | {{FTE}} | {{FTE}} | {{Total}} |
| | 4 | {{FTE}} | {{FTE}} | {{FTE}} | {{Total}} |
| Development | 5 | {{FTE}} | {{FTE}} | {{FTE}} | {{Total}} |
| | 6 | {{FTE}} | {{FTE}} | {{FTE}} | {{Total}} |

## Capacity Planning

### Current Capacity Assessment
- **Available Capacity**: {{Current team capacity}}
- **Committed Capacity**: {{Existing project commitments}}
- **Free Capacity**: {{Available for new project}}
- **Capacity Constraints**: {{Limiting factors}}

### Scaling Strategy
- **Gradual Scaling**: {{How to scale team over time}}
- **Peak Capacity Planning**: {{Maximum resource needs}}
- **Scaling Timeline**: {{When to add/remove resources}}
- **Scaling Costs**: {{Cost implications of scaling}}

### Capacity Risk Management
- **Key Person Dependencies**: {{Single points of failure}}
- **Capacity Buffer Strategy**: {{How to handle demand spikes}}
- **Cross-training Plan**: {{Knowledge sharing strategy}}
- **Capacity Monitoring**: {{How to track and manage capacity}}

## Vendor and Contract Management

### External Service Providers

#### Vendor 1: {{Vendor Name}}
- **Service Provided**: {{What they'll do}}
- **Contract Value**: {{Total cost}}
- **Contract Duration**: {{Timeline}}
- **Key Deliverables**: {{What they'll deliver}}
- **Management Approach**: {{How to manage relationship}}
- **Risk Mitigation**: {{How to mitigate vendor risk}}

*Repeat for each vendor...*

### Procurement Planning
- **Procurement Timeline**: {{When to engage vendors}}
- **Vendor Selection Criteria**: {{How to choose vendors}}
- **Contract Negotiation**: {{Key terms and conditions}}
- **Vendor Management**: {{Ongoing relationship management}}

## Resource Optimization

### Efficiency Strategies
- **Resource Sharing**: {{How to share resources across projects}}
- **Automation Opportunities**: {{Where to automate work}}
- **Process Optimization**: {{How to improve efficiency}}
- **Tool Standardization**: {{Common tools and platforms}}

### Cost Optimization
- **Variable Cost Management**: {{Scaling costs with demand}}
- **Fixed Cost Optimization**: {{Reducing ongoing fixed costs}}
- **Resource Utilization**: {{Maximizing resource efficiency}}
- **ROI Optimization**: {{Focusing on highest-value activities}}

## Risk Analysis

### Resource-Related Risks

#### High-Priority Resource Risks
| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|--------------------||
| {{Resource Risk 1}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} |
| {{Resource Risk 2}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} |
| {{Resource Risk 3}} | {{H/M/L}} | {{H/M/L}} | {{How to mitigate}} |

### Contingency Planning
- **Budget Contingency**: {{Percentage for cost overruns}}
- **Schedule Contingency**: {{Buffer for delays}}
- **Resource Contingency**: {{Backup resource options}}
- **Scope Contingency**: {{Features that can be deferred}}

## Success Metrics

### Resource Management KPIs
- **Budget Variance**: {{Target: stay within X% of budget}}
- **Schedule Adherence**: {{Target: deliver on time}}
- **Resource Utilization**: {{Target: X% utilization}}
- **Quality Metrics**: {{Deliverable quality standards}}

### Return on Investment Analysis

#### Investment Summary
- **Total Investment**: {{3-year total cost}}
- **Expected Benefits**: {{Quantified business value}}
- **Payback Period**: {{When investment pays back}}
- **ROI Calculation**: {{Return percentage}}

#### Benefits Realization
| Benefit Category | Year 1 | Year 2 | Year 3 | Total |
|------------------|--------|--------|--------|---------|
| {{Benefit 1}} | {{Value}} | {{Value}} | {{Value}} | {{Total}} |
| {{Benefit 2}} | {{Value}} | {{Value}} | {{Value}} | {{Total}} |
| **Total Benefits** | **{{Year 1}}** | **{{Year 2}}** | **{{Year 3}}** | **{{Total}}** |

## Appendices

### A. Detailed Work Breakdown Structure
{{Complete WBS with effort estimates}}

### B. Resource Estimation Worksheets
{{Supporting calculations and assumptions}}

### C. Vendor Evaluation Matrix
{{Criteria and scoring for vendor selection}}

### D. Historical Project Data
{{Lessons learned from similar projects}}
```

---

## Template Usage Guide

### Template Selection Criteria

**For Every Project (Required)**:
1. **Project Brief** - Always start here for executive context
2. **Product Requirements Document** - Essential for technical teams

**Based on Project Characteristics**:
- **Market Analysis** - For competitive markets, new products, or strategic initiatives
- **Success Metrics** - For projects with complex success criteria or executive visibility
- **Risk Assessment** - For high-risk projects, regulatory environments, or large investments
- **Resource Plan** - For projects requiring significant resources or budget approval

### Template Customization Guidelines

1. **Remove Irrelevant Sections**: Delete sections that don't apply to your project
2. **Add Industry-Specific Content**: Include domain-specific requirements or constraints
3. **Adjust Complexity Level**: Scale detail up/down based on project size and risk
4. **Integrate with Tools**: Adapt templates to work with your organization's tools

### Quality Assurance Checklist

Before completing any template:
- [ ] All sections completed (no TBD or placeholder text)
- [ ] Stakeholder review and approval obtained
- [ ] Requirements traceable to business objectives
- [ ] Success criteria are specific and measurable
- [ ] Assumptions documented and validated where possible
- [ ] Handoff instructions clear for next phase teams

### Template Maintenance

- **Review Quarterly**: Update templates based on project lessons learned
- **Version Control**: Track template changes and improvements
- **Feedback Loop**: Collect feedback from users and downstream teams
- **Best Practices**: Incorporate industry best practices and organizational standards