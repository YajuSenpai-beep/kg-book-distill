# -*- coding: utf-8 -*-
"""Create the annotation layer if missing. Never overwrites existing notes."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "obsidian", "30-批注")
os.makedirs(OUT, exist_ok=True)

EXAMPLES = {
    "A-05-04-24": ("TransE 推理", "TransE 的一对多问题在书里是明确的：h+r≈t 无法区分同一头实体对应的多个尾实体。工程上先看关系基数切片，若 1-N 占比高，直接上 TransR/KR-EAR，不要继续调 TransE 的维度。"),
    "B-02-03-13": ("TransR 关系特定空间", "TransR 的代价是每个关系一个矩阵；关系数上千时参数会膨胀。实操先用基分解/低秩，或者只对高频关系用 TransR，长尾关系回退到 TransH。"),
    "A-04-03-28": ("远程监督", "远程监督不是“免费标注”，而是“带噪弱标注”。落地时先做 bag 级抽样，确认噪声类型，再决定用句级注意力还是关系层次注意力；不要直接拿句子级标签训练。"),
    "B-06-04-13": ("CSP 内外部模型组合", "CSP 的关键不是模型多复杂，而是按词频路由：高频词用上下文，低频词用字信息。实现时先统计词频分布，再定路由阈值。"),
    "A-03-02-12": ("何时使用原生图数据库", "三个判断里最容易误判的是“模型灵活性”。如果 Schema 其实很稳定，图库的灵活性优势用不上，反而增加运维成本；先用基准查询验证多跳收益。"),
    "A-06-03-16": ("表示学习实体对齐的两条路线", "有种子时优先“分别嵌入 + 线性对齐”，可回滚；无种子时先做分块 + 字符串/结构匹配，再迭代。不要一上来做硬对齐。"),
    "A-07-01-07": ("KGQA 的四类实现方法", "生产系统通常是混合：高频问题模板兜底，复杂问题走语义解析/查询图，开放问题走检索排序。单选一种方法很少能覆盖真实日志。"),
    "A-08-04-39": ("R-GCN", "R-GCN 的前提是关系类型有限且图不太稀疏。关系数上千时先做基分解；邻居平均度低于 2 时，GNN 的收益通常不如 KRL + 外部信息。"),
    "A-09-03-14": ("事理知识图谱的定义", "事理图谱的难点是事件 Schema 和关系标注，不是图算法。没有稳定的事件类型与论元体系时，先别建事理图谱，做事件抽取评测更实际。"),
    "B-07-03-07": ("SDLM 架构", "SDLM 的可解释性来自义原激活，但参数共享和稀疏连接让它更像“可解释的软检索”，不是严格推理。适合做语义线索，不适合做高风险结论。"),
}

README = """# 批注层

这里放**人工批注**，不会被 `build_exports.py` 覆盖。

## 用法

1. 新建 `批注-<知识点ID>.md`，例如 `批注-A-05-04-24.md`。
2. 在批注里写：我的理解、反例、项目经验、待验证问题。
3. 重新运行 `python -I build_exports.py`，对应知识点笔记顶部会出现指向该批注的链接。
4. 不要改 `10-知识点/` 下的生成笔记；它们会被重建覆盖。

## 模板

见 `模板.md`。
"""

TEMPLATE = """---
type: annotation
point: "A-05-04-24"
tags:
  - 批注
---

# 批注：<知识点标题>

## 我的理解

## 反例 / 边界

## 项目经验

## 待验证

返回 [[A-05-04-24 TransE 推理]]
"""


def main():
    for name, text in [("README.md", README), ("模板.md", TEMPLATE)]:
        path = os.path.join(OUT, name)
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").write(text)
    for pid, (title, body) in EXAMPLES.items():
        path = os.path.join(OUT, f"批注-{pid}.md")
        if os.path.exists(path):
            continue
        text = f"""---
type: annotation
point: "{pid}"
tags:
  - 批注
---

# 批注：{title}

{body}

返回 [[{pid} {title}]]
"""
        open(path, "w", encoding="utf-8").write(text)
    print("annotations", len([x for x in os.listdir(OUT) if x.startswith("批注-")]))


if __name__ == "__main__":
    main()
