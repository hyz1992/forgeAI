#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部 Plugins 和 Skills 安装脚本

兼容：Windows / macOS / Linux
支持检测已安装项，避免重复安装

使用方法:
    python install.py
"""

import subprocess
import json
import sys
import re
import io
import platform
from pathlib import Path
from typing import Optional

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置文件路径
BASE_DIR = Path(__file__).parent
PLUGINS_FILE = BASE_DIR / "plugins.json"
SKILLS_FILE = BASE_DIR / "skills.json"


def run_command(
    cmd: list[str], capture: bool = True, timeout: int = 60
) -> subprocess.CompletedProcess:
    """执行命令"""
    try:
        # Windows 需要 shell=True 来正确执行某些命令
        # 显式指定 UTF-8 编码避免 GBK 解码错误
        if sys.platform == 'win32':
            return subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                timeout=timeout,
                shell=True,
                encoding='utf-8',
                errors='replace',
            )
        else:
            return subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace',
            )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, -1, "", "Command timed out")
    except FileNotFoundError:
        return subprocess.CompletedProcess(cmd, -1, "", f"Command not found: {cmd[0]}")


def is_plugin_installed(plugin_name: str, plugin_id: Optional[str] = None) -> bool:
    """检查 Plugin 是否已安装

    Args:
        plugin_name: 插件名称，如 "superpowers"
        plugin_id: 插件完整 ID，如 "superpowers@superpowers-marketplace"
    """
    result = run_command(["claude", "plugin", "list"])
    if result.returncode != 0:
        # 命令执行失败，假设未安装
        return False

    output = result.stdout
    # 同时检测 plugin_id 和 plugin_name
    if plugin_id and plugin_id in output:
        return True
    return plugin_name in output


def is_marketplace_added(marketplace: str) -> bool:
    """检查 Marketplace 是否已添加"""
    result = run_command(["claude", "plugin", "marketplace", "list"])
    if result.returncode != 0:
        return False
    return marketplace in result.stdout


def is_skill_installed(skill_name: str) -> bool:
    """检查 Skill 是否已安装"""
    result = run_command(["npx", "skills", "list"])
    if result.returncode != 0:
        return False
    return skill_name.lower() in result.stdout.lower()


def add_marketplace(marketplace: str) -> bool:
    """添加 Plugin Marketplace"""
    if is_marketplace_added(marketplace):
        print(f"   ⏭️  Marketplace 已添加: {marketplace}")
        return True

    print(f"   📚 添加 Marketplace: {marketplace}")
    result = run_command(
        ["claude", "plugin", "marketplace", "add", marketplace], timeout=30
    )

    if result.returncode == 0 or "already" in result.stderr.lower():
        print(f"   ✅ 添加成功")
        return True
    else:
        print(f"   ⚠️  添加失败: {result.stderr}")
        return True  # 继续尝试安装


def install_plugin(plugin: dict) -> bool:
    """安装单个 Plugin"""
    name = plugin.get("name", "")
    if not name:
        print("   ❌ Plugin 配置缺少 name 字段")
        return False

    print(f"\n📦 Plugin: {name}")

    # 获取 plugin_id（格式：name@scope）
    package = plugin.get("package", "")
    plugin_id = package if package else None

    # 检查是否已安装
    if is_plugin_installed(name, plugin_id):
        print(f"   ⏭️  已安装，跳过")
        return True

    # 添加 marketplace
    marketplace = plugin.get("marketplace")
    if marketplace:
        add_marketplace(marketplace)

    # 安装 plugin
    package = plugin.get("package", "")
    if not package:
        print(f"   ❌ 缺少 package 字段")
        return False

    print(f"   🔧 安装中...")
    result = run_command(
        ["claude", "plugin", "install", package], timeout=120
    )

    if result.returncode == 0:
        print(f"   ✅ 安装成功")
        return True
    else:
        # 检查是否因为已安装而失败
        if "already" in result.stderr.lower() or "installed" in result.stderr.lower():
            print(f"   ✅ 已安装")
            return True
        print(f"   ❌ 安装失败: {result.stderr}")
        return False


def install_skill(skill: dict) -> bool:
    """安装单个 Skill"""
    name = skill.get("name", "")
    if not name:
        print("   ❌ Skill 配置缺少 name 字段")
        return False

    print(f"\n🎨 Skill: {name}")

    # 检查是否已安装
    if is_skill_installed(name):
        print(f"   ⏭️  已安装，跳过")
        return True

    # 构建安装命令
    package = skill.get("package", "")
    if not package:
        print(f"   ❌ 缺少 package 字段")
        return False

    cmd = ["npx", "skills", "add", package]

    if skill.get("global"):
        cmd.append("-g")

    agent = skill.get("agent")
    if agent:
        cmd.extend(["-a", agent])

    print(f"   🔧 安装中...")
    result = run_command(cmd, timeout=120)

    if result.returncode == 0:
        print(f"   ✅ 安装成功")
        return True
    else:
        # 检查是否因为已安装而失败
        output = (result.stdout + result.stderr).lower()
        if "already" in output or "exists" in output:
            print(f"   ✅ 已安装")
            return True
        # 合并 stdout 和 stderr 显示完整错误信息
        error_msg = result.stderr.strip() or result.stdout.strip() or "未知错误"
        print(f"   ❌ 安装失败: {error_msg}")
        return False


def load_json(file_path: Path) -> list[dict]:
    """加载 JSON 配置文件"""
    if not file_path.exists():
        print(f"⚠️  配置文件不存在: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {file_path}")
        print(f"   {e}")
        return []


def setup_multi_platform_skills() -> bool:
    """
    为 Cursor / Codex 等平台创建 Skills 发现路径。
    创建 .cursor/skills 和 .agents/skills 指向 .claude/skills（符号链接或 junction）。
    """
    print("\n🔗 配置多平台 Skills 发现路径...")

    project_root = BASE_DIR.parent.parent
    source_skills = project_root / ".claude" / "skills"
    if not source_skills.exists() or not source_skills.is_dir():
        print("   ⚠️  .claude/skills 不存在，跳过")
        return True

    source_abs = source_skills.resolve()
    links_created = 0

    for link_dir_name in [".cursor", ".agents"]:
        parent = project_root / link_dir_name
        link_path = parent / "skills"

        if link_path.exists():
            print(f"   ⏭️  {link_dir_name}/skills 已存在，跳过")
            continue

        parent.mkdir(parents=True, exist_ok=True)

        try:
            if sys.platform == "win32":
                _create_junction(link_path, source_abs)
            else:
                link_path.symlink_to(source_abs, target_is_directory=True)
            print(f"   ✅ 已创建 {link_dir_name}/skills -> .claude/skills")
            links_created += 1
        except OSError as e:
            print(f"   ⚠️  创建 {link_dir_name}/skills 失败: {e}")

    return True


def _create_junction(link_path: Path, target_path: Path) -> None:
    """Windows: 使用 mklink /J 创建 junction，必须使用绝对路径。"""
    link_abs = link_path.resolve()
    target_abs = target_path.resolve()
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link_abs), str(target_abs)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise OSError(result.stderr or result.stdout or "mklink failed")


def install_git_hooks() -> bool:
    """安装 Git hooks"""
    print("\n🪝 安装 Git Hooks...")

    project_root = BASE_DIR.parent.parent
    git_hooks_dir = project_root / ".git" / "hooks"

    # 检查是否是 Git 仓库
    if not (project_root / ".git").exists():
        print("   ⚠️  不是 Git 仓库，跳过 Git hooks 安装")
        return True

    # 确保 hooks 目录存在
    git_hooks_dir.mkdir(parents=True, exist_ok=True)

    # 要安装的 hooks
    hooks_to_install = [
        ("pre-commit", BASE_DIR.parent / "hooks" / "pre-commit.py"),
    ]

    installed = 0
    for hook_name, hook_source in hooks_to_install:
        if not hook_source.exists():
            print(f"   ⚠️  Hook 源文件不存在: {hook_source}")
            continue

        hook_target = git_hooks_dir / hook_name

        # 读取源文件内容
        with open(hook_source, "r", encoding="utf-8") as f:
            content = f.read()

        # 添加 shebang
        if not content.startswith("#!"):
            content = "#!/usr/bin/env python3\n" + content

        # 写入目标文件
        with open(hook_target, "w", encoding="utf-8") as f:
            f.write(content)

        # 设置执行权限 (Unix)
        import stat
        hook_target.chmod(hook_target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        print(f"   ✅ 已安装: {hook_name}")
        installed += 1

    return installed == len(hooks_to_install)


def check_prerequisites() -> bool:
    """检查前置条件"""
    print("\n🔍 检查前置条件...")

    # 检查 Node.js
    result = run_command(["node", "--version"])
    if result.returncode != 0:
        print("   ❌ Node.js 未安装")
        print("      请先安装 Node.js: https://nodejs.org/")
        return False
    print(f"   ✅ Node.js: {result.stdout.strip()}")

    # 检查 npm
    result = run_command(["npm", "--version"])
    if result.returncode != 0:
        print("   ❌ npm 未安装")
        return False
    print(f"   ✅ npm: {result.stdout.strip()}")

    # 检查 Claude Code（可选）
    result = run_command(["claude", "--version"])
    if result.returncode != 0:
        print("   ⚠️  Claude Code CLI 未检测到（Plugin 安装可能失败）")
    else:
        print(f"   ✅ Claude Code: {result.stdout.strip()}")

    return True


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 AI Engineering OS - 外部依赖安装")
    print("=" * 60)
    print(f"📍 平台: {platform.system()} {platform.release()}")
    print(f"📍 工作目录: {BASE_DIR.parent.parent}")

    # 先创建多平台 Skills 链接（不依赖 npm/Claude，优先执行）
    setup_multi_platform_skills()

    # 检查前置条件
    if not check_prerequisites():
        sys.exit(1)

    # 加载配置
    plugins = load_json(PLUGINS_FILE)
    skills = load_json(SKILLS_FILE)

    # 统计
    stats = {
        "plugin": {"total": len(plugins), "success": 0},
        "skill": {"total": len(skills), "success": 0},
        "git_hooks": {"total": 1, "success": 0}
    }

    # 安装 Plugins
    if plugins:
        print("\n" + "=" * 60)
        print("📡 安装 Plugins")
        print("=" * 60)

        for plugin in plugins:
            if install_plugin(plugin):
                stats["plugin"]["success"] += 1

    # 安装 Skills
    if skills:
        print("\n" + "=" * 60)
        print("🎨 安装 Skills")
        print("=" * 60)

        for skill in skills:
            if install_skill(skill):
                stats["skill"]["success"] += 1

    # 安装 Git Hooks
    if install_git_hooks():
        stats["git_hooks"]["success"] = 1

    # 汇总
    print("\n" + "=" * 60)
    print("📊 安装结果")
    print("=" * 60)

    if plugins:
        print(
            f"Plugins:   {stats['plugin']['success']}/{stats['plugin']['total']} ✅"
            if stats["plugin"]["success"] == stats["plugin"]["total"]
            else f"Plugins:   {stats['plugin']['success']}/{stats['plugin']['total']} ❌"
        )

    if skills:
        print(
            f"Skills:    {stats['skill']['success']}/{stats['skill']['total']} ✅"
            if stats["skill"]["success"] == stats["skill"]["total"]
            else f"Skills:    {stats['skill']['success']}/{stats['skill']['total']} ❌"
        )

    print(
        f"Git Hooks: {stats['git_hooks']['success']}/{stats['git_hooks']['total']} ✅"
        if stats["git_hooks"]["success"] == stats["git_hooks"]["total"]
        else f"Git Hooks: {stats['git_hooks']['success']}/{stats['git_hooks']['total']} ❌"
    )

    total_success = stats["plugin"]["success"] + stats["skill"]["success"] + stats["git_hooks"]["success"]
    total_count = stats["plugin"]["total"] + stats["skill"]["total"] + stats["git_hooks"]["total"]

    print("=" * 60)

    if total_success == total_count:
        print("✅ 所有依赖安装成功！")
        sys.exit(0)
    else:
        print(f"⚠️  部分依赖安装失败 ({total_success}/{total_count})")
        sys.exit(1)


if __name__ == "__main__":
    main()
