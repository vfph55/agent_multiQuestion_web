"""安全过滤器 - 违规/涉密查询检测."""

from typing import Literal, Tuple
from sentence_transformers import SentenceTransformer, util

# 加载轻量级多语言模型（支持中文）
_model = None

def get_model():
    """懒加载模型."""
    global _model
    if _model is None:
        # 使用多语言轻量级模型，支持中文语义理解
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _model


# 违规/涉密查询示例库
VIOLATION_PATTERNS = {
    "confidential_company": [
        "公司财务报表",
        "员工工资表",
        "客户名单",
        "合同金额",
        "融资估值",
        "未公开的产品计划",
        "公司的机密文件",
        "内部人事变动",
        "裁员名单",
        "竞争对手的资料",
    ],
    "confidential_personal": [
        "某某员工的手机号",
        "某某的身份证号",
        "某某的家庭住址",
        "某某的薪资",
        "员工的健康信息",
        "别人的隐私",
    ],
    "violent_illegal": [
        "怎么攻击服务器",
        "怎么入侵系统",
        "怎么破解密码",
        "怎么获取管理员权限",
        "怎么绕过安全检测",
        "写个病毒代码",
        "怎么诈骗",
        "怎么洗钱",
        "制造违禁品",
        "攻击公司网络",
    ],
    "inappropriate": [
        "骂人的脏话",
        "歧视性言论",
        "色情内容",
        "仇恨言论",
        "侮辱性语言",
    ],
}

VIOLATION_MESSAGES = {
    "confidential_company": "⚠️ 该问题涉及公司机密信息，我无法回答。如有工作需要，请联系相关部门授权。",
    "confidential_personal": "⚠️ 该问题涉及个人隐私信息，我无法回答。员工隐私受公司保护。",
    "violent_illegal": "⚠️ 该问题涉及违规/违法行为，我无法回答。请遵守法律法规和公司政策。",
    "inappropriate": "⚠️ 请保持专业礼貌的交流方式。",
}

# 预计算违规模式的向量（缓存）
_violation_embeddings = None

def get_violation_embeddings():
    """获取违规模式的预计算向量."""
    global _violation_embeddings
    if _violation_embeddings is None:
        model = get_model()
        _violation_embeddings = {}
        for category, examples in VIOLATION_PATTERNS.items():
            _violation_embeddings[category] = model.encode(examples)
    return _violation_embeddings


def check_security(query: str, threshold: float = 0.75) -> Tuple[Literal["safe", "blocked"], str]:
    """检查查询是否违规或涉密.

    Args:
        query: 用户查询
        threshold: 相似度阈值，超过则判定为违规

    Returns:
        ("safe"/"blocked", 如果是blocked返回拒绝消息，safe返回空字符串)
    """
    # 1. 快速关键词检查（精确匹配，零成本）
    blocked_keywords = [
        "密码", "入侵", "攻击", "破解", "漏洞利用",
        "工资表", "薪资表", "身份证号", "手机号",
    ]
    for keyword in blocked_keywords:
        if keyword in query.lower():
            # 关键词命中，进一步判断语义
            pass

    # 2. Sentence-BERT 语义相似度检查
    model = get_model()
    query_embedding = model.encode(query)
    violation_embeddings = get_violation_embeddings()

    for category, embeddings in violation_embeddings.items():
        # 计算与该类所有示例的相似度
        similarities = util.cos_sim(query_embedding, embeddings)
        max_sim = float(similarities.max())

        if max_sim > threshold:
            return "blocked", VIOLATION_MESSAGES[category]

    return "safe", ""


# 意图识别示例库（Sentence-BERT 方案）
INTENT_EXAMPLES = {
    "company": [
        "公司年假多少天",
        "Python编码规范是什么",
        "怎么请假",
        "报销流程怎么走",
        "公司的工作时间是几点",
        "入职需要准备什么材料",
        "团建活动安排",
        "办公用品怎么领",
        "公司的价值观是什么",
        "绩效考核标准",
    ],
    "realtime": [
        "今天天气怎么样",
        "现在几点了",
        "股价多少",
        "最新的新闻",
        "今天有什么热点",
        "汇率是多少",
        "今天的金价",
        "比赛结果",
        "今天有什么会议",
        "现在的日期",
    ],
    "general": [
        "Python怎么写循环",
        "什么是机器学习",
        "TCP三次握手原理",
        "Docker怎么用",
        "解释一下区块链",
        "怎么学好编程",
        "推荐几本书",
        "什么是API",
        "怎么提高代码质量",
        "解释一下云原生",
    ],
}

# 预计算意图向量（缓存）
_intent_embeddings = None

def get_intent_embeddings():
    """获取意图示例的预计算向量."""
    global _intent_embeddings
    if _intent_embeddings is None:
        model = get_model()
        _intent_embeddings = {}
        for intent, examples in INTENT_EXAMPLES.items():
            _intent_embeddings[intent] = model.encode(examples)
    return _intent_embeddings


def classify_intent_sbert(query: str, threshold: float = 0.6) -> Tuple[str, float]:
    """使用 Sentence-BERT 进行意图识别.

    Args:
        query: 用户查询
        threshold: 最低相似度阈值，低于此值返回 "uncertain"

    Returns:
        (意图类别, 最高相似度分数)
    """
    model = get_model()
    query_embedding = model.encode(query)
    intent_embeddings = get_intent_embeddings()

    scores = {}
    for intent, embeddings in intent_embeddings.items():
        similarities = util.cos_sim(query_embedding, embeddings)
        # 取前3个最高相似度的平均，提高稳定性
        top_k_sims = similarities[0].sort(descending=True)[0][:3]
        scores[intent] = float(top_k_sims.mean())

    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    # 如果最高相似度低于阈值，返回不确定
    if best_score < threshold:
        return "uncertain", best_score

    return best_intent, best_score


# 综合路由函数
def route_with_sbert(query: str) -> Tuple[str, str]:
    """综合路由：先安全检查，再意图识别.

    Returns:
        (路由结果, 说明信息)
        路由结果可能是：blocked, company, realtime, general, llm_fallback
    """
    # 1. 安全检查
    status, message = check_security(query)
    if status == "blocked":
        return "blocked", message

    # 2. 意图识别
    intent, score = classify_intent_sbert(query)

    if intent == "uncertain":
        # 相似度太低，需要 LLM 兜底
        return "llm_fallback", f"语义不明确(相似度{score:.2f})，需LLM判断"

    return intent, f"Sentence-BERT识别(相似度{score:.2f})"


if __name__ == "__main__":
    # 测试
    test_queries = [
        "公司年假多少天",
        "今天天气怎么样",
        "Python怎么写循环",
        "怎么攻击服务器",
        "某某员工的手机号",
        "怎么入侵公司系统",
    ]

    print("=" * 60)
    print("安全过滤 + 意图识别测试")
    print("=" * 60)

    for query in test_queries:
        print(f"\n查询: {query}")
        result, info = route_with_sbert(query)
        print(f"结果: {result}")
        print(f"说明: {info}")
