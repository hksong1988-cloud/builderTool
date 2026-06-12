"""全站点 IP 检索与替换。"""
import os

SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".idea", ".vscode", "target", "out"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 超过 5MB 的文件跳过


def _iter_text_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def _read_text(path: str):
    """读文本文件，二进制或超大文件返回 None。"""
    try:
        if os.path.getsize(path) > MAX_FILE_SIZE:
            return None, None
        with open(path, "rb") as f:
            raw = f.read()
        if b"\x00" in raw[:8192]:
            return None, None
        for enc in ("utf-8", "gbk"):
            try:
                return raw.decode(enc), enc
            except UnicodeDecodeError:
                continue
        return None, None
    except OSError:
        return None, None


def preview_ip(root: str, old_ip: str) -> list:
    """返回 [(相对路径, 行号, 行内容), ...]"""
    hits = []
    for path in _iter_text_files(root):
        text, _enc = _read_text(path)
        if text is None or old_ip not in text:
            continue
        rel = os.path.relpath(path, root)
        for i, line in enumerate(text.splitlines(), 1):
            if old_ip in line:
                hits.append((rel, i, line.strip()[:200]))
    return hits


def replace_ip(root: str, old_ip: str, new_ip: str) -> list:
    """执行替换，返回 [(相对路径, 替换次数), ...]"""
    results = []
    for path in _iter_text_files(root):
        text, enc = _read_text(path)
        if text is None or old_ip not in text:
            continue
        count = text.count(old_ip)
        try:
            with open(path, "w", encoding=enc, newline="") as f:
                f.write(text.replace(old_ip, new_ip))
            results.append((os.path.relpath(path, root), count))
        except OSError as e:
            results.append((os.path.relpath(path, root), f"写入失败: {e}"))
    return results
