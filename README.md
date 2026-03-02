# M365 Copilot Agent Test

Test repository for M365 Copilot to GitHub Copilot custom agent integration.

## Custom Agent

This repo contains a custom agent at `.github/agents/m365-task-handler.agent.md`
that processes tasks originating from Microsoft 365 (emails, meeting transcripts).

-----

# M365-GH-Integration: Assigning GitHub Issues to Copilot Custom Agents via API

This document describes the end-to-end process of creating a GitHub issue and assigning it to a **GitHub Copilot custom agent** using the GitHub REST and GraphQL APIs.

## Prerequisites

- A GitHub repository with **GitHub Copilot** enabled (requires Copilot Enterprise or Premium)
- A [GitHub Personal Access Token (PAT)](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) with `repo` scope, or the `gh` CLI authenticated
- A custom agent definition file in `.github/agents/` (e.g., `m365-task-handler.agent.md`)

## Overview

| Step | API | Endpoint |
|------|-----|----------|
| 1. Create the issue | REST | `POST /repos/{owner}/{repo}/issues` |
| 2. Create a "copilot" label | REST | `POST /repos/{owner}/{repo}/labels` |
| 3. Label the issue | REST | `POST /repos/{owner}/{repo}/issues/{number}/labels` |
| 4. Assign to Copilot | REST | `POST /repos/{owner}/{repo}/issues/{number}/assignees` |
| 5. Verify | GraphQL | `query { repository { issue { ... } } }` |

---

## Step 1: Create a Custom Agent Definition

Before creating issues, ensure your repo has a Copilot custom agent. Place a markdown file in `.github/agents/`:

```
.github/
  agents/
    m365-task-handler.agent.md
```

Example agent file:

```yaml
---
name: m365-task-handler
description: >
  Handles development tasks sourced from Microsoft 365 emails and
  meeting transcripts.
target: github-copilot
tools:
  - read
  - edit
  - search
  - execute
---

You are a coding agent that receives tasks originating from
Microsoft 365 (emails, meeting transcripts, action items).
```

## Step 2: Create a GitHub Issue via REST API

### Using `curl`

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/{owner}/{repo}/issues \
  -d '{
    "title": "Add M365 email integration webhook handler",
    "body": "## Source: Microsoft 365 Email\n\n**Summary:** Build a webhook endpoint for M365 email notifications.\n\n## Requirements\n- [ ] Create webhook endpoint\n- [ ] Parse M365 payloads\n- [ ] Extract action items\n- [ ] Add auth validation",
    "labels": ["enhancement"]
  }'
```

### Using `gh` CLI

```bash
gh issue create \
  --repo {owner}/{repo} \
  --title "Add M365 email integration webhook handler" \
  --body "## Summary
Build a webhook endpoint for M365 email notifications.

## Requirements
- [ ] Create webhook endpoint
- [ ] Parse M365 payloads
- [ ] Extract action items"
```

**Response** (key fields):

```json
{
  "number": 3,
  "html_url": "https://github.com/{owner}/{repo}/issues/3",
  "state": "open"
}
```

## Step 3: Create a Label for Copilot (One-Time Setup)

### Using `curl`

```bash
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/{owner}/{repo}/labels \
  -d '{
    "name": "copilot",
    "description": "Assign to GitHub Copilot coding agent",
    "color": "6f42c1"
  }'
```

### Using `gh` CLI

```bash
gh label create "copilot" \
  --repo {owner}/{repo} \
  --description "Assign to GitHub Copilot coding agent" \
  --color "6f42c1"
```

## Step 4: Assign the Issue to Copilot

There are two mechanisms for triggering GitHub Copilot on an issue:

### Method A: Label-Based Assignment

Add the `copilot` label to the issue. When Copilot coding agent is enabled for the repo, labeling an issue triggers the agent to pick it up.

```bash
# Using curl
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/{owner}/{repo}/issues/3/labels \
  -d '{"labels": ["copilot"]}'
```

```bash
# Using gh CLI
gh issue edit 3 --repo {owner}/{repo} --add-label "copilot"
```

### Method B: Direct User Assignment (Copilot Premium/Enterprise)

When Copilot coding agent is fully enabled, `Copilot` appears as an assignable user in the repository. You can assign it just like any collaborator:

```bash
# Using curl
curl -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/{owner}/{repo}/issues/3/assignees \
  -d '{"assignees": ["Copilot"]}'
```

```bash
# Using gh CLI
gh issue edit 3 --repo {owner}/{repo} --add-assignee "Copilot"
```

> **Note:** Direct assignment to `Copilot` requires that the Copilot coding agent feature is enabled in the repository settings under **Settings > Copilot > Coding agent**. If the feature is not enabled, the API will silently ignore the assignment or return a user-not-found error.

## Step 5: Verify the Issue via GraphQL

Use the GraphQL API to confirm the issue was created with correct labels and assignments:

```graphql
query {
  repository(owner: "{owner}", name: "{repo}") {
    issue(number: 3) {
      title
      state
      url
      labels(first: 10) {
        nodes {
          name
        }
      }
      assignees(first: 10) {
        nodes {
          login
        }
      }
    }
  }
}
```

### Using `gh` CLI

```bash
gh api graphql -f query='
{
  repository(owner: "{owner}", name: "{repo}") {
    issue(number: 3) {
      title
      state
      url
      labels(first: 10) {
        nodes { name }
      }
      assignees(first: 10) {
        nodes { login }
      }
    }
  }
}'
```

## Complete Automation Script

Combine all steps into a single script:

```bash
#!/bin/bash
set -euo pipefail

OWNER="siddjoshi"
REPO="m365-copilot-agent-test"
GITHUB_TOKEN="${GITHUB_TOKEN:?Set GITHUB_TOKEN}"

API="https://api.github.com"
HEADERS=(-H "Authorization: Bearer $GITHUB_TOKEN"
         -H "Accept: application/vnd.github+json"
         -H "X-GitHub-Api-Version: 2022-11-28")

# 1. Create the issue
ISSUE=$(curl -s -X POST "${HEADERS[@]}" \
  "$API/repos/$OWNER/$REPO/issues" \
  -d '{
    "title": "Add M365 email integration webhook handler",
    "body": "## Requirements\n- [ ] Create webhook endpoint\n- [ ] Parse M365 payloads"
  }')

ISSUE_NUMBER=$(echo "$ISSUE" | jq -r '.number')
echo "Created issue #$ISSUE_NUMBER"

# 2. Create copilot label (skip if exists)
curl -s -X POST "${HEADERS[@]}" \
  "$API/repos/$OWNER/$REPO/labels" \
  -d '{"name":"copilot","color":"6f42c1","description":"Assign to Copilot agent"}' \
  || echo "Label already exists"

# 3. Add label to issue
curl -s -X POST "${HEADERS[@]}" \
  "$API/repos/$OWNER/$REPO/issues/$ISSUE_NUMBER/labels" \
  -d '{"labels":["copilot"]}'

echo "Issue #$ISSUE_NUMBER labeled with 'copilot'"

# 4. Try direct assignment (requires Copilot coding agent enabled)
curl -s -X POST "${HEADERS[@]}" \
  "$API/repos/$OWNER/$REPO/issues/$ISSUE_NUMBER/assignees" \
  -d '{"assignees":["Copilot"]}'

echo "Assignment attempted. Verify at: https://github.com/$OWNER/$REPO/issues/$ISSUE_NUMBER"
```

## How the Custom Agent Processes the Issue

Once Copilot picks up the issue, the workflow is:

```
Issue Created ──> Copilot Triggered ──> Agent Loaded
                                            │
                              .github/agents/m365-task-handler.agent.md
                                            │
                                  ┌─────────┴─────────┐
                                  │  Agent Workflow:   │
                                  │  1. Parse issue    │
                                  │  2. Search code    │
                                  │  3. Implement fix  │
                                  │  4. Open PR        │
                                  └────────────────────┘
```

## API Reference

| Action | Method | Endpoint | Docs |
|--------|--------|----------|------|
| Create issue | `POST` | `/repos/{owner}/{repo}/issues` | [Create an issue](https://docs.github.com/en/rest/issues/issues#create-an-issue) |
| Add labels | `POST` | `/repos/{owner}/{repo}/issues/{number}/labels` | [Add labels](https://docs.github.com/en/rest/issues/labels#add-labels-to-an-issue) |
| Assign users | `POST` | `/repos/{owner}/{repo}/issues/{number}/assignees` | [Add assignees](https://docs.github.com/en/rest/issues/assignees#add-assignees-to-an-issue) |
| Create label | `POST` | `/repos/{owner}/{repo}/labels` | [Create a label](https://docs.github.com/en/rest/issues/labels#create-a-label) |
| GraphQL query | `POST` | `/graphql` | [GraphQL API](https://docs.github.com/en/graphql) |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `Could not resolve to a User with the login of 'Copilot'` | Copilot coding agent not enabled for the repo | Enable it in repo **Settings > Copilot > Coding agent** |
| Assignment silently ignored | Token lacks `repo` scope | Generate a new PAT with `repo` scope |
| Agent doesn't pick up the issue | No agent definition in `.github/agents/` | Create an agent markdown file |
| 404 on API calls | Incorrect owner/repo or private repo without access | Verify the repo path and token permissions |
