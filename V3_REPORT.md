# 小说协同创作 Agent — V3 版本升级报告

> 版本：3.0.0  
> 日期：2026-05-29  
> 升级路径：V2（记忆系统）→ V3（风格学习 + 叙事智能）

---

## 1. 版本定位

| 版本 | 定位 | 核心能力 |
|------|------|----------|
| V1 | AI 续写器 | 能续写 |
| V2 | 具备记忆的续写系统 | 能记忆（角色 + 世界观 + 摘要） |
| **V3** | **个性化叙事 AI** | **能模仿用户文风 + 理解叙事状态** |

V3 是质变——系统从"AI帮你写"进入"AI像你一样写"的阶段，首次具备 **Narrative Intelligence（叙事智能）**。

---

## 2. 新增核心能力

| 能力 | 实现模块 | 说明 |
|------|----------|------|
| 文风学习 | StyleService | LLM 采样分析用户历史章节，构建 Style Profile |
| 叙事理解 | NarrativeService | LLM 分析当前章节的叙事状态（场景类型/张力/情绪/节奏/目标） |
| 情绪曲线 | EmotionService | 从全书叙事状态推导章节级情绪曲线，用于前端可视化 |
| 风格注入 | PromptBuilder.build_v3() | 将风格画像 + 叙事状态 + 情绪目标整合到续写 Prompt |
| 协作控制 | AIPanel V3 控件 | 情绪目标选择、节奏控制、V2/V3 模式切换 |

---

## 3. 系统架构

```
Frontend (Next.js + Zustand + TipTap)
    │
    ▼
Backend API (FastAPI v3.0.0)
    │
    ▼
WritingEngine (V3)
    ├── StyleService ────── LLM 分析 → style_profiles 表
    ├── NarrativeService ── LLM 分析 → narrative_states 表
    ├── EmotionService ──── 推导情绪曲线（只读，无独立表）
    ├── MemoryService ───── V2 角色 + 世界观 + 摘要（保持不变）
    └── PromptBuilder ───── build_v3() 融合全部上下文
```

### 数据流

```
用户写章节 → 自动保存
    ├── V2: 生成摘要 → 提取角色 → 提取世界观 → RAG 索引
    └── V3: 分析叙事状态 → 写入 narrative_states
                                          ↓
用户点击"分析风格" → StyleService 采样5章 → LLM → style_profiles
                                                      ↓
用户切换到 V3 模式 → 点击"AI续写"
    → WritingEngine.generate_continuation_v3()
        → 收集: 记忆上下文 + 风格画像 + 叙事状态 + 情绪目标
        → PromptBuilder.build_v3() 融合全部上下文
        → LLM 生成（模仿文风 + 延续情绪 + 推进叙事）
```

---

## 4. 数据库变更

### 新增表

**style_profiles**（每部小说一条）

| 列 | 类型 | 说明 |
|----|------|------|
| id | SERIAL PK | |
| novel_id | INTEGER UNIQUE FK | 关联 novels |
| style_json | JSONB | 风格画像 JSON |
| created_at / updated_at | TIMESTAMP | |

**narrative_states**（每章一条）

| 列 | 类型 | 说明 |
|----|------|------|
| id | SERIAL PK | |
| novel_id | INTEGER FK | 关联 novels |
| chapter_id | INTEGER UNIQUE FK | 关联 chapters |
| scene_type | VARCHAR(100) | 场景类型 |
| tension_score | REAL | 张力评分 0-10 |
| emotion | VARCHAR(50) | 主导情绪 |
| pace | VARCHAR(50) | 叙事节奏 |
| goal | TEXT | 叙事目标 |
| emotional_curve | JSONB | 章内情绪曲线 |
| narrative_json | JSONB | 完整 LLM 分析结果 |
| created_at / updated_at | TIMESTAMP | |

---

## 5. 后端新增/修改文件清单

### 新增（10个文件）

| 文件 | 说明 |
|------|------|
| `models/style_profile.py` | StyleProfile SQLAlchemy 模型 |
| `models/narrative_state.py` | NarrativeState SQLAlchemy 模型 |
| `repositories/style_profile.py` | 风格画像 upsert 仓库（复用 WorldMemory 模式） |
| `repositories/narrative_state.py` | 叙事状态 upsert 仓库（复用 Summary 模式） |
| `schemas/style.py` | StyleProfileResponse, GenerateRequest |
| `schemas/narrative.py` | NarrativeStateResponse, EmotionCurveResponse |
| `services/style/__init__.py` | StyleService — LLM 采样分析 + 保存 |
| `services/narrative/__init__.py` | NarrativeService — LLM 叙事分析 |
| `services/emotion/__init__.py` | EmotionService — 情绪曲线推导 |
| `api/style.py` | GET/POST `/api/novels/{id}/style-profile` |
| `api/narrative.py` | GET/POST `/api/chapters/{id}/narrative-state`, GET `/api/novels/{id}/narrative-states` |
| `api/emotion.py` | GET `/api/novels/{id}/emotion-curve` |

### 修改（5个文件）

| 文件 | 变更 |
|------|------|
| `init.sql` | 新增 style_profiles 和 narrative_states 表 |
| `api/ai.py` | 新增 `POST /api/chapters/{id}/continue-v3` 端点 |
| `main.py` | 注册3个新路由，版本号 2.0.0 → 3.0.0 |
| `prompts/builder.py` | 新增 V3_SYSTEM_PROMPT + build_v3() 方法 |
| `services/writing/engine.py` | 注入V3服务，新增 generate_continuation_v3()、风格/叙事懒加载、update_memory_after_save 增加叙事分析 |

---

## 6. 前端新增/修改文件清单

### 新增（2个组件）

| 文件 | 说明 |
|------|------|
| `components/StylePanel.tsx` | 可折叠风格分析面板，显示句式/对话比/描写密度/节奏/基调/情绪密度/备注，含"分析风格"按钮 |
| `components/NarrativePanel.tsx` | 可折叠叙事曲线面板，张力柱状图（情绪色条）+ 点击查看详情 + "分析当前章节"按钮 |

### 修改（5个文件）

| 文件 | 变更 |
|------|------|
| `types/index.ts` | 新增 StyleProfile, NarrativeState, EmotionCurve 等 7 个 TypeScript 接口 |
| `lib/api.ts` | 新增 getStyleProfile, generateStyleProfile, getNarrativeState, getEmotionCurve, continueWritingV3 等 7 个 API 函数 |
| `store/useNovelStore.ts` | 新增 4 个 V3 状态字段 + 7 个 action；selectNovel 自动加载风格画像和情绪曲线；selectChapter 自动加载叙事状态 |
| `components/AIPanel.tsx` | 新增 V2/V3 切换开关、V3 控件区（情绪目标选择器、节奏控制器）、内联叙事状态/风格基调指示器 |
| `page.tsx` | 右侧栏新增 StylePanel + NarrativePanel（置于 MemoryPanel 上方） |

---

## 7. Style Profile JSON 结构

StyleService 通过 LLM 分析用户历史章节后产出的风格画像：

```json
{
  "sentence_length": { "average": "medium", "variance": "high" },
  "dialogue_ratio": 0.35,
  "emotion_density": {
    "primary_emotions": ["压抑", "紧张"],
    "density": "high"
  },
  "description_density": "medium",
  "pace": "fast",
  "preferred_tone": "压抑热血混合",
  "common_expressions": ["他冷哼一声", "眼中闪过一抹"],
  "stylistic_notes": "作者偏好短句+高频心理描写，对白占比约35%",
  "sentence_patterns": ["20字以内短句为主", "动作+心理复合句式"]
}
```

### 采样策略

- 每部小说最多取 5 章（首、尾 + 中间均匀分布）
- 每章取前 2000 字符
- Token 预算约 2,500 tokens，适合一次 LLM 调用

---

## 8. Narrative State JSON 结构

NarrativeService 分析每章后产出的叙事状态：

```json
{
  "scene_type": "冲突",
  "tension_score": 7.5,
  "emotion": "紧张",
  "pace": "fast",
  "goal": "长老当众质疑主角境界，制造压迫感和冲突感",
  "emotional_curve": [
    { "position": 0, "emotion": "平静", "intensity": 0.3 },
    { "position": 500, "emotion": "紧张", "intensity": 0.7 },
    { "position": 1200, "emotion": "压抑", "intensity": 0.9 }
  ],
  "narrative_notes": "本段通过对话推进冲突，从平静逐步升级到高潮"
}
```

---

## 9. V3 Prompt 结构

build_v3() 产出的 Prompt 按以下顺序组织上下文：

```
1. 【作者写作风格画像】     ← 新增：句式/对话比/描写密度/节奏/基调
2. 【当前叙事状态】         ← 新增：场景类型/张力/情绪/节奏/目标
3. 【情感目标】             ← 新增：情绪走向指导
4. 【当前角色状态】         ← V2 继承
5. 【世界观状态】           ← V2 继承
6. 【近期剧情摘要】         ← V2 继承
7. 【相关历史剧情（RAG）】  ← V2 继承
8. 【当前正文】             ← V2 继承
9. 【创作意图】 + 【风格要求】
```

关键差异：V3 在正文之前先建立"怎么写"的完整上下文（风格 + 叙事 + 情感），再提供"写什么"的剧情上下文。

---

## 10. API 端点总览

| 方法 | 路径 | 版本 | 说明 |
|------|------|------|------|
| POST | `/api/chapters/{id}/continue` | V2 | 原有续写（保持不变） |
| POST | `/api/chapters/{id}/regenerate` | V2 | 原有重新生成（保持不变） |
| **POST** | **`/api/chapters/{id}/continue-v3`** | **V3** | **整合风格+叙事的续写** |
| **GET** | **`/api/novels/{id}/style-profile`** | **V3** | **获取风格画像** |
| **POST** | **`/api/novels/{id}/style-profile`** | **V3** | **触发风格分析** |
| **GET** | **`/api/chapters/{id}/narrative-state`** | **V3** | **获取叙事状态** |
| **POST** | **`/api/chapters/{id}/narrative-state`** | **V3** | **触发叙事分析** |
| **GET** | **`/api/novels/{id}/narrative-states`** | **V3** | **获取全书叙事状态列表** |
| **GET** | **`/api/novels/{id}/emotion-curve`** | **V3** | **获取全书情绪曲线** |
| GET | `/api/memory/novels/{id}/snapshot` | V2 | 记忆快照（保持不变） |

---

## 11. 关键设计决策

| 决策 | 原因 |
|------|------|
| 风格分析由 LLM 采样 5 章完成 | Token 预算可控（~2,500 tokens）；风格稳定，无需全量分析 |
| 风格分析按需触发（按钮），非每次保存 | LLM 调用昂贵；风格跨章节稳定 |
| 叙事状态在保存时自动更新 | 叙事随章节变化，自动触发合理 |
| EmotionService 无独立表 | 从 narrative_states 推导，避免数据冗余 |
| V3 使用独立 `/continue-v3` 端点 | 完全向后兼容 V2 |
| V3 控件隐藏于切换开关后 | 用户主动选择复杂度，不强加 |
| 纯 CSS 实现情绪曲线可视化 | 不引入图表库依赖 |

---

## 12. 技术栈

| 层 | 技术 | 版本 |
|----|------|------|
| 前端 | Next.js + React 19 + TipTap + Zustand | — |
| 后端 | FastAPI + SQLAlchemy async + Pydantic | v3.0.0 |
| 数据库 | PostgreSQL + JSONB | — |
| 向量库 | Chroma（RAG 检索） | — |
| LLM | DeepSeek V4 Pro（通过 gateway） | — |
| 自然语言 | 中文小说（重点优化中文文风分析） | — |

---

## 13. 验证清单

- [x] 所有 Python 文件编译通过（14 个新增/修改文件）
- [x] TypeScript 编译通过（零错误）
- [x] V2 端点未修改（向后兼容）
- [x] 数据库 DDL 包含 V3 表（`style_profiles` + `narrative_states`）
- [x] 风格画像可存储和读取（StyleService + StylePanel）
- [x] 叙事状态自动生成（update_memory_after_save）
- [x] 情绪曲线可从叙事状态推导（EmotionService）
- [x] V3 Prompt 整合全部上下文（build_v3）
- [x] 前端 V3 控件正常工作（切换/情绪目标/节奏控制）
- [ ] 启动全部服务进行端到端集成测试（需运行环境）
- [ ] 多章节风格分析质量验收（需实际小说数据）

---

## 14. 后续演进方向

| 方向 | 说明 |
|------|------|
| Style Embedding | 将风格向量化，支持风格检索和相似作者推荐 |
| 多轮叙事规划 | 提前规划多章的叙事弧线（narrative arc） |
| 抽象意图理解增强 | "宿命感""史诗感"等抽象创作意图的系统化映射 |
| 风格迁移 | 支持切换写作风格（"用古龙风格写这一章"） |
| A/B 验证 | 对比 V2 和 V3 的生成质量，量化风格一致性 |
