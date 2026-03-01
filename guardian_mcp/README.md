# Guardian MCP (Zero-Trust Security Layer)

## Overview
A FastMCP 3.0 server that acts as a "Security Proxy" for Python environments. It intercepts all installation requests and validates them against the Google OSV (Open Source Vulnerabilities) Database before execution.

## Technical Architecture
- **Language:** Python 3.12+ (managed by `uv`)
- **Framework:** `fastmcp` 3.0
- **Database:** Real-time API calls to `https://api.osv.dev/v1/query`
- **Isolation:** Operations are restricted to a local `./guardian_vault` directory.

## Core Tool: `secure_provision`
**Arguments:** - `package_name` (str): e.g., "jinja2"
- `version` (str): e.g., "2.11.2"
- `purpose` (str): Context for the audit log.

**Logic Flow:**
1. **Intercept:** Receive the package and version.
2. **Scan:** Send a POST request to OSV.dev API with `{ "package": {"name": package_name, "ecosystem": "PyPI"}, "version": version }`.
3. **Analyze:** - If `vulns` key exists in JSON response -> Return `Status: BLOCKED` with CVE ID and summary.
   - If `vulns` is empty -> Proceed.
4. **Execute:** Run `uv pip install <package>==<version> --target ./guardian_vault`.
5. **Report:** Return success message with the local path to the library.
