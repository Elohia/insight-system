#!/usr/bin/env python3
"""
洞见Hook - 对话开始时自动调用
使用三层记忆系统：模糊层(启动) / 精确层(按需) / 深度层(按需)
"""

import os
import sys
import json
import re
from pathlib import Path

# 添加项目根目录到路径
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / "utils"))
sys.path.insert(0, str(script_dir / "core"))

# 导入配置加载器
from utils.config_loader import get_config, get_state_file

# 获取配置
_config = get_config()
STATE_FILE = str(_config.state_file)

# 导入三层记忆系统
try:
    from three_layer_memory import ThreeLayerMemory, get_startup_context, get_context_by_need
    THREE_LAYER_AVAILABLE = True
except ImportError:
    THREE_LAYER_AVAILABLE = False
    print("⚠️ 三层记忆系统未加载")


def get_relevant_insights(query, top_k=3):
    """获取与查询相关的洞见"""
    if not os.path.exists(STATE_FILE):
        return []
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    insights = [i for i in state.get("insights", []) if i.get("type") == "insight"]
    
    if not insights:
        return []
    
    # 简单的关键词匹配
    query_words = set(re.findall(r'[\w\u4e00-\u9fff]+', query.lower()))
    
    scored = []
    for insight in insights:
        insight_text = insight.get("insight_text", "")
        insight_words = set(re.findall(r'[\w\u4e00-\u9fff]+', insight_text.lower()))
        
        # 计算重叠
        overlap = len(query_words & insight_words)
        if overlap > 0:
            scored.append((overlap, insight))
    
    # 按重叠度排序
    scored.sort(key=lambda x: x[0], reverse=True)
    
    return [s[1] for s in scored[:top_k]]


def get_recent_insights(n=5):
    """获取最近的洞见（优先高质量）"""
    if not os.path.exists(STATE_FILE):
        return []
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    insights = [i for i in state.get("insights", []) if i.get("type") == "insight"]
    
    # 优先返回有追问的高质量洞见
    with_questions = [i for i in insights if i.get("follow_up_question")]
    without_questions = [i for i in insights if not i.get("follow_up_question")]
    
    # 组合：先返回有追问的，再返回其他的
    result = with_questions + without_questions
    return result[:n]


def get_unanswered_questions():
    """获取未回答的追问"""
    if not os.path.exists(STATE_FILE):
        return []
    
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)
    
    questions = []
    for insight in state.get("insights", []):
        if insight.get("type") == "insight" and insight.get("follow_up_question"):
            questions.append({
                "question": insight["follow_up_question"],
                "related_insight": insight.get("insight_text", "")[:50]
            })
    
    return questions[:3]


def format_for_context(insights):
    """格式化洞见供对话上下文使用"""
    if not insights:
        return ""
    
    lines = ["🧠 相关洞见:"]
    for i in insights:
        text = i.get("insight_text", "")
        follow_up = i.get("follow_up_question", "")
        lines.append(f"  • {text}")
        if follow_up:
            lines.append(f"    ❓ {follow_up}")
    
    return "\n".join(lines)


def get_startup_memory() -> str:
    """获取启动时的记忆上下文（只加载模糊层）"""
    if THREE_LAYER_AVAILABLE:
        return get_startup_context()
    
    # 降级：使用旧版洞见加载
    insights = get_recent_insights(5)
    if insights:
        return format_for_context(insights)
    return ""


def get_memory_by_query(query: str, layer: str = "precise") -> str:
    """按需获取记忆
    
    Args:
        query: 查询内容
        layer: "precise" 或 "deep"
    """
    if THREE_LAYER_AVAILABLE:
        if layer == "precise":
            return get_context_by_need("precise", query=query)
        elif layer == "deep":
            # 从查询提取关键词
            keywords = re.findall(r'[\w\u4e00-\u9fff]+', query)[:5]
            return get_context_by_need("deep", keywords=keywords)
    
    # 降级：使用旧版搜索
    insights = get_relevant_insights(query)
    if insights:
        return format_for_context(insights)
    return ""


def get_reverse_prompt() -> str:
    """反向提示：主动提出用户没想到的问题
    
    参考: proactive-agent Reverse Prompting
    不等待用户提问，主动提供价值
    """
    prompts = []
    
    # 1. 检查未回答的问题
    questions = get_unanswered_questions()
    if questions:
        prompts.append(f"💭 上次留下的问题: {questions[0]['question']}")
    
    # 2. 检查 working buffer 中的待处理内容
    if THREE_LAYER_AVAILABLE:
        try:
            memory = ThreeLayerMemory()
            fuzzy = memory.load_fuzzy_layer()
            buffer = fuzzy.get("working_buffer", [])
            if buffer:
                prompts.append(f"📝 Working Buffer 中有 {len(buffer)} 条未处理内容")
        except:
            pass
    
    # 3. 检查是否需要更新模糊层
    if THREE_LAYER_AVAILABLE:
        try:
            memory = ThreeLayerMemory()
            if memory.should_update_fuzzy():
                prompts.append("🔄 模糊层已过期，建议更新")
        except:
            pass
    
    # 4. 从洞见中提取反向提示
    if not prompts:
        insights = get_recent_insights(3)
        for i in insights:
            follow_up = i.get("follow_up_question", "")
            if follow_up:
                prompts.append(f"💡 值得思考的问题: {follow_up}")
                break
    
    if prompts:
        return "\n\n🎯 反向提示:\n" + "\n".join(f"  {p}" for p in prompts[:2])
    
    return ""


def main():
    """主函数 - 用于命令行调用
    
    启动模式 (--startup): 只加载模糊层
    精确模式 (--precise + query): 加载精确层
    深度模式 (--deep + keywords): 加载深度层
    """
    if THREE_LAYER_AVAILABLE:
        # 使用三层记忆系统
        if "--startup" in sys.argv:
            # 启动模式：只加载模糊层
            context = get_startup_context()
            if context:
                print("🔮 模糊层已加载:")
                print(context)
            else:
                print("⚠️ 模糊层为空")
            
            # 添加反向提示
            reverse_prompt = get_reverse_prompt()
            if reverse_prompt:
                print(reverse_prompt)
            
            return
        
        if "--precise" in sys.argv:
            # 精确模式：按查询加载精确层
            query_idx = sys.argv.index("--precise") + 1
            query = " ".join(sys.argv[query_idx:]) if query_idx < len(sys.argv) else ""
            context = get_context_by_need("precise", query=query)
            if context:
                print(context)
            else:
                print("未找到相关洞见")
            return
        
        if "--deep" in sys.argv:
            # 深度模式：按关键词加载深度层
            kw_idx = sys.argv.index("--deep") + 1
            keywords = sys.argv[kw_idx:] if kw_idx < len(sys.argv) else None
            context = get_context_by_need("deep", keywords=keywords)
            if context:
                print(context)
            else:
                print("未找到相关记忆")
            return
        
        if "--update-fuzzy" in sys.argv:
            # 更新模糊层
            from three_layer_memory import update_fuzzy_layer
            fuzzy = update_fuzzy_layer()
            print(f"✅ 模糊层已更新，估算 {fuzzy['stats']['token_estimate']} tokens")
            return
    
    # 默认模式：显示最近的洞见（兼容旧版）
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        # 搜索模式
        query = " ".join(sys.argv[1:])
        insights = get_relevant_insights(query)
        if insights:
            print(format_for_context(insights))
        else:
            print("未找到相关洞见")
    else:
        # 显示最近的洞见
        insights = get_recent_insights()
        if insights:
            print("🧠 最近洞见:")
            for i in insights:
                print(f"  • {i.get('insight_text', 'N/A')[:50]}...")
        
        # 显示未回答的问题
        questions = get_unanswered_questions()
        if questions:
            print("\n❓ 待思考的问题:")
            for q in questions:
                print(f"  • {q['question']}")
                print(f"    (关联: {q['related_insight']})")


if __name__ == "__main__":
    main()
