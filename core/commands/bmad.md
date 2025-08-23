---
description: Initiate comprehensive BMAD planning workflow
---

# BMAD Planning Workflow Initiation

Request: "$ARGUMENTS"

**IMPORTANT**: You MUST immediately use the Task tool to invoke the master-orchestrator agent. Do not just describe - actually invoke it NOW.

Use the Task tool with:
- subagent_type: "master-orchestrator"
- description: "BMAD planning coordination"
- prompt: "You are the Master Orchestrator for BMAD planning workflows.

User Request: $ARGUMENTS

Coordinate the complete BMAD planning sequence:

Phase 1: Strategic Planning
- Use bmad-analyst for requirements gathering and user research
- Use bmad-project-manager for feature prioritization and roadmap planning  
- Use bmad-architect for system design and technical architecture
- Coordinate human review gates for planning approval

Phase 2: Story Creation
- Use bmad-scrum-master for context engineering and story decomposition
- Ensure story files have clear acceptance criteria
- Coordinate human review for story validation

Phase 3: Implementation Coordination  
- Select appropriate specialist agents based on requirements
- Use git-checkpoint for safety throughout implementation
- Coordinate quality gates for testing and integration

Execute the complete Governed Agentic Agile Loop (GAAL) workflow with proper governance gates and safety measures."