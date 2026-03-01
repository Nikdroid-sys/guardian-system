import asyncio
import os
import httpx
import re
from typing import List, TypedDict
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from fastmcp import Client
from rich.console import Console
from rich.panel import Panel

# --- Path Resolution ---
ROOT_DIR = Path.cwd() 
VAULT_PATH = ROOT_DIR / "guardian_vault"
load_dotenv(dotenv_path=ROOT_DIR / ".env")
console = Console()

LLM_CONFIG = {
    "model": os.getenv("OLLAMA_MODEL", "llama3.1"), 
    "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    "api_key": "ollama"
}

class AgentState(TypedDict):
    messages: List[BaseMessage]
    target_package: str
    current_version: str
    last_security_alert: str
    retry_count: int

# --- Helper: Live PyPI Lookup ---
async def get_latest_pypi_version(package_name: str) -> str:
    """Queries PyPI to find the actual latest stable version."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=5.0)
            if response.status_code == 200:
                return response.json()["info"]["version"]
        except:
            pass
    return "0.12.1" # Fallback

# --- MCP Tool Call ---
async def call_guardian_mcp(package: str, version: str):
    async with Client("http://127.0.0.1:8000/mcp") as client:
        result = await client.call_tool("secure_provision", arguments={"package_name": package, "version": version})
        return result.content[0].text

# --- LangGraph Nodes ---
def executor(state: AgentState):
    pkg, ver = state["target_package"], state["current_version"]
    console.print(f"\n[bold blue][Agent][/bold blue] 📦 Requesting Provision: [cyan]{pkg}=={ver}[/cyan]")
    
    try:
        result = asyncio.run(call_guardian_mcp(pkg, ver))
        console.print(f"[dim]{result}[/dim]")
        
        if "Status: BLOCKED" in result:
            state['last_security_alert'] = result
        elif "Status: SUCCESS" in result:
            state['last_security_alert'] = ""
        else:
            state['last_security_alert'] = "CRITICAL_FAILURE"
            
        state['messages'].append(ToolMessage(content=result, tool_call_id="executor"))
    except Exception as e:
        state['last_security_alert'] = f"Connection Error: {str(e)}"
    return state

def self_correction(state: AgentState):
    console.print(f"\n[bold magenta][Self-Correction][/bold magenta] 🧠 Analyzing CVE and seeking patch...")
    llm = ChatOpenAI(**LLM_CONFIG)
    prompt = (
        f"The package {state['target_package']}=={state['current_version']} was BLOCKED due to a vulnerability.\n"
        f"REASON: {state['last_security_alert']}\n"
        "TASK: Provide the NEXT stable version number that is likely patched. "
        "Respond ONLY with the version number (e.g., '3.1.3')."
    )
    response = llm.invoke(prompt)
    # Regex clean to ensure we only get numbers and dots
    state['current_version'] = re.sub(r'[^0-9.]', '', response.content.strip())
    state['retry_count'] += 1
    console.print(f"[bold magenta][Self-Correction][/bold magenta] ✨ Suggested Patch: [green]{state['current_version']}[/green]")
    return state

def should_continue(state: AgentState):
    if state['last_security_alert'] != "" and state['retry_count'] < 3:
        return "self_correct"
    return END

# --- Graph Construction ---
workflow = StateGraph(AgentState)
workflow.add_node("executor", executor)
workflow.add_node("self_correct", self_correction)
workflow.set_entry_point("executor")
workflow.add_conditional_edges("executor", should_continue)
workflow.add_edge("self_correct", "executor")
app = workflow.compile()

# --- Entry Point ---
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(Panel.fit("[bold cyan]🛡️ GUARDIAN-MCP: AGENTIC SECURITY STORY[/bold cyan]", border_style="cyan"))
    
    user_prompt = console.input("\n[bold]Describe the environment to build: [/bold]")
    
    # 1. Strict Extraction with LLM
    llm = ChatOpenAI(**LLM_CONFIG)
    extract_msg = (
        "Extract 'package,version' from the text. Rules:\n"
        "1. If no version is found, use 'LATEST'.\n"
        "2. Respond ONLY with 'package,version'. No other text.\n"
        f"Text: '{user_prompt}'"
    )
    raw_ext = llm.invoke(extract_msg).content.strip()
    
    # Clean Hallucinations
    clean_ext = re.sub(r'[^a-zA-Z0-9.,-]', '', raw_ext).split(",")
    pkg = clean_ext[0].lower()
    ver = clean_ext[1] if len(clean_ext) > 1 else "LATEST"

    # 2. Dynamic PyPI Lookup
    if ver.upper() == "LATEST":
        console.print(f"[dim]🔍 Resolving latest version for {pkg}...[/dim]")
        ver = asyncio.run(get_latest_pypi_version(pkg))

    # 3. Execution
    app.invoke({
        "messages": [HumanMessage(content=user_prompt)], 
        "target_package": pkg, 
        "current_version": ver, 
        "last_security_alert": "", 
        "retry_count": 0
    })
    
    # 4. Final Vault Verification
    if VAULT_PATH.exists() and any(VAULT_PATH.iterdir()):
        pkgs = [i.name for i in VAULT_PATH.iterdir() if i.is_dir() and not i.name.startswith(('.', '_'))]
        console.print(Panel(
            f"[bold green]✅ DEMO SUCCESS[/bold green]\n"
            f"Vault secured at: {VAULT_PATH.absolute()}\n"
            f"Included: {', '.join(pkgs[:3])}...",
            border_style="green"
        ))
    else:
        console.print(Panel("[bold red]❌ DEMO FAILED[/bold red]\nVault is empty. Check MCP logs.", border_style="red"))