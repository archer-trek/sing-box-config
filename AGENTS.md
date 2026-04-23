# Agent Guide

## Repository Purpose
- This repo generates sing-box configuration files from reusable JSON templates.
- Source templates live in `templates/`.
- Generated outputs live in `1.13/`.
- The generator entry point is `main.py`.

## Working Rules
- Treat files under `templates/` and `main.py` as the source of truth.
- Do not hand-edit generated files in `1.13/` unless the user explicitly asks for a direct patch.
- When template or generator logic changes, regenerate the output files.
- Keep JSON formatting consistent with the generator output: UTF-8, 2-space indentation, no trailing comments.

## Common Tasks
### Regenerate configs
```bash
python3 main.py
```

### Check generated diffs
```bash
git diff -- templates main.py 1.13
```

### Validate generated JSON
```bash
python3 -m json.tool 1.13/config.json >/dev/null
python3 -m json.tool 1.13/config-with-tailscale.json >/dev/null
python3 -m json.tool 1.13/shellcrash/config.json >/dev/null
python3 -m json.tool 1.13/shellcrash/dns.json >/dev/null
```

## Current Generation Behavior
- `1.13/config.json` merges:
  - `templates/log.json`
  - `templates/experimental.json`
  - `templates/dns.json`
  - `templates/inbounds.json`
  - `templates/outbounds.json`
  - `templates/route.json`
- `1.13/config-with-tailscale.json` merges:
  - `templates/log.json`
  - `templates/experimental.json`
  - `templates/dns.json`
  - `templates/inbounds.json`
  - `templates/outbounds.json`
  - `templates/route.json`
  - `templates/endpoints.json`
- `1.13/shellcrash/config.json` merges:
  - `templates/outbounds.json`
  - `templates/route.json`
- `1.13/shellcrash/dns.json` is generated from:
  - `templates/dns.json`
- Generation rewrites rule-set URLs from `/sing-box-ruleset/` to `/sing-box-ruleset-compatible/`.
- `config-with-tailscale.json` prepends a custom route for `192.168.5.0/24` to outbound `ts-ep`.

## Change Strategy
- For DNS changes, start with `templates/dns.json`.
- For inbound changes, start with `templates/inbounds.json`.
- For outbound changes, start with `templates/outbounds.json`.
- For routing changes, start with `templates/route.json`.
- For Tailscale endpoint changes, start with `templates/endpoints.json`.
- For generation logic changes, edit `main.py` and then regenerate outputs.
