---
description: Interactive rollback to previous development state
---

# Development State Rollback

Request: "$ARGUMENTS"

**IMPORTANT**: You MUST immediately use the Task tool to invoke the git-checkpoint agent for rollback. Do not describe - actually invoke it NOW.

Use the Task tool with:
- subagent_type: "git-checkpoint"
- description: "Rollback to previous state"
- prompt: "You are the git-checkpoint agent specializing in safe rollback operations.

User Request: Rollback to: $ARGUMENTS

Your tasks:
1. Show recent checkpoints with context and timestamps
2. Analyze impact of potential rollback
3. Provide rollback options:
   - Soft rollback: Keep changes in working directory
   - Hard rollback: Completely restore previous state
   - Selective rollback: Choose specific files
   - Recovery branch: Rollback on new branch preserving current work
4. Execute rollback safely with emergency backup
5. Report rollback results and current status

Ensure safe, intelligent rollback with multiple recovery options."