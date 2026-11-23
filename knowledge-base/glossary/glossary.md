# 术语表

- 术语：40；已解析到知识点：37

| 中文 | English | 别名 | 类别 | 知识点 | 页 |
|---|---|---|---|---|---:|
| 知识图谱 | Knowledge Graph | KG | 概念 | A-01-01-05 | p.16-17 |
| 三元组 | Triple | 头实体-关系-尾实体 | 概念 | A-03-01-03 | p.58-59 |
| 本体 | Ontology | 本体模型 | 概念 | A-05-02-10 | p.132-133 |
| 知识表示 | Knowledge Representation | KR | 概念 | A-02-01-01 | p.36-37 |
| 知识表示学习 | Knowledge Representation Learning | KRL | 概念 | B-01-03-12 | p.22-23 |
| 知识图谱嵌入 | Knowledge Graph Embedding | KGE | 概念 | — | — |
| 知识抽取 | Knowledge Extraction | 信息抽取 | 任务 | A-01-04-06 | p.33 |
| 命名实体识别 | Named Entity Recognition | NER、实体识别 | 任务 | A-04-02-06 | p.83-84 |
| 关系抽取 | Relation Extraction | RE | 任务 | A-04-03-18 | p.95 |
| 属性抽取 | Attribute Extraction | 属性补全 | 任务 | A-04-04-32 | p.107 |
| 事件抽取 | Event Extraction | — | 任务 | A-04-06-42 | p.114-115 |
| 实体对齐 | Entity Alignment | 实体链接、EA | 任务 | A-07-04-20 | p.228-230 |
| 本体匹配 | Ontology Matching | 本体对齐 | 任务 | A-06-02-06 | p.186 |
| 知识融合 | Knowledge Fusion | 知识合并 | 任务 | A-01-04-07 | p.33 |
| 链接预测 | Link Prediction | 知识图谱补全 | 任务 | A-02-04-24 | p.54 |
| 知识推理 | Knowledge Reasoning | 推理 | 任务 | A-01-04-08 | p.34 |
| 知识图谱问答 | Knowledge Graph Question Answering | KGQA | 任务 | A-07-01-06 | p.207-208 |
| 图神经网络 | Graph Neural Network | GNN | 模型 | A-08-03-29 | p.265-266 |
| 图卷积网络 | Graph Convolutional Network | GCN | 模型 | A-08-03-31 | p.266-267 |
| 图注意力网络 | Graph Attention Network | GAT | 模型 | A-08-03-33 | p.268 |
| 随机游走 | Random Walk | 游走 | 方法 | — | — |
| 社区发现 | Community Detection | 社区划分 | 任务 | A-08-02-18 | p.256 |
| 中心度 | Centrality | 中心性 | 概念 | A-08-02-15 | p.254 |
| 义原 | Sememe | — | 概念 | B-05-01-02 | p.160-162 |
| 知网 | HowNet | HowNet | 资源 | B-01-01-05 | p.17 |
| 义项 | Sense | 词义 | 概念 | B-05-01-42 | p.161 |
| 词义消歧 | Word Sense Disambiguation | WSD | 任务 | B-05-02-04 | p.162-163 |
| 事理图谱 | Event Logic Graph | 事件演化图 | 概念 | A-09-03-15 | p.310-311 |
| 多模态知识图谱 | Multimodal Knowledge Graph | MMKG | 概念 | A-09-01-05 | p.292-293 |
| 知识增强预训练 | Knowledge-Enhanced Pretraining | 知识预训练 | 方法 | A-09-05-24 | p.332-333 |
| 联邦知识图谱 | Federated Knowledge Graph | 联邦图谱 | 概念 | A-09-06-43 | p.357-358 |
| 远程监督 | Distant Supervision | 弱监督 | 方法 | A-04-03-28 | p.104 |
| 多实例学习 | Multi-Instance Learning | MIL、bag | 方法 | B-03-02-05 | p.85-90 |
| 注意力机制 | Attention | 注意力 | 方法 | B-03-03-49 | p.92-93 |
| 负采样 | Negative Sampling | 负例采样 | 方法 | B-02-02-57 | p.39-41 |
| 平移模型 | Translational Model | 翻译模型 | 模型 | B-02-02-09 | p.35-36 |
| 双线性模型 | Bilinear Model | — | 模型 | A-02-04-23 | p.54 |
| 张量分解 | Tensor Factorization | 张量分解模型 | 方法 | — | — |
| 零样本 | Zero-Shot | zero-shot | 概念 | A-04-07-48 | p.121-122 |
| 长尾 | Long-Tail | 长尾分布 | 概念 | A-08-04-46 | p.278-279 |

## 定义

- **知识图谱**（Knowledge Graph）：知识图谱用图结构建模实体及其关联关系，并以三元组为基本知识单元。
- **三元组**（Triple）：最简单的方式：一张 (Subject, Predicate, Object) 三列表存所有三元组。
- **本体**（Ontology）：在 TBox 中定义 subClassOf、domain/range、传递/互反/函数等公理，在 ABox 上做演绎推理。
- **知识表示**（Knowledge Representation）：知识表示（KR）是用易于计算机处理的方式描述人脑知识的方法；它不等于数据格式、数据结构或编程语言。
- **知识表示学习**（Knowledge Representation Learning）：符号 KG 计算效率低、数据稀疏；知识表示学习把实体/关系映射为低维向量，提升计算效率与泛化。
- **知识抽取**（Knowledge Extraction）：从结构化/半结构化/文本数据中抽取实体、关系、属性、概念、事件等知识要素。
- **命名实体识别**（Named Entity Recognition）：NER 从文本中识别实体边界并判断其类型，是关系抽取与事件抽取的前置任务。
- **关系抽取**（Relation Extraction）：给定包含两个实体的句子，判断实体间关系并抽取三元组，用于图谱补全。
- **属性抽取**（Attribute Extraction）：为实体补全属性及属性值；属性是描述实体某一方面特征的键值信息。
- **事件抽取**（Event Extraction）：事件抽取通常分事件发现/分类（触发词识别）与事件要素抽取（论元角色）两步。
- **实体对齐**（Entity Alignment）：实体链接 = 实体识别 + 链接消歧，把问句中的提及映射到图谱实体。
- **本体匹配**（Ontology Matching）：本体匹配发现源本体与目标本体之间的映射单元集合，输出概念/关系的对应关系。
- **知识融合**（Knowledge Fusion）：把多源数据中的概念/实体映射到统一命名空间，分本体层与实例层。
- **链接预测**（Link Prediction）：给定 h,r,t 中两个预测第三个，用 Hit@n、MR、MRR 评价；需区分原始与过滤式。
- **知识推理**（Knowledge Reasoning）：利用已有事实/关系推断未知事实，用于链接预测、属性补全、错误检测、问句扩展等。
- **知识图谱问答**（Knowledge Graph Question Answering）：KGQA 的核心是问句表示与理解，以及问句语义与图谱实体/关系的匹配。
- **图神经网络**（Graph Neural Network）：GNN 通过聚合邻居信息更新节点表示，多层堆叠扩大感受野。
- **图卷积网络**（Graph Convolutional Network）：GCN 对邻居特征做归一化聚合，再与自身特征融合，通过多层传播学习节点表示。
- **图注意力网络**（Graph Attention Network）：GAT 用注意力机制为不同邻居分配不同权重，再聚合邻居特征。
- **社区发现**（Community Detection）：社区发现把图划分为内部连接紧密、外部连接稀疏的节点组。
- **中心度**（Centrality）：中心度衡量节点重要性，包括度中心度、中介中心度、接近中心度、PageRank 等。
- **义原**（Sememe）：义原是最小语义单位；HowNet 用约 2000 个义原、义项级标注十万级词条。
- **知网**（HowNet）：HowNet 用义原标注词义；义原是最小语义单位，词义可由义原组合表示。
- **义项**（Sense）：多义词的每个义项单独标注义原，使词义消歧与义项表示成为可能。
- **词义消歧**（Word Sense Disambiguation）：WSD 根据上下文选择词的正确义项；是义原/义项表示的重要应用与评估任务。
- **事理图谱**（Event Logic Graph）：实体图谱描述名词性实体及属性/关系；事理图谱描述谓词性事件及演化逻辑。
- **多模态知识图谱**（Multimodal Knowledge Graph）：MMKG 融合结构化属性、数值特征与实体图像，基于 FB15K/DBpedia/YAGO 构建多模态版本。
- **知识增强预训练**（Knowledge-Enhanced Pretraining）：直接透出三元组会导致重复查询、下游重复训练、不完整误差与隐私风险；可用预训练+向量服务替代。
- **联邦知识图谱**（Federated Knowledge Graph）：联邦 KG 由多参与方分布式构建与消费，需解决激励、确权、溯责、信任与隐私。
- **远程监督**（Distant Supervision）：用知识库中已有三元组对齐文本，自动标注训练数据；假设过强，会引入大量噪声。
- **多实例学习**（Multi-Instance Learning）：把包含同一实体对的句子组成 bag，在 bag 级别做关系预测，降低单句噪声影响。
- **注意力机制**（Attention）：可用注意力熵正则、dropout、实体位置屏蔽等稳定训练，避免注意力塌缩。
- **负采样**（Negative Sampling）：unif 均匀替换头/尾；bern 按头尾实体分布伯努利采样，减少假阴性偏差。
- **平移模型**（Translational Model）：TransE 把关系视为头到尾的平移向量，要求 h+r≈t；简单高效、可扩展。
- **双线性模型**（Bilinear Model）：DistMult 用乘法/双线性函数给三元组打分，关系用矩阵（常为对角）表示。
- **零样本**（Zero-Shot）：在没有目标关系标注时抽取新关系；可用阅读理解式或规则引导的语义映射。
- **长尾**（Long-Tail）：把关系组织成层次图，用 GCN 编码关系树，将头部关系特征迁移到尾部关系；在样本少的关系上效果明显提升。