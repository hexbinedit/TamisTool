# TamisTool Configuration Reference

> Full reference for `~/.tamis/config.toml`

---

## Initialising the Config File

```bash
tamis config init
```

This creates `~/.tamis/config.toml` with default values. To overwrite an existing config:

```bash
tamis config init --force
```

To use a custom path:

```bash
tamis config init --config /path/to/config.toml
```

---

## Config File Location

| Platform | Default path |
|---|---|
| Linux / macOS | `~/.tamis/config.toml` |
| Windows | `%USERPROFILE%\.tamis\config.toml` |

---

## Full Reference

### `[database]` section

| Key | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `"single"` | Storage mode: `"single"` or `"per_client"` |
| `single_db_path` | string | `"~/.tamis/tamis.db"` | Path to the single shared DB file |
| `per_client_dir` | string | `"~/.tamis/clients"` | Directory for per-client DB files |

#### `mode = "single"` (default)

All clients and projects are stored in a single `tamis.db` file, scoped by client and project
foreign keys. Best for analysts managing multiple clients from one workstation.

```toml
[database]
mode = "single"
single_db_path = "~/.tamis/tamis.db"
```

#### `mode = "per_client"`

Each client gets its own `<client_name>.db` file inside `per_client_dir`. Best for:
- Isolating client data
- Air-gapped handoffs (share a single client DB file)
- Multi-analyst environments where each analyst owns a client

```toml
[database]
mode = "per_client"
per_client_dir = "~/.tamis/clients"
```

---

### `[scan]` section

| Key | Type | Default | Description |
|---|---|---|---|
| `stale_days` | integer | `30` | Tables with no data in the past N days are marked as `stale` |

```toml
[scan]
stale_days = 30
```

---

## Environment Variable Reference

Credentials are **never stored in config.toml**. Pass them at runtime via environment variables
(recommended) or CLI flags.

| Variable | Description | CLI flag equivalent |
|---|---|---|
| `TAMIS_APP_ID` | Azure AD service principal app ID | `--app-id` |
| `TAMIS_APP_SECRET` | Service principal secret | `--app-secret` |
| `TAMIS_TENANT_ID` | Azure tenant ID | `--tenant-id` |
| `TAMIS_WORKSPACE_ID` | Sentinel workspace ID | `--workspace-id` |
| `TAMIS_CLUSTER_URI` | Kusto cluster URI | `--cluster-uri` |

### Example `.env` for scripting

```bash
export TAMIS_APP_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export TAMIS_APP_SECRET=your-secret-here
export TAMIS_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export TAMIS_WORKSPACE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export TAMIS_CLUSTER_URI=https://ade.loganalytics.io/subscriptions/.../resourcegroups/.../providers/...
```

---

## Updating Config Values

Use `tamis config set` to update individual values:

```bash
tamis config set database.mode per_client
tamis config set scan.stale_days 14
```

View current config:

```bash
tamis config show
```

---

*hexbinedit.io — https://hexbinedit.io*
