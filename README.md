# TamisTool (tah-mee-tool) — Kusto Table Analyzer

> SIEM visibility auditing for Microsoft Sentinel and Defender.
> Built by [hexbinedit.io](https://hexbinedit.io)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)]()

---

TamisTool is a command-line SIEM visibility auditing tool. It connects to Microsoft Sentinel and
Defender workspaces to enumerate, assess, and report on the data sources present in a given
environment — answering the recurring question analysts face before every investigation:

> *"What visibility do I actually have in this environment?"*

---

## Quick Install

```bash
git clone https://github.com/hexbinedit/TamisTool.git
cd TamisTool
pipx install 
```

## Quick Start

```bash
# 1. Initialise config
tamis config init

# 2. Register a client
tamis client new acme-corp --workspace-id <workspace-id>

# 3. Run a discovery scan
tamis scan run --client acme-corp \
  --app-id $TAMIS_APP_ID \
  --app-secret $TAMIS_APP_SECRET \
  --tenant-id $TAMIS_TENANT_ID \
  --cluster-uri https://<cluster>.kusto.windows.net

# 4. Generate a report
tamis report generate --client acme-corp --format html --output ./acme_report.html
```

Or use environment variables (recommended for scripting):

```bash
export TAMIS_APP_ID=...
export TAMIS_APP_SECRET=...
export TAMIS_TENANT_ID=...
export TAMIS_WORKSPACE_ID=...
export TAMIS_CLUSTER_URI=https://<cluster>.kusto.windows.net

tamis scan run --client acme-corp
```

## Documentation

| Document | Description |
|---|---|
| [docs/CONFIGURATION.md](docs/CONFIGURATION.md) | Full config reference |
| [docs/SCAN_TYPES.md](docs/SCAN_TYPES.md) | Scan type reference and KQL details |
| [docs/REPORT_GUIDE.md](docs/REPORT_GUIDE.md) | How to read and share TamisTool reports |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Dev setup and contribution guide |

## License

MIT — see [LICENSE](LICENSE).

---

*hexbinedit.io — https://hexbinedit.io*
