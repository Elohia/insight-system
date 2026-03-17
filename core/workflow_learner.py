#!/usr/bin/env python3
"""
工作流学习与自动化模块
AI 自动学习用户的工作流程并优化
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from collections import Counter

# 尝试导入 config
try:
    from config import get_workflows_file, get_memory_dir
except ImportError:
    def get_workflows_file() -> str:
        return str(Path.home() / ".openclaw" / "workflows.json")

    def get_memory_dir() -> str:
        return str(Path.home() / ".openclaw" / "workspace" / "memory")


@dataclass
class WorkflowStep:
    """工作流步骤"""
    step_id: str
    action: str
    tool: Optional[str] = None
    args: Optional[dict] = None
    description: Optional[str] = None


@dataclass
class Workflow:
    """工作流"""
    id: str
    name: str
    description: str
    trigger_patterns: List[str]  # 触发这个工作流的用户指令模式
    steps: List[WorkflowStep]
    frequency: int = 0  # 执行频率
    last_used: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)


class WorkflowLearner:
    """工作流学习器"""

    def __init__(self):
        self.workflows: List[Workflow] = []
        self.load_workflows()

    def load_workflows(self):
        """从文件加载工作流"""
        workflows_file = Path(get_workflows_file())

        if workflows_file.exists():
            try:
                with open(workflows_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for w in data.get("workflows", []):
                        steps = [WorkflowStep(**s) for s in w.get("steps", [])]
                        w["steps"] = steps
                        self.workflows.append(Workflow(**w))
            except Exception as e:
                print(f"加载工作流失败: {e}")
                self.workflows = []

    def save_workflows(self):
        """保存工作流到文件"""
        workflows_file = Path(get_workflows_file())

        # 确保目录存在
        workflows_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "workflows": [asdict(w) for w in self.workflows],
            "last_updated": datetime.now().isoformat(),
        }

        with open(workflows_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _extract_intent(self, message: str) -> str:
        """
        从消息中提取意图

        Args:
            message: 用户消息

        Returns:
            意图字符串
        """
        message = message.lower()

        # 定义意图模式
        intent_patterns = {
            "search": r"(搜索?|查找?|google|百度|查询)\s+",
            "read_file": r"(读取?|打开|查看|看)\s+.*文件",
            "write_file": r"(写入?|创建|新建|写)\s+.*文件",
            "code": r"(写代码|debug|调试|编程|开发)",
            "run_command": r"(运行?|执行|跑)\s+.*命令",
            "analyze": r"(分析?|研究?|调研)",
            "summarize": r"(总结?|概括?|汇总)",
            "translate": r"(翻译?|转换)",
            "post_social": r"(发布|发|分享)\s+.*(微博|推特|twitter|微信)",
        }

        for intent, pattern in intent_patterns.items():
            if re.search(pattern, message):
                return intent

        return "general"

    def _generate_workflow_id(self) -> str:
        """生成唯一的工作流 ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"workflow_{timestamp}"

    def learn_from_interaction(self, messages: List[Dict[str, Any]]) -> Optional[Workflow]:
        """
        从交互中学习工作流

        Args:
            messages: 对话消息列表

        Returns:
            学习到的工作流（如果有新模式）
        """
        if not messages:
            return None

        # 提取用户消息
        user_messages = [m.get("content", "") for m in messages if m.get("role") == "user"]
        assistant_messages = [m.get("content", "") for m in messages if m.get("role") == "assistant"]

        if not user_messages:
            return None

        # 分析用户指令模式
        intents = [self._extract_intent(msg) for msg in user_messages]
        intent_counter = Counter(intents)

        # 如果某个意图出现多次，可能是可复用的工作流
        most_common_intent, count = intent_counter.most_common(1)[0]

        if count < 2:
            return None  # 出现次数太少，不足以形成工作流

        # 检查是否已存在类似工作流
        existing = [w for w in self.workflows if most_common_intent in w.trigger_patterns]
        if existing:
            # 更新现有工作流的频率
            for w in existing:
                w.frequency += 1
                w.last_used = datetime.now().isoformat()
            self.save_workflows()
            return None

        # 创建新工作流
        workflow = Workflow(
            id=self._generate_workflow_id(),
            name=f"{most_common_intent} 工作流",
            description=f"自动学习的工作流：{most_common_intent}",
            trigger_patterns=[most_common_intent],
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    action=most_common_intent,
                    description=f"执行 {most_common_intent} 操作"
                )
            ],
            frequency=count,
            tags=[most_common_intent]
        )

        self.workflows.append(workflow)
        self.save_workflows()

        return workflow

    def find_matching_workflow(self, query: str) -> Optional[Workflow]:
        """
        查找匹配的工作流

        Args:
            query: 用户查询

        Returns:
            匹配的工作流（如果有）
        """
        query_lower = query.lower()

        for workflow in self.workflows:
            for pattern in workflow.trigger_patterns:
                if pattern in query_lower:
                    # 更新使用统计
                    workflow.frequency += 1
                    workflow.last_used = datetime.now().isoformat()
                    self.save_workflows()
                    return workflow

        return None

    def get_automatable_workflows(self) -> List[Workflow]:
        """
        获取可自动化的工作流建议

        Returns:
            高频工作流列表
        """
        # 按频率排序
        sorted_workflows = sorted(
            self.workflows,
            key=lambda w: w.frequency,
            reverse=True
        )

        # 返回频率 >= 3 的工作流
        return [w for w in sorted_workflows if w.frequency >= 3]

    def suggest_automation(self) -> List[str]:
        """
        生成自动化建议

        Returns:
            建议列表
        """
        suggestions = []
        automatable = self.get_automatable_workflows()

        for workflow in automatable:
            suggestion = (
                f"建议自动化: {workflow.name}\n"
                f"  - 执行频率: {workflow.frequency} 次\n"
                f"  - 触发模式: {', '.join(workflow.trigger_patterns)}\n"
                f"  - 可设置定时任务自动执行"
            )
            suggestions.append(suggestion)

        return suggestions

    def analyze_sessions(self, days: int = 7) -> Dict[str, Any]:
        """
        分析近期会话，提取工作流模式

        Args:
            days: 分析天数

        Returns:
            分析结果
        """
        memory_dir = Path(get_memory_dir())
        sessions_file = memory_dir / "sessions.json"

        if not sessions_file.exists():
            return {"error": "没有会话记录"}

        try:
            with open(sessions_file, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
        except Exception as e:
            return {"error": str(e)}

        # 过滤近期会话
        cutoff = datetime.now() - timedelta(days=days)
        recent_sessions = []

        for session in sessions:
            try:
                session_date = datetime.fromisoformat(session.get("created_at", ""))
                if session_date >= cutoff:
                    recent_sessions.append(session)
            except Exception:
                continue

        # 统计意图
        all_intents = []
        for session in recent_sessions:
            messages = session.get("messages", [])
            for msg in messages:
                if msg.get("role") == "user":
                    intent = self._extract_intent(msg.get("content", ""))
                    if intent != "general":
                        all_intents.append(intent)

        intent_counts = Counter(all_intents)

        return {
            "total_sessions": len(recent_sessions),
            "intent_distribution": dict(intent_counts),
            "top_intents": intent_counts.most_common(5),
            "automatable_suggestions": self.suggest_automation(),
        }

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        删除工作流

        Args:
            workflow_id: 工作流 ID

        Returns:
            是否成功
        """
        original_len = len(self.workflows)
        self.workflows = [w for w in self.workflows if w.id != workflow_id]

        if len(self.workflows) < original_len:
            self.save_workflows()
            return True

        return False


def main():
    """测试入口"""
    learner = WorkflowLearner()

    print("当前工作流:")
    for w in learner.workflows:
        print(f"  - {w.name} (频率: {w.frequency})")

    print("\n分析结果:")
    analysis = learner.analyze_sessions(days=7)
    print(json.dumps(analysis, ensure_ascii=False, indent=2))

    print("\n自动化建议:")
    for suggestion in learner.suggest_automation():
        print(suggestion)


if __name__ == "__main__":
    main()
