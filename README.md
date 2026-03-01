# 🛡️ Guardian-MCP: Zero-Trust AI Governance Layer

**Guardian-MCP** is a security-first Model Context Protocol (MCP) server that eliminates "Autonomous Agent Liability." It acts as a deterministic security gate between an LLM's intent and system execution, ensuring no AI agent can provision vulnerable code into your environment.

### 🚀 Overview
Autonomous agents often suggest or install outdated, vulnerable Python packages to solve tasks. Guardian-MCP intercepts these commands in real-time, audits them against the global vulnerability database, and only provisions "Clean" dependencies.

* **Action:** Engineered a "Security-First" MCP server using FastMCP 3.0.
* **Context:** Automated real-time vulnerability scanning via **Google’s OSV Database**.
* **Result:** 100% block rate of high-CVE dependency installs, utilizing `uv` for isolated, production-ready execution.

---

### 📊 System Architecture

![Guardian-MCP Architecture](https://github.com/Nikdroid-sys/guardian-system/blob/main/assets/architecture.png)

---

### 🧪 Scenarios
Scenario 1: The "Legacy Exploit" Block
User Request: "I need to build a legacy-compatible web server. Install Flask==0.12.1."

The Threat: Flask 0.12.1 has a known high-severity vulnerability (CVE-2018-1000656) that allows for Jinja2 template injection.

Guardian Action:

Intercepts the uv pip install command.

Queries Google OSV and identifies the CVE.

Blocks the installation and returns a CRITICAL alert to the Agent.

Agent Outcome: The Agent reads the alert, researches a patched version, and automatically upgrades to Flask==3.1.3.

Scenario 2: Zero-Trust "Clean Room" Provisioning
User Request: "Set up an environment for data analysis with requests."

Guardian Action:

Resolves "latest" to requests==2.32.3.

Performs a clean scan (No CVEs found).

Uses uv to target the guardian_vault/ directory.

Result: The package is provisioned in a hidden, isolated vault so it doesn't pollute your global system python or other projects.

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
git clone https://github.com/Nikdroid-sys/guardian-system.git
cd guardian-system
uv pip install -r requirements.txt

---

**2. Run**
Terminal 1
python .\guardian_mcp\main.py

Terminal 2
python .\researcher_agent\main.py

