import os
import json
from typing import List, Dict, Any


def load_json(file_path: str) -> Dict[Any, Any]:
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
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


def merge(templates: List[str], overwrite: list, target_file: str):
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
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"配置已生成到: {target_file}")

    return result


def _insert_custom_rules(result: Dict[Any, Any], rules: List[Dict[Any, Any]]):
    """插入自定义路由"""
    result['route']['rules'] = rules + result['route']['rules']


def _replace_rule_set_url(result: Dict[Any, Any]):
    for rule_set in result['route']['rule_set']:
        rule_set['url'] = rule_set['url'].replace(
            '/sing-box-ruleset/', '/sing-box-ruleset-compatible/')


if __name__ == '__main__':
    merge(
        [
            'templates/log.json', 'templates/experimental.json', 'templates/dns.json',
            'templates/inbounds.json', 'templates/outbounds.json', 'templates/route.json',
        ],
        [
            _replace_rule_set_url
        ],
        '1.12/config.json')

    merge(
        [
            'templates/outbounds.json', 'templates/route.json',
        ],
        [
            _replace_rule_set_url
        ],
        '1.12/shellcrash/config.json')

    merge(['templates/dns.json'], None, '1.12/shellcrash/dns.json')
