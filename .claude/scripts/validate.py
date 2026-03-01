#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档校验脚本

校验需求文档和宪法文档的完整性。

**需求文档严格校验的原因**：确保下游阶段（/fi-plan 架构、/contract 类型、/fi-test 测试）
拿到的输入具备必备字段（项目名称、目标、核心功能、验收标准等），避免「残缺需求 → 架构空泛
→ 合同/测试/实现连锁偏差」。校验在 /fi-init 生成需求后自动执行，不通过则提示补全再继续。

使用方法:
    python validate.py requirement     # 校验需求文档
    python validate.py constitution    # 校验宪法文档
    python validate.py all             # 校验所有

兼容：Windows / macOS / Linux
"""

import sys
import re
import io
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 路径配置
BASE_DIR = Path(__file__).parent.parent.parent
REQUIREMENT_FILE = BASE_DIR / "docs" / "requirements.md"
CONSTITUTION_FILE = BASE_DIR / ".claude" / "shared-references" / "constitution.md"


def parse_markdown_to_dict(content: str) -> dict:
    """将 markdown 内容解析为字典结构（简化版）"""
    result = {
        "project": {},
        "features": [],
        "nonFunctional": {},
        "boundaries": {},
        "acceptance": [],
    }

    lines = content.split("\n")
    current_section = None
    current_feature = None

    for line in lines:
        line = line.strip()

        # 检测章节标题
        if line.startswith("## "):
            section_title = line[3:].lower()
            if "项目信息" in section_title or "project" in section_title:
                current_section = "project"
            elif "核心功能" in section_title or "功能" in section_title:
                current_section = "features"
            elif "非功能" in section_title:
                current_section = "nonFunctional"
            elif "边界" in section_title:
                current_section = "boundaries"
            elif "验收" in section_title:
                current_section = "acceptance"
            else:
                current_section = None

        # 检测子标题（功能）
        elif line.startswith("### 功能") or line.startswith("### "):
            if current_section == "features":
                feature_name = line.replace("### ", "").replace("功能 ", "").strip()
                current_feature = {"name": feature_name, "description": "", "priority": "should"}
                result["features"].append(current_feature)

        # 解析内容
        elif current_section == "project":
            if line.startswith("**") and line.endswith("**"):
                pass
            elif ":" in line or "：" in line:
                parts = re.split(r"[:：]", line, maxsplit=1)
                if len(parts) == 2:
                    key = parts[0].replace("*", "").strip()
                    value = parts[1].strip()
                    if "名称" in key:
                        result["project"]["name"] = value
                    elif "目标" in key:
                        result["project"]["goal"] = value
                    elif "类型" in key:
                        result["project"]["type"] = value

        elif current_section == "features" and current_feature:
            if line.startswith("**描述") and (":" in line or "：" in line):
                parts = re.split(r"[:：]", line, maxsplit=1)
                if len(parts) > 1:
                    current_feature["description"] = parts[1].strip()
            elif line.startswith("**优先级") and (":" in line or "：" in line):
                parts = re.split(r"[:：]", line, maxsplit=1)
                if len(parts) > 1:
                    current_feature["priority"] = parts[1].strip()

        elif current_section == "acceptance":
            if line.startswith("- [ ]") or line.startswith("- [x]"):
                criterion = line.replace("- [ ]", "").replace("- [x]", "").strip()
                result["acceptance"].append({"criterion": criterion})

    return result


def validate_requirement() -> bool:
    """校验需求文档"""
    print("\n📋 校验需求文档...")

    if not REQUIREMENT_FILE.exists():
        print(f"   ❌ 需求文档不存在: {REQUIREMENT_FILE}")
        return False

    with open(REQUIREMENT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    if len(content.strip()) < 100:
        print("   ⚠️  需求文档内容过少，可能未填写完整")
        return False

    data = parse_markdown_to_dict(content)
    errors = []

    if not data["project"].get("name"):
        errors.append("缺少项目名称")
    if not data["project"].get("goal"):
        errors.append("缺少项目目标")
    if not data["features"]:
        errors.append("缺少核心功能")
    if not data["acceptance"]:
        errors.append("缺少验收标准")

    if errors:
        print("   ❌ 校验失败:")
        for error in errors:
            print(f"      - {error}")
        return False

    print("   ✅ 需求文档校验通过")
    return True


def validate_constitution() -> bool:
    """校验宪法文档"""
    print("\n📜 校验工程宪法...")

    if not CONSTITUTION_FILE.exists():
        print(f"   ❌ 宪法文档不存在: {CONSTITUTION_FILE}")
        return False

    with open(CONSTITUTION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    required_sections = [
        "类型安全",
        "函数设计",
        "模块设计",
        "错误处理",
        "测试",
    ]

    errors = []
    for section in required_sections:
        if section not in content:
            errors.append(f"缺少章节: {section}")

    if errors:
        print("   ❌ 校验失败:")
        for error in errors:
            print(f"      - {error}")
        return False

    print("   ✅ 工程宪法校验通过")
    return True


def validate_all() -> bool:
    """校验所有文档"""
    print("=" * 50)
    print("🔍 文档校验")
    print("=" * 50)

    results = {
        "requirement": validate_requirement(),
        "constitution": validate_constitution(),
    }

    print("\n" + "=" * 50)
    print("📊 校验结果")
    print("=" * 50)

    all_passed = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)
    return all_passed


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python validate.py <requirement|constitution|all>")
        print("\n示例:")
        print("  python validate.py requirement   # 校验需求文档")
        print("  python validate.py constitution  # 校验宪法文档")
        print("  python validate.py all           # 校验所有")
        sys.exit(1)

    target = sys.argv[1].lower()

    if target == "requirement":
        success = validate_requirement()
    elif target == "constitution":
        success = validate_constitution()
    elif target == "all":
        success = validate_all()
    else:
        print(f"❌ 未知的校验目标: {target}")
        print("   支持的目标: requirement, constitution, all")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
