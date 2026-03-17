#!/usr/bin/env python3
"""
AI 自我驱动核心 - 自动运行碰撞引擎
定期执行任务：更新模糊层、运行碰撞引擎、生成摘要
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目路径
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# 导入配置模块
try:
    from core.config import (
        get_openclaw_home,
        get_memory_dir,
        get_insight_state_file,
        get_fuzzy_layer_file,
    )
except ImportError:
    # 回退到直接定义
    def get_openclaw_home():
        return os.getenv("OPENCLAW_HOME", str(Path.home() / ".openclaw"))

    def get_memory_dir():
        return str(Path(get_openclaw_home()) / "workspace" / "memory")

    def get_insight_state_file():
        return str(Path(get_openclaw_home()) / "insight-state.json")

    def get_fuzzy_layer_file():
        return str(Path(get_openclaw_home()) / "memory-fuzzy-layer.json")


def update_fuzzy_layer():
    """更新模糊层"""
    print("🔮 更新模糊层...")

    try:
        from core.three_layer_memory import ThreeLayerMemory

        memory = ThreeLayerMemory()
        memory.fuzzy_layer = memory.generate_fuzzy_layer()
        print(f"✅ 模糊层已更新 ({memory.fuzzy_layer.get('stats', {}).get('token_estimate', 0)} tokens)")
        return True

    except ImportError:
        # 如果三层记忆模块不可用，尝试简单的更新
        print("⚠️ 三层记忆模块不可用，跳过模糊层更新")
        return False
    except Exception as e:
        print(f"❌ 模糊层更新失败: {e}")
        return False


def run_collider():
    """运行碰撞引擎"""
    print("⚡ 运行碰撞引擎...")

    try:
        # 添加 collider 路径
        collider_path = script_dir / "collider"
        if str(collider_path) not in sys.path:
            sys.path.insert(0, str(collider_path))

        from collider.engine import analyze_patterns

        results = analyze_patterns()

        if results:
            print(f"✅ 碰撞引擎完成，发现 {len(results)} 个新洞见")
            for r in results:
                print(f"  💡 {r.get('insight', '')[:50]}... (置信度: {r.get('confidence', 0):.2f})")
        else:
            print("ℹ️ 碰撞引擎完成，未发现新洞见")

        return True

    except ImportError as e:
        print(f"⚠️ 碰撞引擎模块不可用: {e}")
        return False
    except Exception as e:
        print(f"❌ 碰撞引擎运行失败: {e}")
        return False


def run_workflow_learner():
    """运行工作流学习"""
    print("📚 运行工作流学习...")

    try:
        from core.workflow_learner import WorkflowLearner

        learner = WorkflowLearner()
        analysis = learner.analyze_sessions(days=7)

        if "error" not in analysis:
            print(f"✅ 工作流分析完成，分析了 {analysis.get('total_sessions', 0)} 个会话")

            # 输出自动化建议
            suggestions = learner.suggest_automation()
            if suggestions:
                print("📋 自动化建议:")
                for s in suggestions[:2]:
                    print(f"  {s[:100]}...")
        else:
            print(f"ℹ️ 工作流分析: {analysis.get('error')}")

        return True

    except ImportError:
        print("⚠️ 工作流学习模块不可用，跳过")
        return False
    except Exception as e:
        print(f"❌ 工作流学习失败: {e}")
        return False


def generate_summary():
    """生成运行摘要"""
    print("\n" + "=" * 50)
    print("📊 AI 自我驱动摘要")
    print("=" * 50)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "openclaw_home": get_openclaw_home(),
    }

    # 检查文件状态
    state_file = get_insight_state_file()
    fuzzy_file = get_fuzzy_layer_file()

    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            insights_count = len(state.get("insights", []))
            summary["insights_count"] = insights_count
            print(f"📝 洞见总数: {insights_count}")
        except Exception as e:
            print(f"⚠️ 读取状态文件失败: {e}")
    else:
        print("ℹ️ 尚未有洞见记录")

    if os.path.exists(fuzzy_file):
        try:
            with open(fuzzy_file, 'r') as f:
                fuzzy = json.load(f)
            token_est = fuzzy.get("stats", {}).get("token_estimate", 0)
            summary["fuzzy_layer_tokens"] = token_est
            print(f"🔮 模糊层 tokens: {token_est}")
        except Exception as e:
            print(f"⚠️ 读取模糊层失败: {e}")

    print("=" * 50)

    return summary


def auto_drive(enable_collider: bool = True, enable_workflow: bool = False):
    """
    自我驱动主函数

    Args:
        enable_collider: 是否运行碰撞引擎
        enable_workflow: 是否运行工作流学习
    """
    print("🧠 开始 AI 自我驱动...")
    print(f"⏰ 时间: {datetime.now().isoformat()}")
    print(f"📁 OpenClaw: {get_openclaw_home()}")
    print()

    results = {
        "fuzzy_layer": update_fuzzy_layer(),
        "collider": run_collider() if enable_collider else None,
        "workflow": run_workflow_learner() if enable_workflow else None,
    }

    summary = generate_summary()
    results["summary"] = summary

    # 保存运行日志
    log_dir = Path(get_openclaw_home()) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "auto_drive.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now().isoformat()}] 自我驱动完成: ")
        f.write(json.dumps(results, ensure_ascii=False, indent=2))

    print("\n✅ 自我驱动完成")

    return results


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="AI 自我驱动")
    parser.add_argument("--no-collider", action="store_true", help="跳过碰撞引擎")
    parser.add_argument("--workflow", action="store_true", help="启用工作流学习")
    parser.add_argument("--dry-run", action="store_true", help="只显示将要执行的操作")

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 dry-run 模式")
        print(f"  模糊层更新: 是")
        print(f"  碰撞引擎: {'否' if args.no_collider else '是'}")
        print(f"  工作流学习: {'是' if args.workflow else '否'}")
        print(f"\n📁 OpenClaw: {get_openclaw_home()}")
        return

    auto_drive(
        enable_collider=not args.no_collider,
        enable_workflow=args.workflow
    )


if __name__ == "__main__":
    main()
