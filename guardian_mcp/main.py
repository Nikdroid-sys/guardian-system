import asyncio
import httpx
import subprocess
import os
from fastmcp import FastMCP
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# --- Absolute Path Strategy ---
ROOT_DIR = Path.cwd() 
VAULT_PATH = ROOT_DIR / "guardian_vault"
VAULT_PATH.mkdir(exist_ok=True)
load_dotenv(dotenv_path=ROOT_DIR / ".env")

# Required for stateless HTTP communication
os.environ["FASTMCP_STATELESS_HTTP"] = "true"
PORT = int(os.getenv("PORT", 8000))

console = Console()
server = FastMCP("Guardian-MCP")

OSV_API_URL = "https://api.osv.dev/v1/query"

@server.tool()
async def secure_provision(package_name: str, version: str) -> str:
    """Audits and installs Python packages into the secure vault."""
    console.print(f"\n[bold yellow]🛡️  Guardian Audit:[/bold yellow] Inspecting {package_name}=={version}...")

    # 1. Real-time Vulnerability Scan
    async with httpx.AsyncClient() as client:
        try:
            payload = {"version": version, "package": {"name": package_name, "ecosystem": "PyPI"}}
            response = await client.post(OSV_API_URL, json=payload, timeout=15.0)
            response.raise_for_status()
            scan_results = response.json()
        except Exception as e:
            return f"Status: FAILED. OSV Database unreachable: {str(e)}"

    # 2. Safety Interception
    if "vulns" in scan_results:
        vuln = scan_results["vulns"][0]
        cve_id = vuln.get("id", "CVE-UNKNOWN")
        summary = vuln.get("summary", "No details provided.")
        console.print(Panel(f"[red]CRITICAL VULNERABILITY DETECTED[/red]\nID: {cve_id}\nIssue: {summary}", 
                            title="INTERCEPTED", border_style="red"))
        return f"Status: BLOCKED. Vulnerability found: {cve_id}. Summary: {summary}. Use a patched version."

    # 3. Secure Provisioning via UV
    console.print(f"[bold green]✅ Clean Check:[/bold green] Provisioning {package_name} to Vault...")
    try:
        target_dir = str(VAULT_PATH.absolute())
        # --force-reinstall ensures the vault is populated even if cached locally
        cmd = ["uv", "pip", "install", f"{package_name}=={version}", "--target", target_dir, "--no-cache", "--force-reinstall"]
        
        process = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            files = os.listdir(target_dir)
            if files:
                return f"Status: SUCCESS. {package_name}=={version} is now available in the Guardian Vault."
            return "Status: FAILED. Vault directory is empty after install."
        return f"Status: FAILED. uv Error: {stderr.decode()}"
    except Exception as e:
        return f"Status: FAILED. System error: {str(e)}"

if __name__ == "__main__":
    console.print(Panel("[bold cyan]GUARDIAN-MCP SERVER ACTIVE[/bold cyan]\nTransport: HTTP | Port: 8000", border_style="cyan"))
    server.run(transport="http", host="127.0.0.1", port=PORT)