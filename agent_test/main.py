#!/usr/bin/env python3
"""ZURU Melon 知识问答 Agent - CLI 入口."""

from src.agent import KnowledgeAgent


def interactive_mode(agent: KnowledgeAgent):
    """交互式问答模式（支持多轮对话）."""
    print("\n" + "=" * 50)
    print("🤖 ZURU Melon 知识问答 Agent")
    print("=" * 50)
    print("提示：")
    print("  - 询问公司政策/流程/编码规范")
    print("  - 询问通用技术问题")
    print("  - 输入 'new' 开启新会话")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("=" * 50 + "\n")

    current_session_id = None

    while True:
        try:
            prompt_text = f"📝 你的问题 [{current_session_id or '新会话'}]: "
            question = input(prompt_text).strip()

            if not question:
                continue

            if question.lower() in ("quit", "exit", "q"):
                print("👋 再见！")
                break

            if question.lower() == "new":
                current_session_id = None
                print("\n🆕 已开启新会话\n")
                continue

            # 获取回答，传入 session_id 保持上下文
            result = agent.answer(question, current_session_id)

            # 保存 session_id 用于后续对话
            current_session_id = result["session_id"]

            # 显示路由信息
            source_icons = {
                "company": "🏢",
                "realtime": "🔍",
                "general": "🌐"
            }
            source_texts = {
                "company": "知识库",
                "realtime": "实时搜索",
                "general": "通用模型"
            }
            source_icon = source_icons.get(result["question_type"], "🤖")
            source_text = source_texts.get(result["question_type"], "未知")

            print(f"\n{source_icon} [{source_text}] 回答：")
            print("-" * 40)
            print(result["answer"])
            print("-" * 40)
            print(f"会话ID: {result['session_id']}\n")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


def main():
    """主函数."""
    print("📚 正在加载知识库...")

    # 1. 创建 Agent
    agent = KnowledgeAgent()
    print("✓ Agent 已初始化\n")

    # 2. 启动交互模式
    interactive_mode(agent)


if __name__ == "__main__":
    main()
