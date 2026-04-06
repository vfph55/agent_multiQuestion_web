#!/usr/bin/env python3
"""批量测试知识问答 Agent."""

from src.agent import KnowledgeAgent


def run_tests():
    """运行测试用例."""
    agent = KnowledgeAgent()

    test_cases = [
        # (问题, 期望类型)
        ("公司的年假有多少天？", "company"),
        ("Python命名规范是什么？", "company"),
        ("试用期多长？", "company"),
        ("什么是机器学习？", "general"),
        ("Python怎么写类？", "general"),
        ("解释一下装饰器", "general"),
    ]

    print("=" * 60)
    print("🧪 知识问答 Agent 测试")
    print("=" * 60)

    for question, expected_type in test_cases:
        print(f"\n❓ 问题: {question}")
        result = agent.answer(question)

        # 验证路由
        is_correct = result['question_type'] == expected_type
        icon = "✅" if is_correct else "❌"
        print(f"{icon} 路由: {result['question_type']} (期望: {expected_type})")
        print(f"📤 来源: {result['source']}")
        print(f"💬 回答: {result['answer'][:100]}...")
        print("-" * 60)


if __name__ == "__main__":
    run_tests()
