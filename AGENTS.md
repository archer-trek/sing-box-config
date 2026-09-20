# Agent Guide

## Project Overview

This repo generates sing-box (1.13.x / 1.14.x) configuration files by deep-merging reusable JSON templates. The generator entry point is `main.py`.

- **Source of truth**: `templates/` + `main.py`
- **Generated outputs**: `1.13/`, `1.14/`
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
1.14/
  config.json                          # Full config for sing-box 1.14 (no Tailscale)
  config-with-tailscale.json           # Full config for sing-box 1.14 with Tailscale
```

## Working Rules

1. **Never hand-edit files in `1.13/` or `1.14/`** unless the user explicitly asks for a direct patch. Always modify templates or `main.py` instead, then regenerate.
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
| `_fill_direct_domains(result)` | Inject `DIRECT_DOMAIN_SUFFIX` into the empty `domain_suffix: []` anchor rules in route/dns; raises if no anchor is found |
| `_insert_custom_rules(result, rules)` | Prepend custom route rules to `result["route"]["rules"]` |
| `_adapt_for_1_14(result)` | Adapt for sing-box 1.14: remove deprecated `dns.independent_cache`, configure `http_clients` and `route.default_http_client` |

The direct-connect domain list lives in a single place: the `DIRECT_DOMAIN_SUFFIX` constant in `main.py`. The templates keep empty `domain_suffix: []` anchor rules (route: `outbound: 直连`; dns: `server: dns_direct`) that `_fill_direct_domains` fills at generation time — do not hand-edit those lists in templates.

### Generation pipeline

```
config.json:
  log.json → experimental.json → dns.json → inbounds.json → outbounds.json → route.json
  overwrite: _replace_rule_set_url + _fill_direct_domains

config-with-tailscale.json:
  (same as above) + endpoints.json
  overwrite: _replace_rule_set_url + _fill_direct_domains + prepend {ip_cidr: [192.168.5.0/24], outbound: ts-ep}

shellcrash/config.json:
  outbounds.json → route.json
  overwrite: _replace_rule_set_url + _fill_direct_domains

shellcrash/dns.json:
  dns.json only
  overwrite: _fill_direct_domains

1.14/config.json:
  log.json → experimental.json → dns.json → inbounds.json → outbounds.json → route.json
  overwrite: _fill_direct_domains + _adapt_for_1_14

1.14/config-with-tailscale.json:
  (same as above) + endpoints.json
  overwrite: _fill_direct_domains + _adapt_for_1_14 + prepend {ip_cidr: [192.168.5.0/24], outbound: ts-ep}
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
python3 -m json.tool 1.14/config.json > /dev/null && echo "OK"
python3 -m json.tool 1.14/config-with-tailscale.json > /dev/null && echo "OK"
```

### Review diffs before committing
```bash
git diff -- templates main.py 1.13 1.14
```

### Run a Python snippet (e.g. quick template inspection)
```bash
python3 -c "import json; d=json.load(open('templates/route.json')); print(len(d['route']['rules']), 'rules')"
```

## Change Strategy

| Goal | Start here |
|---|---|
| DNS changes (servers, rules, fake-ip) | `templates/dns.json` |
| Direct-connect domain list | `DIRECT_DOMAIN_SUFFIX` in `main.py` |
| Inbound changes (ports, sniffing) | `templates/inbounds.json` |
| Outbound changes (nodes, selectors, groups) | `templates/outbounds.json` |
| Routing changes (rules, rule-sets) | `templates/route.json` |
| Tailscale endpoint changes | `templates/endpoints.json` |
| Generation logic or post-processing | `main.py` |
| Log level or Clash API settings | `templates/log.json` / `templates/experimental.json` |
