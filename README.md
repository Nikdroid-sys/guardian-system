# 🛡️ Guardian-MCP: Zero-Trust AI Governance Layer

**Guardian-MCP** is a security-first Model Context Protocol (MCP) server that eliminates "Autonomous Agent Liability." It acts as a deterministic security gate between an LLM's intent and system execution, ensuring no AI agent can provision vulnerable code into your environment.

### 🚀 Overview
Autonomous agents often suggest or install outdated, vulnerable Python packages to solve tasks. Guardian-MCP intercepts these commands in real-time, audits them against the global vulnerability database, and only provisions "Clean" dependencies.

* **Action:** Engineered a "Security-First" MCP server using FastMCP 3.0.
* **Context:** Automated real-time vulnerability scanning via **Google’s OSV Database**.
* **Result:** 100% block rate of high-CVE dependency installs, utilizing `uv` for isolated, production-ready execution.

---

### 📊 System Architecture

![Guardian-MCP Architecture](./path-to-your-eraser-diagram.png)

---

### ✨ Key Features: Standard vs. Guardian
| Feature | Standard Agent | **Guardian-Protected Agent** |
| :--- | :---: | :--- |
| **Dependency Audit** | ❌ None | ✅ **Real-time OSV Scan** |
| **Security Policy** | ❌ Trust-by-default | ✅ **Zero-Trust Enforcement** |
| **Vulnerability Handling** | ❌ Exploit Risk | ✅ **Auto-Healing/Patching** |
| **Environment** | ❌ Global/Polluted | ✅ **Isolated `uv` Vault** |

---

### 📖 Human-in-the-Loop & Self-Healing
If a version is blocked (e.g., Flask 0.12.1), the agent triggers a **Self-Correction** node:
1. **Identify:** Detects CVE-2018-1000656.
2. **Intercept:** Guardian-MCP returns `Status: BLOCKED`.
3. **Resolve:** Agent researches the next stable version (e.g., 3.1.3) and re-attempts provisioning.

---

### 💻 Getting Started

**1. Clone & Install**
```bash
git clone [https://github.com/your-username/guardian-mcp.git](https://github.com/your-username/guardian-mcp.git)
cd guardian-mcp
uv pip install -r requirements.txt