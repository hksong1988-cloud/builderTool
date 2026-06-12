# builderTool - Git 多项目分支管理工具

一个 PyQt5 桌面工具，用于集中管理工作目录（如 `haimanyun`）下的多个 Git 项目。

## 功能

- 扫描目录下所有 git 项目并列表展示
- 克隆新仓库到指定目录
- 读取/切换本地分支（切换前自动检测未提交代码，防止冲突）
- 常用操作：status / pull / add+commit（提交前弹窗确认改动文件）/ push
- 基于指定基准分支创建新分支并自动切换（支持中文分支名）
- 全站点 IP 检索替换（先预览匹配，再执行替换）
- 操作日志面板：完整记录每条 git 命令及输出，错误红色显示

## 环境要求

- Python 3.7+
- 已安装 git 并加入 PATH，且配置好凭证（SSH key 或凭证缓存）

## 安装与运行

```bash
pip install -r requirements.txt
python main.py
```

## 项目结构

```
builderTool/
├── main.py               # 入口
├── requirements.txt
└── app/
    ├── config.py         # 配置持久化（~/.buildertool_config.json）
    ├── git_ops.py        # git 命令封装（参数列表方式，支持中文分支名）
    ├── ip_replace.py     # 全站点 IP 检索/替换
    ├── worker.py         # 后台线程（QThread）
    └── main_window.py    # 主窗口 UI 与交互
```
