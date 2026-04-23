# sing-box-config

Template-based `sing-box` configuration generator.

This repo keeps editable source fragments in `templates/` and generates ready-to-use JSON files in `1.13/` with `main.py`.

## Structure

- `templates/log.json` - log level and timestamp settings
- `templates/experimental.json` - Clash API and cache settings
- `templates/dns.json` - DNS upstreams and DNS routing rules
- `templates/inbounds.json` - local inbound definitions
- `templates/outbounds.json` - selectors, regional groups, direct outbound, and auto-match groups
- `templates/route.json` - traffic routing rules and remote rule-set definitions
- `templates/endpoints.json` - optional endpoint definitions, currently used for Tailscale
- `main.py` - merges templates and writes generated configs
- `1.13/config.json` - full generated config
- `1.13/config-with-tailscale.json` - full generated config with Tailscale endpoint and extra custom route
- `1.13/shellcrash/config.json` - generated outbound + route config for ShellCrash
- `1.13/shellcrash/dns.json` - generated DNS config for ShellCrash

## How It Works

`main.py` deep-merges template files in a fixed order:

- `1.13/config.json`
  - `templates/log.json`
  - `templates/experimental.json`
  - `templates/dns.json`
  - `templates/inbounds.json`
  - `templates/outbounds.json`
  - `templates/route.json`
- `1.13/config-with-tailscale.json`
  - `templates/log.json`
  - `templates/experimental.json`
  - `templates/dns.json`
  - `templates/inbounds.json`
  - `templates/outbounds.json`
  - `templates/route.json`
  - `templates/endpoints.json`
- `1.13/shellcrash/config.json`
  - `templates/outbounds.json`
  - `templates/route.json`
- `1.13/shellcrash/dns.json`
  - `templates/dns.json`

During generation:

- rule-set URLs are rewritten from `/sing-box-ruleset/` to `/sing-box-ruleset-compatible/`
- `config-with-tailscale.json` prepends a custom route so `192.168.5.0/24` goes through outbound `ts-ep`

## Generate

```bash
python3 main.py
```

## Validate

```bash
python3 -m json.tool 1.13/config.json >/dev/null
python3 -m json.tool 1.13/config-with-tailscale.json >/dev/null
python3 -m json.tool 1.13/shellcrash/config.json >/dev/null
python3 -m json.tool 1.13/shellcrash/dns.json >/dev/null
```

## Typical Changes

- Update DNS behavior in `templates/dns.json`
- Update traffic routing in `templates/route.json`
- Update policy groups and region selectors in `templates/outbounds.json`
- Update local inbound behavior in `templates/inbounds.json`
- Update endpoint definitions in `templates/endpoints.json`
- Update generation logic in `main.py`

After changing source files, regenerate the outputs in `1.13/`.

## Notes

- Treat `templates/` and `main.py` as the source of truth
- Avoid manually editing generated files in `1.13/`
- Generated JSON uses UTF-8 and 2-space indentation
