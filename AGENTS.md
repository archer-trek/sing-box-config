# Agent Guide

## Project Overview

This repo generates sing-box (1.13.x) configuration files by deep-merging reusable JSON templates. The generator entry point is `main.py`.

- **Source of truth**: `templates/` + `main.py`
- **Generated outputs**: `1.13/`
- **Python**: 3.14 (managed via `uv`, see `pyproject.toml` and `.python-version`)
- **No external dependencies** — `main.py` uses only the Python standard library.

## Project Structure

```
templates/
  log.json           # Log level and timestamp settings
  experimental.json  # Clash API and cache file settings
  dns.json           # DNS servers, rules, and DNS routing
  inbounds.json      # Local inbound listeners (mixed/socks/http)
  outbounds.json     # Outbound nodes, selectors, and policy groups
  route.json         # Traffic routing rules and remote rule-set definitions
  endpoints.json     # Optional endpoint definitions (currently for Tailscale)
main.py              # Generator: deep-merge templates → write output JSON
1.13/
  config.json                          # Full config (no Tailscale)
  config-with-tailscale.json           # Full config with Tailscale endpoint + custom route
  shellcrash/
    config.json                        # Outbounds + route only (for ShellCrash)
    dns.json                           # DNS only (for ShellCrash)
```

## Working Rules

1. **Never hand-edit files in `1.13/`** unless the user explicitly asks for a direct patch. Always modify templates or `main.py` instead, then regenerate.
2. After changing templates or generator logic, always regenerate outputs with `python3 main.py`.
3. Match the existing code style:
   - JSON: UTF-8, 2-space indent, LF line endings, final newline (see `.editorconfig`)
   - Python: UTF-8, 4-space indent, LF line endings (see `.editorconfig`)
   - JSON output is written via `json.dump(..., ensure_ascii=False, indent=2)` — no trailing commas, no comments.

## Generator Logic (`main.py`)

### Core functions

| Function | Purpose |
|---|---|
| `load_json(path)` | Load a JSON file into a dict |
| `deep_merge(base, override)` | Recursively merge two dicts — override keys win |
| `merge(templates, overwrite, target)` | Load and deep-merge a list of template files, apply optional overwrite callbacks, write to target |
| `_replace_rule_set_url(result)` | Rewrite rule-set URLs: `/sing-box-ruleset/` → `/sing-box-ruleset-compatible/` |
| `_insert_custom_rules(result, rules)` | Prepend custom route rules to `result["route"]["rules"]` |

### Generation pipeline

```
config.json:
  log.json → experimental.json → dns.json → inbounds.json → outbounds.json → route.json
  overwrite: _replace_rule_set_url

config-with-tailscale.json:
  (same as above) + endpoints.json
  overwrite: _replace_rule_set_url + prepend {ip_cidr: [192.168.5.0/24], outbound: ts-ep}

shellcrash/config.json:
  outbounds.json → route.json
  overwrite: _replace_rule_set_url

shellcrash/dns.json:
  dns.json only (no overwrite)
```

### Adding a new overwrite callback

An overwrite callback receives the merged result dict and mutates it in place. To add new post-processing logic:

1. Define a function `def _my_transform(result: Dict): ...` in `main.py`
2. Add it to the `overwrite` list of the target merge call
3. Regenerate with `python3 main.py`

## Common Tasks

### Regenerate all configs
```bash
python3 main.py
```

### Validate generated JSON syntax
```bash
python3 -m json.tool 1.13/config.json > /dev/null && echo "OK"
python3 -m json.tool 1.13/config-with-tailscale.json > /dev/null && echo "OK"
python3 -m json.tool 1.13/shellcrash/config.json > /dev/null && echo "OK"
python3 -m json.tool 1.13/shellcrash/dns.json > /dev/null && echo "OK"
```

### Review diffs before committing
```bash
git diff -- templates main.py 1.13
```

### Run a Python snippet (e.g. quick template inspection)
```bash
python3 -c "import json; d=json.load(open('templates/route.json')); print(len(d['route']['rules']), 'rules')"
```

## Change Strategy

| Goal | Start here |
|---|---|
| DNS changes (servers, rules, fake-ip) | `templates/dns.json` |
| Inbound changes (ports, sniffing) | `templates/inbounds.json` |
| Outbound changes (nodes, selectors, groups) | `templates/outbounds.json` |
| Routing changes (rules, rule-sets) | `templates/route.json` |
| Tailscale endpoint changes | `templates/endpoints.json` |
| Generation logic or post-processing | `main.py` |
| Log level or Clash API settings | `templates/log.json` / `templates/experimental.json` |
