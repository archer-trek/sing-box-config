# Agent Guide

## Repository Purpose
- This repo generates sing-box configuration files from reusable JSON templates.
- Source templates live in `templates/`.
- Generated outputs live in `1.12/`.
- The generator entry point is `gen.py`.

## Working Rules
- Treat files under `templates/` and `gen.py` as the source of truth.
- Do not hand-edit generated files in `1.12/` unless the user explicitly asks for a direct patch.
- When template or generator logic changes, regenerate the output files.
- Keep JSON formatting consistent with the generator output: UTF-8, 2-space indentation, no trailing comments.

## Common Tasks
### Regenerate configs
```bash
python3 gen.py
```

### Check generated diffs
```bash
git diff -- templates gen.py 1.12
```

### Validate generated JSON
```bash
python3 -m json.tool 1.12/config.json >/dev/null
python3 -m json.tool 1.12/shellcrash/config.json >/dev/null
python3 -m json.tool 1.12/shellcrash/dns.json >/dev/null
```

## Current Generation Behavior
- `1.12/config.json` merges:
  - `templates/log.json`
  - `templates/experimental.json`
  - `templates/dns.json`
  - `templates/inbounds.json`
  - `templates/outbounds.json`
  - `templates/route.json`
- `1.12/shellcrash/config.json` merges:
  - `templates/outbounds.json`
  - `templates/route.json`
- `1.12/shellcrash/dns.json` is generated from:
  - `templates/dns.json`
- Generation also rewrites rule-set URLs from `/sing-box-ruleset/` to `/sing-box-ruleset-compatible/`.

## Change Strategy
- For DNS changes, start with `templates/dns.json`.
- For inbound changes, start with `templates/inbounds.json`.
- For outbound changes, start with `templates/outbounds.json`.
- For routing changes, start with `templates/route.json`.
- For generation logic changes, edit `gen.py` and then regenerate outputs.
