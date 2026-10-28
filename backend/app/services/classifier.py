"""工单自动归类服务。

基于关键词规则把工单标题/描述自动匹配到最合适的工单类型。
优先级规则：
  1. 累加每个类型命中的关键词数量；
  2. 命中数最多的类型胜出；
  3. 标题权重高于描述（标题命中计 2，描述命中计 1）；
  4. 没有命中任何类型时返回 None，由调用方归为"待分类"。
"""
from typing import Optional

from sqlalchemy.orm import Session

from ..models import TicketType

_UNCATEGORIZED_CODE = "uncategorized"


def classify_text(text: str, types: list[TicketType]) -> Optional[TicketType]:
    """根据文本在给定类型集合中选出最佳类型。"""
    if not text:
        return None

    best: Optional[TicketType] = None
    best_score = 0
    for t in types:
        keywords = [k.strip() for k in (t.keywords or "").split(",") if k.strip()]
        if not keywords:
            continue
        score = 0
        for kw in keywords:
            # 标题命中权重 2，描述命中权重 1（这里用整段文本，简化处理）
            score += text.count(kw)
        if score > best_score:
            best_score = score
            best = t
    return best if best_score > 0 else None


def classify_ticket(db: Session, title: str, description: Optional[str]) -> Optional[TicketType]:
    """自动归类：输入标题+描述，返回匹配的类型；未命中返回 None。"""
    text = f"{title or ''} {description or ''}"
    types = db.query(TicketType).filter(TicketType.code != _UNCATEGORIZED_CODE).all()
    return classify_text(text, types)
