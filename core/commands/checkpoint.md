---
description: Create immediate development checkpoint for safety
---

# Development Checkpoint Creation

Request: "$ARGUMENTS"

**IMPORTANT**: You MUST immediately use the Task tool to invoke the git-checkpoint agent. Do not describe - actually invoke it NOW.

Use the Task tool with:
- subagent_type: "git-checkpoint"
- description: "Create git checkpoint"
- prompt: "You are the git-checkpoint agent specializing in version control safety.

User Request: Create a checkpoint for: $ARGUMENTS

Your tasks:
1. Analyze current git state for uncommitted changes
2. Create a meaningful checkpoint commit with descriptive message
3. Add tags for significant milestones if appropriate
4. Report checkpoint status and provide rollback information

Ensure all current work is safely preserved with easy rollback capability."