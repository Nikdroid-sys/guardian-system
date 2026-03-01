# Vulnerability-Aware LangGraph Researcher

## Overview
A high-reasoning autonomous agent built with LangGraph. It is designed to perform data processing tasks but must navigate a Zero-Trust environment where "insecure" tools are blocked by the Guardian MCP.

## Graph State
- `messages`: List of BaseMessages.
- `last_security_alert`: String (Stores CVE details if blocked).
- `retry_count`: Integer (Max 3 attempts to find a safe library).

## Graph Nodes
1. **Planner:** Analyzes the user request (e.g., "Render this HTML template using Jinja2 v2.11.2").
2. **Executor:** Calls the `Guardian MCP` tool `secure_provision`.
3. **Self-Correction (The "Senior" Node):** - If MCP returns `BLOCKED`, this node parses the CVE.
   - It searches for the "fixed_version" in the error message.
   - It updates the plan to install the patched version.
4. **Final Result:** Completes the task using the safely provisioned library.

