"""Git 命令封装：全部用参数列表方式调用，免疫中文/括号/空格分支名问题。"""
import os
import subprocess
from dataclasses import dataclass


@dataclass
class GitResult:
    cmd: str            # 展示用的命令字符串
    code: int           # 退出码，0 为成功
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.code == 0

    @property
    def output(self) -> str:
        parts = [p for p in (self.stdout.strip(), self.stderr.strip()) if p]
        return "\n".join(parts)


CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def run_git(repo: str, *args: str, timeout: int = 120) -> GitResult:
    """在 repo 目录执行 git 命令。args 为参数列表，不走 shell。"""
    cmd_display = "git " + " ".join(args)
    try:
        proc = subprocess.run(
            # core.quotepath=false：让中文文件名正常显示而不是 \346\211... 转义
            ["git", "-c", "core.quotepath=false"] + list(args),
            cwd=repo,
            capture_output=True,
            timeout=timeout,
            creationflags=CREATE_NO_WINDOW,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},  # 凭证缺失时直接失败而不是卡住等输入
        )
        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")
        return GitResult(cmd_display, proc.returncode, stdout, stderr)
    except subprocess.TimeoutExpired:
        return GitResult(cmd_display, -1, "", f"命令超时（>{timeout}s），请检查网络或凭证配置")
    except FileNotFoundError:
        return GitResult(cmd_display, -1, "", "未找到 git，请确认已安装并加入 PATH")


# ---------- 常用操作 ----------

def is_git_repo(path: str) -> bool:
    return os.path.isdir(os.path.join(path, ".git"))


def scan_projects(work_dir: str) -> list:
    """扫描工作目录下所有 git 项目（一级子目录）。"""
    projects = []
    if not os.path.isdir(work_dir):
        return projects
    try:
        for name in sorted(os.listdir(work_dir), key=str.lower):
            full = os.path.join(work_dir, name)
            if os.path.isdir(full) and is_git_repo(full):
                projects.append(name)
    except OSError:
        pass
    return projects


def current_branch(repo: str) -> GitResult:
    return run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")


def local_branches(repo: str) -> tuple:
    """返回 (GitResult, 分支列表, 当前分支)。"""
    r = run_git(repo, "branch", "--list")
    branches, current = [], ""
    if r.ok:
        for line in r.stdout.splitlines():
            line = line.rstrip()
            if not line.strip():
                continue
            if line.startswith("* "):
                current = line[2:].strip()
                branches.append(current)
            else:
                branches.append(line.strip())
    return r, branches, current


def dirty_files(repo: str) -> tuple:
    """返回 (GitResult, 脏文件列表)。"""
    r = run_git(repo, "status", "--short")
    files = [ln for ln in r.stdout.splitlines() if ln.strip()] if r.ok else []
    return r, files


def remote_branches(repo: str) -> tuple:
    """返回 (GitResult, 远端分支列表)。过滤掉 HEAD 指针行。"""
    r = run_git(repo, "branch", "-r")
    branches = []
    if r.ok:
        for line in r.stdout.splitlines():
            name = line.strip()
            if not name or "->" in name:  # 跳过 origin/HEAD -> origin/master
                continue
            branches.append(name)
    return r, branches
