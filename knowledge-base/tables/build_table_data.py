# -*- coding: utf-8 -*-
"""Merge curated cell-level tables with index-only records for every table.

Existing cell-level rows are preserved. Missing table IDs get a one-row
index record (caption/page/note) so all 100 tables have a structured entry.
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
PATH = os.path.join(BASE, "table-data.json")
FIG_LIST = json.load(open(os.path.join(KB, "figures", "figure-index.json"), encoding="utf-8"))
FIG_MAP = {f["id"]: f for f in FIG_LIST}

EXTRA = [
    {
        "id": "TAB-B-2-2", "caption": "将关系分类后在 FB15K 上的评测结果", "book": "B", "page": 41,
        "columns": ["model", "sampling", "head_1to1", "head_1toN", "head_Nto1", "head_NtoN",
                    "tail_1to1", "tail_1toN", "tail_Nto1", "tail_NtoN"],
        "numeric_columns": list(range(2, 10)), "status": "matrix",
        "rows": [
            ["unstructured", "-", 34.5, 2.5, 6.1, 6.6, 34.3, 4.2, 1.9, 6.6],
            ["SE", "-", 35.6, 62.6, 17.2, 37.5, 34.9, 14.6, 68.3, 41.3],
            ["SME(linear)", "-", 35.1, 53.7, 19.0, 40.3, 32.7, 14.9, 61.6, 43.3],
            ["SME(bilinear)", "-", 30.9, 69.6, 19.9, 38.6, 28.2, 13.1, 76.0, 41.8],
            ["TransE", "-", 43.7, 65.7, 18.2, 47.2, 43.7, 19.7, 66.7, 50.0],
            ["TransH", "unif", 66.7, 81.7, 30.2, 57.4, 63.7, 30.1, 83.2, 60.8],
            ["TransH", "bern", 66.8, 87.6, 28.7, 64.5, 65.5, 39.8, 83.3, 67.2],
            ["TransR", "unif", 76.9, 77.9, 38.1, 66.9, 76.2, 38.4, 76.2, 69.1],
            ["TransR", "bern", 78.8, 89.2, 34.1, 69.2, 79.2, 37.4, 90.4, 72.1],
            ["CTransR", "unif", 78.6, 77.8, 36.4, 68.0, 77.4, 37.8, 78.0, 70.3],
            ["CTransR", "bern", 81.5, 89.0, 34.7, 71.2, 80.8, 38.6, 90.1, 73.8]
        ],
        "note": "Hits@10（%）；分头/尾实体与 1-1/1-N/N-1/N-N 四类。"
    },
    {
        "id": "TAB-B-2-14", "caption": "FB15K 上关系预测的评测结果", "book": "B", "page": 62,
        "columns": ["model", "mr_raw", "mr_filtered", "h1_raw", "h1_filtered"],
        "numeric_columns": [1, 2, 3, 4], "status": "matrix",
        "rows": [
            ["TransE", 2.91, 2.53, 69.5, 90.2],
            ["DKRL(CBOW)", 2.85, 2.51, 65.3, 82.7],
            ["DKRL(CNN)", 2.91, 2.55, 69.8, 89.0],
            ["DKRL(CNN)+TransE", 2.41, 2.03, 69.8, 90.8]
        ],
        "note": "关系预测用 Hits@1；DKRL(CNN)+TransE 最好。"
    },
    {
        "id": "TAB-B-7-1", "caption": "LIWC 词典统计结果", "book": "B", "page": 216,
        "columns": ["level", "words", "labels"],
        "numeric_columns": [1, 2], "status": "matrix",
        "rows": [["合计", 6828, 51], ["级别1", 6828, 10],
                 ["级别2", 6363, 34], ["级别3", 589, 7]],
        "note": "中文 LIWC 的 3 层标签统计。"
    },
    {
        "id": "TAB-B-3-1", "caption": "模型超参数设置", "book": "B", "page": 91,
        "columns": ["parameter", "value"], "numeric_columns": [1], "status": "key_value",
        "rows": [["卷积窗口大小", 3], ["句子表示维度", 230], ["词向量维度", 50],
                 ["位置向量维度", 5], ["训练批次大小", 160], ["学习率", 0.01]],
        "note": "PCNN/CNN 远程监督抽取配置。"
    },
    {
        "id": "TAB-B-3-4", "caption": "模型超参数设置", "book": "B", "page": 99,
        "columns": ["parameter", "value"], "numeric_columns": [1], "status": "key_value",
        "rows": [["卷积窗口大小", 3], ["句子表示维度", 230], ["词向量维度", 50],
                 ["位置向量维度", 5], ["训练批次大小", 160], ["学习率", 0.2]],
        "note": "HATT 配置。"
    },
    {
        "id": "TAB-B-3-8", "caption": "模型超参数设置", "book": "B", "page": 106,
        "columns": ["parameter", "value"], "numeric_columns": [1], "status": "key_value",
        "rows": [["卷积窗口大小", 3], ["句子表示维度", 230], ["词向量维度", 50],
                 ["位置向量维度", 5], ["训练批次大小", 160], ["学习率", 0.001]],
        "note": "MNRE 配置。"
    },
    {
        "id": "TAB-B-3-11", "caption": "模型超参数设置", "book": "B", "page": 117,
        "columns": ["parameter", "value"], "numeric_columns": [1], "status": "key_value",
        "rows": [["训练批次大小", 160], ["学习率", 0.002], ["CNN 句子表示维度", 230],
                 ["RNN 句子表示维度", 200], ["判别器隐层大小", 2048],
                 ["卷积窗口大小", 3], ["词向量维度", 50], ["位置向量维度", 5]],
        "note": "多语言/对抗关系抽取配置。"
    },
    {
        "id": "TAB-B-4-2", "caption": "最优超参数设定", "book": "B", "page": 137,
        "columns": ["parameter", "value"], "numeric_columns": [1], "status": "key_value",
        "rows": [["学习率", 0.005], ["LSTM 隐藏层维数", 100], ["词向量维数", 300],
                 ["窗口大小", 15], ["批次大小", 1000]],
        "note": "KNET 最优超参数。"
    }
]


def main():
    data = json.load(open(PATH, encoding="utf-8"))["tables"] if os.path.exists(PATH) else []
    have = {t["id"] for t in data}
    for t in data:
        t.setdefault("status", "matrix")
    extra = list(EXTRA)
    import glob
    for extra_path in sorted(glob.glob(os.path.join(BASE, "table-extra*.json"))):
        extra += json.load(open(extra_path, encoding="utf-8"))["tables"]
    idx = {t["id"]: i for i, t in enumerate(data)}
    for t in extra:
        if t["id"] in idx:
            if data[idx[t["id"]]].get("status") == "index_only":
                data[idx[t["id"]]] = t
        else:
            data.append(t)
            have.add(t["id"])
    for f in FIG_LIST:
        if f["kind"] != "表" or f["id"] in have:
            continue
        data.append({
            "id": f["id"], "caption": f["caption"], "book": f["book"], "page": f["page"],
            "columns": ["table_id", "caption", "page", "note"],
            "numeric_columns": [],
            "rows": [[f["id"], f["caption"], f["page"], f["note"]]],
            "status": "index_only",
            "note": f["note"],
        })
        have.add(f["id"])
    for t in data:
        if t.get("status") == "index_only" and t["id"] in FIG_MAP:
            t["note"] = FIG_MAP[t["id"]]["note"]
    data.sort(key=lambda t: (t["book"], t["page"], t["id"]))
    json.dump({"tables": data}, open(PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    from collections import Counter
    print("total", len(data), "status", dict(Counter(t["status"] for t in data)))


if __name__ == "__main__":
    main()
