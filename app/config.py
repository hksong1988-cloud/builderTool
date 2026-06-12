"""配置持久化：记忆工作目录历史、上次选中项目等。"""
import json
import os
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".buildertool_config.json")

DEFAULTS = {
    "work_dirs": [],          # 历史工作目录，最近的排前面
    "last_project": "",       # 上次选中的项目名
    "last_old_ip": "",
    "last_new_ip": "",
    "project_notes": {},      # 项目备注 {项目名: 备注}
    "ip_history": [],         # IP 替换历史 [{time, project, branch, old_ip, new_ip, files}]
    "branch_name_history": [], # 新建分支名历史（全局复用）[{name, note}]，最近的排前面
    "theme": "dark",          # 界面主题 dark / light
}


def load_config() -> dict:
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = dict(DEFAULTS)
        cfg.update(data if isinstance(data, dict) else {})
        return cfg
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULTS)


def save_config(cfg: dict) -> None:
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def remember_work_dir(cfg: dict, path: str) -> None:
    """把目录插到历史最前面，去重，最多保留 10 条。"""
    path = os.path.normpath(path)
    dirs = [d for d in cfg.get("work_dirs", []) if os.path.normpath(d) != path]
    dirs.insert(0, path)
    cfg["work_dirs"] = dirs[:10]


def add_ip_history(cfg: dict, project: str, branch: str, old_ip: str,
                   new_ip: str, files: int) -> None:
    """追加一条 IP 替换历史，最新的排最前，最多保留 200 条。"""
    history = cfg.setdefault("ip_history", [])
    history.insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": project,
        "branch": branch,
        "old_ip": old_ip,
        "new_ip": new_ip,
        "files": files,
    })
    cfg["ip_history"] = history[:200]


def old_ips_for_project(cfg: dict, project: str) -> list:
    """返回某项目执行过替换的 new_ip 列表（去重，最近用过的排前面）。
    新IP成功替换后即成为下一轮的旧IP候选，旧IP本身不再重复记录。"""
    seen, result = set(), []
    for rec in cfg.get("ip_history", []):
        if rec.get("project") != project:
            continue
        ip = rec.get("new_ip", "")
        if ip and ip not in seen:
            seen.add(ip)
            result.append(ip)
    return result


def remove_old_ip_for_project(cfg: dict, project: str, ip: str) -> None:
    """从 ip_history 中删除某项目所有 new_ip == ip 的记录，使其从旧IP候选中消失。"""
    cfg["ip_history"] = [
        rec for rec in cfg.get("ip_history", [])
        if not (rec.get("project") == project and rec.get("new_ip") == ip)
    ]


# ---- 分支名历史：存储为 [{name, note}] ----

def _norm_branch_entry(entry) -> dict:
    """兼容旧版字符串条目，统一转为 {name, note} dict。"""
    if isinstance(entry, str):
        return {"name": entry, "note": ""}
    return {"name": entry.get("name", ""), "note": entry.get("note", "")}


def branch_name_history(cfg: dict) -> list:
    """返回规范化后的分支名历史列表 [{name, note}]。"""
    return [_norm_branch_entry(e) for e in cfg.get("branch_name_history", [])]


def add_branch_name(cfg: dict, name: str, note: str = "") -> None:
    """把分支名插到历史最前面，去重（按 name），最多保留 50 条。"""
    history = [e for e in branch_name_history(cfg) if e["name"] != name]
    history.insert(0, {"name": name, "note": note})
    cfg["branch_name_history"] = history[:50]


def remove_branch_name(cfg: dict, name: str) -> None:
    """从历史中删除指定分支名（按 name 匹配）。"""
    cfg["branch_name_history"] = [
        e for e in branch_name_history(cfg) if e["name"] != name
    ]
