#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post Tool Use Hook

Write 或 Edit 工具使用后自动运行的检查脚本。
执行类型检查、代码规范检查和相关测试。

在 Claude Code 中通过 settings.local.json 的 PostToolUse 自动触发；
在 OpenCode、Cursor、Codex、Antigravity 等无该 hook 的平台可手动执行。

使用方法:
    python post-tool-use.py <tool> <file_path>
    # tool: Write 或 Edit
    # file_path: 被写入或编辑的文件路径（相对项目根）

兼容：Windows / macOS / Linux
"""

import subprocess
import sys
import os
import io
import json
from pathlib import Path
from typing import Optional

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def get_file_extension(file_path: str) -> str:
    """获取文件扩展名"""
    return Path(file_path).suffix.lower()


def is_typescript_file(file_path: str) -> bool:
    """判断是否为 TypeScript 文件"""
    ext = get_file_extension(file_path)
    return ext in ['.ts', '.tsx', '.vue']


def is_python_file(file_path: str) -> bool:
    """判断是否为 Python 文件"""
    return get_file_extension(file_path) == '.py'


def is_source_file(file_path: str) -> bool:
    """判断是否为需要检查的源文件"""
    return is_typescript_file(file_path) or is_python_file(file_path)


def run_command(cmd: list[str], cwd: Optional[str] = None, timeout: int = 60) -> tuple[int, str, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd(),
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, '', 'Command timed out'
    except FileNotFoundError:
        return -1, '', f'Command not found: {cmd[0]}'


def find_tsconfigs() -> list[Path]:
    """查找项目中的 tsconfig.json（根目录、server、client）"""
    candidates = [
        Path('tsconfig.json'),
        Path('server/tsconfig.json'),
        Path('client/tsconfig.json'),
    ]
    return [p for p in candidates if p.exists()]


def type_check() -> bool:
    """运行 TypeScript 类型检查"""
    print('   🔍 类型检查中...')

    tsconfigs = find_tsconfigs()
    if not tsconfigs:
        print('      ⚠️  未找到 tsconfig.json，跳过')
        return True

    all_passed = True
    for tsconfig in tsconfigs:
        cwd = str(tsconfig.parent) if tsconfig.parent != Path('.') else None
        label = cwd or '根目录'
        returncode, stdout, stderr = run_command(
            ['npx', 'tsc', '--noEmit', '--pretty'],
            cwd=cwd
        )
        if returncode == 0:
            print(f'      ✅ 类型检查通过 ({label})')
        else:
            print(f'      ❌ 类型检查失败 ({label})')
            if stderr:
                print(stderr[:500])
            all_passed = False

    return all_passed


def lint_check(file_path: str, auto_fix: bool = False) -> bool:
    """运行 ESLint 检查"""
    print(f'   📏 代码规范检查中...')

    eslint_configs = [
        '.eslintrc', '.eslintrc.js', '.eslintrc.cjs', '.eslintrc.json',
        'eslint.config.js', 'eslint.config.mjs', 'eslint.config.ts',
    ]
    has_eslint = False
    for base in ['', 'server/', 'client/']:
        if any((Path(base) / config).exists() for config in eslint_configs):
            has_eslint = True
            break

    if not has_eslint:
        print('      ⚠️  ESLint 配置不存在，跳过')
        return True

    cmd = ['npx', 'eslint', file_path, '--max-warnings', '0']
    if auto_fix:
        cmd.insert(3, '--fix')

    returncode, stdout, stderr = run_command(cmd)

    if returncode == 0:
        print('      ✅ 代码规范检查通过')
        return True
    else:
        print('      ❌ 代码规范检查失败')
        if stdout:
            print(stdout[:500])
        return False


def run_related_tests(file_path: str) -> bool:
    """运行相关测试"""
    print(f'   🧪 运行相关测试...')

    vitest_configs = [
        Path('vitest.config.ts'), Path('vitest.config.js'),
        Path('server/vitest.config.ts'), Path('server/vitest.config.js'),
        Path('client/vitest.config.ts'), Path('client/vitest.config.js'),
    ]
    if not any(p.exists() for p in vitest_configs):
        print('      ⚠️  Vitest 配置不存在，跳过')
        return True

    path = Path(file_path)
    test_paths = []

    # 模式 1: 同目录下的 .test.ts
    test_paths.append(path.parent / f'{path.stem}.test{path.suffix}')

    # 模式 2: server/tests、client/tests 或 tests/unit 下的对应测试
    for prefix in ['server/src', 'client/src', 'src']:
        prefix_path = Path(prefix)
        try:
            relative = path.relative_to(prefix_path)
            base = prefix.split('/')[0] if '/' in prefix else ''
            test_dir = Path(base) / 'tests' if base else Path('tests')
            test_paths.append(
                test_dir / 'unit' / str(relative).replace(path.suffix, f'.test{path.suffix}')
            )
            break
        except ValueError:
            continue

    test_file = None
    for tp in test_paths:
        if tp.exists():
            test_file = str(tp)
            break

    if not test_file:
        print('      ⚠️  未找到相关测试文件，跳过')
        return True

    # 若测试文件在 server/ 或 client/ 下，则在该子目录执行 vitest
    vitest_cwd = None
    if test_file.startswith('server/'):
        vitest_cwd = 'server'
    elif test_file.startswith('client/'):
        vitest_cwd = 'client'

    returncode, stdout, stderr = run_command(
        ['npx', 'vitest', 'run', test_file, '--reporter=verbose'],
        timeout=120,
        cwd=vitest_cwd
    )

    if returncode == 0:
        print('      ✅ 测试通过')
        return True
    else:
        print('      ❌ 测试失败')
        if stdout:
            print(stdout[:500])
        return False


def python_syntax_check(file_path: str) -> bool:
    """Python 语法检查"""
    print(f'   🐍 Python 语法检查...')

    returncode, stdout, stderr = run_command(['python', '-m', 'py_compile', file_path])

    if returncode == 0:
        print('      ✅ 语法检查通过')
        return True
    else:
        print('      ❌ 语法检查失败')
        if stderr:
            print(stderr[:500])
        return False


def check_git_diff(file_path: str) -> None:
    """检查文件变更（仅 Edit 操作）"""
    print(f'   📝 文件变更预览...')

    returncode, stdout, stderr = run_command(['git', 'diff', file_path])

    if returncode == 0 and stdout:
        lines = stdout.split('\n')[:10]
        for line in lines:
            print(f'      {line}')
        if len(stdout.split('\n')) > 10:
            print('      ... (更多变更省略)')


def write_error_marker(has_errors: bool) -> None:
    """写入错误标记文件，供 /fix agent 读取"""
    error_file = Path('.ai-engineer') / 'errors.json'
    error_file.parent.mkdir(exist_ok=True)

    if has_errors:
        error_file.write_text(json.dumps({"has_errors": True, "timestamp": str(Path(__file__).stat().st_mtime)}))
    else:
        if error_file.exists():
            error_file.unlink()


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print('用法: post-tool-use.py <tool> <file_path>')
        sys.exit(0)

    tool = sys.argv[1]
    file_path = sys.argv[2]

    # 只处理源文件
    if not is_source_file(file_path):
        sys.exit(0)

    # 跳过测试文件本身
    if '.test.' in file_path or '.spec.' in file_path:
        sys.exit(0)

    # 跳过 .claude 目录下的文件（避免递归）
    if '.claude' in file_path:
        sys.exit(0)

    tool_name = '写入' if tool == 'Write' else '编辑'
    print(f'\n📄 文件{tool_name}完成: {file_path}')
    print('   ' + '=' * 40)

    all_passed = True
    auto_fix = (tool == 'Edit')  # Edit 时尝试自动修复

    # 根据文件类型执行不同检查
    if is_typescript_file(file_path):
        if not type_check():
            all_passed = False

        if not lint_check(file_path, auto_fix):
            all_passed = False

        if not run_related_tests(file_path):
            all_passed = False

    elif is_python_file(file_path):
        if not python_syntax_check(file_path):
            all_passed = False

    # Edit 操作时显示变更预览
    if tool == 'Edit':
        check_git_diff(file_path)

    print('   ' + '=' * 40)

    if all_passed:
        print('   ✅ 所有检查通过')
    else:
        print('   ❌ 存在问题，可能需要 /fix 修复')

    # 写入错误标记
    write_error_marker(not all_passed)

    # Hook 不应该阻止操作，只做记录
    sys.exit(0)


if __name__ == '__main__':
    main()
