#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre Commit Hook

git commit 前自动运行的检查脚本。
确保提交的代码符合质量标准。

兼容：Windows / macOS / Linux
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Optional


def run_command(cmd: list[str], cwd: Optional[str] = None) -> tuple[int, str, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or os.getcwd(),
            timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, '', 'Command timed out'
    except FileNotFoundError:
        return -1, '', f'Command not found: {cmd[0]}'


def get_staged_files() -> list[str]:
    """获取暂存的文件列表"""
    returncode, stdout, stderr = run_command(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM']
    )

    if returncode != 0:
        return []

    return [f for f in stdout.strip().split('\n') if f]


def filter_files(files: list[str], extensions: list[str]) -> list[str]:
    """按扩展名过滤文件"""
    return [
        f for f in files
        if any(f.endswith(ext) for ext in extensions)
    ]


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
    print('🔍 类型检查中...')

    tsconfigs = find_tsconfigs()
    if not tsconfigs:
        print('   ⚠️  未找到 tsconfig.json，跳过')
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
            print(f'   ✅ 类型检查通过 ({label})')
        else:
            print(f'   ❌ 类型检查失败 ({label})')
            if stderr:
                print(stderr)
            all_passed = False

    return all_passed


def lint_check(files: list[str]) -> bool:
    """运行 ESLint 检查"""
    print(f'📏 代码规范检查中... ({len(files)} 个文件)')

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
        print('   ⚠️  ESLint 配置不存在，跳过')
        return True

    returncode, stdout, stderr = run_command(
        ['npx', 'eslint'] + files + ['--max-warnings', '0']
    )

    if returncode == 0:
        print('   ✅ 代码规范检查通过')
        return True
    else:
        print('   ❌ 代码规范检查失败')
        if stdout:
            print(stdout)
        return False


def run_tests() -> bool:
    """运行测试"""
    print('🧪 运行测试...')

    if not Path('vitest.config.ts').exists() and not Path('vitest.config.js').exists():
        print('   ⚠️  Vitest 配置不存在，跳过')
        return True

    returncode, stdout, stderr = run_command(
        ['npx', 'vitest', 'run', '--reporter=verbose']
    )

    if returncode == 0:
        # 解析测试结果
        print('   ✅ 所有测试通过')
        return True
    else:
        print('   ❌ 测试失败')
        if stdout:
            print(stdout)
        return False


def check_coverage() -> bool:
    """检查测试覆盖率"""
    print('📊 检查覆盖率...')

    if not Path('vitest.config.ts').exists() and not Path('vitest.config.js').exists():
        print('   ⚠️  Vitest 配置不存在，跳过')
        return True

    returncode, stdout, stderr = run_command(
        ['npx', 'vitest', 'run', '--coverage', '--reporter=json']
    )

    # 尝试读取覆盖率报告
    coverage_file = Path('coverage') / 'coverage-summary.json'
    if coverage_file.exists():
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                coverage = json.load(f)

            line_coverage = coverage.get('total', {}).get('lines', {}).get('pct', 0)

            if line_coverage >= 90:
                print(f'   ✅ 覆盖率: {line_coverage}%')
                return True
            else:
                print(f'   ❌ 覆盖率不足: {line_coverage}% (要求 ≥90%)')
                return False
        except (json.JSONDecodeError, KeyError):
            print('   ⚠️  无法解析覆盖率报告')
            return True
    else:
        print('   ⚠️  覆盖率报告不存在，跳过检查')
        return True


def check_secrets(files: list[str]) -> bool:
    """检查是否包含敏感信息"""
    print('🔐 检查敏感信息...')

    suspicious_patterns = [
        'api_key',
        'secret',
        'password',
        'token',
        'credential',
        'private_key',
    ]

    found_issues = []

    for file_path in files:
        if not Path(file_path).exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            for pattern in suspicious_patterns:
                if pattern in content:
                    # 检查是否是硬编码的值（而不是环境变量引用）
                    if '=' in content and 'process.env' not in content:
                        found_issues.append(f'{file_path}: 可能包含 {pattern}')
        except UnicodeDecodeError:
            # 二进制文件，跳过
            continue

    if found_issues:
        print('   ⚠️  发现可能的敏感信息:')
        for issue in found_issues:
            print(f'      - {issue}')
        print('   请确保使用环境变量而非硬编码')
        return False
    else:
        print('   ✅ 未发现敏感信息')
        return True


def main():
    """主函数"""
    print('\n🚀 Pre-commit 检查开始')
    print('=' * 50)

    # 获取暂存的文件
    staged_files = get_staged_files()

    if not staged_files:
        print('没有暂存的文件需要检查')
        sys.exit(0)

    print(f'📦 暂存文件数: {len(staged_files)}')

    # 分类文件
    ts_files = filter_files(staged_files, ['.ts', '.tsx', '.vue'])
    py_files = filter_files(staged_files, ['.py'])

    all_passed = True

    # TypeScript 检查
    if ts_files:
        print(f'\n📝 TypeScript 文件: {len(ts_files)} 个')

        if not type_check():
            all_passed = False

        if not lint_check(ts_files):
            all_passed = False

        if not run_tests():
            all_passed = False

        if not check_coverage():
            all_passed = False

    # Python 检查
    if py_files:
        print(f'\n🐍 Python 文件: {len(py_files)} 个')

        for py_file in py_files:
            returncode, _, stderr = run_command(['python', '-m', 'py_compile', py_file])
            if returncode != 0:
                print(f'   ❌ {py_file}: 语法错误')
                print(stderr)
                all_passed = False

        if all_passed:
            print('   ✅ 所有 Python 文件语法正确')

    # 安全检查
    if not check_secrets(staged_files):
        all_passed = False

    print('\n' + '=' * 50)

    if all_passed:
        print('✅ 所有检查通过，可以提交')
        sys.exit(0)
    else:
        print('❌ 检查未通过，请修复后再提交')
        print('\n提示: 使用 git commit --no-verify 可跳过检查（不推荐）')
        sys.exit(1)


if __name__ == '__main__':
    main()
