from __future__ import annotations

import json
import os
from typing import Any, Dict, List

# 直连域名列表（唯一来源）：同时注入到 route 规则和 dns 规则中，
# 避免在 templates/route.json 和 templates/dns.json 两处重复维护。
DIRECT_DOMAIN_SUFFIX = [
    "sensorsdata.cn",
    "courier.push.apple.com",
    "opencode.ai",
]


def load_json(file_path: str) -> Dict[Any, Any]:
    """加载JSON文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def deep_merge(base: Dict[Any, Any], override: Dict[Any, Any]) -> Dict[Any, Any]:
    """深度合并两个字典，override会覆盖base中的值"""
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def merge(templates: List[str], overwrite: list | None, target_file: str):
    """
    合并多个模板文件，并可选地用特定版本的配置进行覆盖

    Args:
        templates: 模板文件路径列表
        target_file: 输出文件路径
    """
    # 初始化结果字典
    result = {}

    # 合并所有模板文件
    for template in templates:
        template_data = load_json(template)
        result = deep_merge(result, template_data)

    if overwrite:
        for f in overwrite:
            f(result)

    # 确保目标目录存在
    os.makedirs(os.path.dirname(os.path.abspath(target_file)), exist_ok=True)
    # 写入文件
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"配置已生成到: {target_file}")

    return result


def _insert_custom_rules(result: Dict[Any, Any], rules: List[Dict[Any, Any]]):
    """插入自定义路由"""
    result["route"]["rules"] = rules + result["route"]["rules"]


def _replace_rule_set_url(result: Dict[Any, Any]):
    for rule_set in result["route"]["rule_set"]:
        rule_set["url"] = rule_set["url"].replace("/sing-box-ruleset/", "/sing-box-ruleset-compatible/")


def _fill_direct_domains(result: Dict[Any, Any]):
    """把 DIRECT_DOMAIN_SUFFIX 注入到 route/dns 中的直连锚点规则。

    锚点：route 中 outbound=直连 且 domain_suffix 为空的规则，
    以及 dns 中 server=dns_direct 且 domain_suffix 为空的规则。
    """
    injected = False

    route = result.get("route")
    if route:
        for rule in route.get("rules", []):
            if rule.get("outbound") == "直连" and rule.get("domain_suffix") == []:
                rule["domain_suffix"] = list(DIRECT_DOMAIN_SUFFIX)
                injected = True

    dns = result.get("dns")
    if dns:
        for rule in dns.get("rules", []):
            if rule.get("server") == "dns_direct" and rule.get("domain_suffix") == []:
                rule["domain_suffix"] = list(DIRECT_DOMAIN_SUFFIX)
                injected = True

    if not injected:
        raise ValueError("未找到直连域名锚点规则（domain_suffix: []），请检查模板")

def _adapt_for_1_14(result: Dict[Any, Any]):
    """为 sing-box 1.14 适配配置：
    1. 移除已废弃的 independent_cache 字段
    2. 显式配置 http_clients 与 route.default_http_client
    """
    dns = result.get("dns")
    if dns and "independent_cache" in dns:
        del dns["independent_cache"]

    result["http_clients"] = [
        {
            "tag": "default-client",
            "detour": "默认策略",
        }
    ]
    route = result.get("route")
    if route:
        route["default_http_client"] = "default-client"



if __name__ == "__main__":
    merge(
        [
            "templates/log.json",
            "templates/experimental.json",
            "templates/dns.json",
            "templates/inbounds.json",
            "templates/outbounds.json",
            "templates/route.json",
        ],
        [_replace_rule_set_url, _fill_direct_domains],
        "1.13/config.json",
    )

    merge(
        [
            "templates/log.json",
            "templates/experimental.json",
            "templates/dns.json",
            "templates/inbounds.json",
            "templates/outbounds.json",
            "templates/route.json",
            "templates/endpoints.json",
        ],
        [
            _replace_rule_set_url,
            _fill_direct_domains,
            lambda r: _insert_custom_rules(
                r,
                [
                    {"ip_cidr": ["192.168.5.0/24"], "outbound": "ts-ep"},
                ],
            ),
        ],
        "1.13/config-with-tailscale.json",
    )

    merge(
        [
            "templates/outbounds.json",
            "templates/route.json",
        ],
        [
            _replace_rule_set_url,
            _fill_direct_domains,
        ],
        "1.13/shellcrash/config.json",
    )

    merge(["templates/dns.json"], [_fill_direct_domains], "1.13/shellcrash/dns.json")

    # 1.14 配置生成
    merge(
        [
            "templates/log.json",
            "templates/experimental.json",
            "templates/dns.json",
            "templates/inbounds.json",
            "templates/outbounds.json",
            "templates/route.json",
        ],
        [_fill_direct_domains, _adapt_for_1_14],
        "1.14/config.json",
    )

    merge(
        [
            "templates/log.json",
            "templates/experimental.json",
            "templates/dns.json",
            "templates/inbounds.json",
            "templates/outbounds.json",
            "templates/route.json",
            "templates/endpoints.json",
        ],
        [
            _fill_direct_domains,
            _adapt_for_1_14,
            lambda r: _insert_custom_rules(
                r,
                [
                    {"ip_cidr": ["192.168.5.0/24"], "outbound": "ts-ep"},
                ],
            ),
        ],
        "1.14/config-with-tailscale.json",
    )
