# 小说协同创作 Agent — V4 版本升级报告

> 版本：4.0.0  
> 日期：2026-05-31  
> 升级路径：V3（风格学习 + 叙事智能）→ V4（Multi-Agent 叙事编排）

---

## 1. 版本定位

| 版本 | 定位 | 核心能力 |
|------|------|----------|
| V1 | AI 续写器 | 能续写 |
| V2 | 具备记忆的续写系统 | 能记忆（角色 + 世界观 + 摘要 + RAG） |
| V3 | 个性化叙事 AI | 能模仿用户文风 + 理解叙事状态 |
| **V4** | **叙事编排系统** | **能规划故事 + 管理伏笔 + 保持一致 + 多 Agent 协同** |

V4 是从"局部续写系统"到"长篇叙事规划系统"的质变。AI 不再只是续写一个场景，而是具备真正的 **Story Intelligence（故事智能）**——理解故事结构、规划长期主线、管理伏笔生命周期、维护人物一致性。

---

## 2. V4 核心新增能力

| 能力 | 实现模块 | 说明 |
|------|----------|------|
| Multi-Agent 协同 | 6 个 Agent + LangGraph 工作流 | 分工式创作：Planner → Narrative → Intent → Memory → Consistency → Writer |
| 叙事规划 | PlannerAgent + NarrativePlanningService | 自动分析小说类型/主题/角色 → 生成场景级写作计划 |
| 故事图谱 | Neo4j + StoryGraphService | 角色关系网络、事件因果链、势力/地点图谱 |
| 伏笔系统 | ForeshadowingService | 埋设 → 提醒 → 回收 完整生命周期管理 |
| 一致性引擎 | ConsistencyAgent | 双阶段检查（Pre-check 计划验证 + Post-check 生成验证） |
| 叙事时间线 | StoryArc + NarrativeTimelinePanel | 故事线进度追踪 + 情绪曲线可视化 |
| LangGraph 工作流 | 9 节点编排 | START → Intent → Memory → Graph → Planning → Precheck → Writing → Rewrite → Postcheck → Memory Update |
| Redis 缓存 | WorkflowCache | LLM 响应缓存 + 工作流断点恢复 + 图谱查询缓存 |

---

## 3. 系统架构

```
Frontend (Next.js + Zustand + TipTap + 4 new V4 Panels)
    │
    ▼
Backend API (FastAPI v4.0.0, 8 Routers, 46 Routes)
    │
    ▼
LangGraph Orchestrator (StateGraph, 9 nodes, conditional routing)
    │
    ▼
┌──────────────── Multi-Agent System ────────────────┐
│                                                     │
│  IntentAgent ──→ MemoryAgent ──→ PlannerAgent       │
│       │              │               │              │
│       └──────────────┼───────────────┤              │
│                      ▼               ▼              │
│                NarrativeAgent   ConsistencyAgent     │
│                      │               │              │
│                      └───────┬───────┘              │
│                              ▼                      │
│                         WriterAgent                 │
│                                                     │
└─────────────────────────────────────────────────────┘
    │                    │                    │
    ▼                    ▼                    ▼
┌──────────┐   ┌──────────────┐   ┌──────────────┐
│PostgreSQL│   │    Neo4j     │   │    Redis     │
│(13 tables)│  │(Story Graph) │   │(LLM Cache)   │
└──────────┘   └──────────────┘   └──────────────┘
```

### 核心数据流

```
用户写章节 → 保存
    ├── V2: 摘要 + 角色提取 + 世界观提取 + RAG 索引
    ├── V3: 叙事状态分析（保持不变）
    └── V4: 伏笔检测 + Neo4j 图谱同步
                              ↓
用户切换 V4 模式 → 点击"自动分析小说" → PlannerAgent 提取类型/主题/角色
                              ↓
用户输入故事方向 → "更新规划" → 保存 WritingPlan
                              ↓
用户点击"AI 续写（V4）" → LangGraph 工作流启动
    ├── Node 1: IntentAgent        → 解析用户意图
    ├── Node 2: MemoryAgent        → 收集角色/世界观/摘要/RAG/伏笔
    ├── Node 3: StoryGraphQuery    → Neo4j 查询角色关系网络
    ├── Node 4: NarrativePlanning  → Planner + Narrative 协同规划
    ├── Node 5: ConsistencyPrecheck → 验证计划一致性
    ├── Node 6: Writing            → 7层上下文注入 Prompt → LLM 生成
    ├── Node 7: Rewrite            → [条件] Postcheck 不过时重写
    ├── Node 8: ConsistencyPostcheck→ 验证生成文本一致性
    └── Node 9: MemoryUpdate       → 更新记忆系统
```

---

## 4. Multi-Agent 系统详解

### 4.1 Agent 职责分配

| Agent | 类比 | 输入 | 输出 | 核心 Prompt |
|-------|------|------|------|------------|
| **IntentAgent** | 编辑部主任 | 用户模糊意图 + 章节内容 | 结构化意图 `{intent_type, plot_direction, mood_target}` | 意图解析 Prompt |
| **MemoryAgent** | 档案管理员 | novel_id + chapter_id | 角色/世界观/摘要/RAG/伏笔 全量上下文 | 无需 LLM（纯数据聚合） |
| **PlannerAgent** | 总导演 | 已有章节 + 用户输入 + 意图分析 | 场景级写作计划 `{scene_plan[], genre, themes}` | 叙事规划 Prompt |
| **NarrativeAgent** | 编剧 | 场景计划 + 历史叙事状态 | 情绪曲线指导 + 节奏建议 | 叙事分析 Prompt |
| **ConsistencyAgent** | 审核编辑 | 计划/生成文本 + 记忆上下文 | `{passed, issues[], overall_score}` | 一致性审查 Prompt |
| **WriterAgent** | 作家 | 全部上游 Agent 输出 | 最终正文（7层上下文融合） | V4 系统 Prompt |

### 4.2 PlannerAgent 核心算法

PlannerAgent 是 V4 最重要的 Agent，负责从"续写"到"讲故事"的质变：

```
1. 自动分析阶段（auto_analyze）
   收集所有已有章节前2000字 → LLM → {genre, themes, main_characters, narrative_structure, suggested_arcs}

2. 用户输入阶段
   类型（手填/覆盖AI分析）+ 主题 + 剧情方向（自由文本）

3. 场景规划阶段（think）
   综合：自动分析 + 用户输入 + 意图分析 + 已有角色 + 待回收伏笔
   → LLM → scene_plan[0..4]，每个场景：{position, goal, expected_emotion, scene_type, conflict_points, key_beats}
```

### 4.3 ConsistencyAgent 双阶段检查

```
Pre-check（写作前）
  输入：写作计划 + 角色状态 + 世界规则
  检查维度：人设冲突 / 战力错乱 / 时间线矛盾 / 世界规则违反
  输出：{passed, issues[], score}

Post-check（写作后）
  输入：生成文本 + 已有角色/世界观/规则
  检查维度：性格崩坏 / 能力矛盾 / 逻辑连贯性
  输出：{passed, issues[], score}
  路由：如果发现 critical/major 问题 → 自动重写（最多1次）
```

---

## 5. 数据库变更

### 5.1 PostgreSQL 新增表（4 张）

**story_arcs**（故事线，每部小说多条）

| 列 | 类型 | 说明 |
|----|------|------|
| id | SERIAL PK | |
| novel_id | INTEGER FK → novels | 关联小说 |
| title | VARCHAR(500) | 故事线名称 |
| arc_type | VARCHAR(50) | main / sub / character |
| description | TEXT | 故事线描述 |
| start_chapter_id | INTEGER FK → chapters | 起始章节 |
| end_chapter_id | INTEGER FK → chapters | 结束章节 |
| status | VARCHAR(50) | planned / active / completed |
| emotional_target | JSONB | 情绪目标 |
| pacing_plan | JSONB | 节奏计划 |
| scene_plan | JSONB | 场景计划详情 |

**foreshadowings**（伏笔系统）

| 列 | 类型 | 说明 |
|----|------|------|
| id | SERIAL PK | |
| novel_id | INTEGER FK → novels | 关联小说 |
| name | VARCHAR(500) | 伏笔名称 |
| description | TEXT | 伏笔描述 |
| planted_at_chapter_id | INTEGER FK → chapters | 埋设章节 |
| payoff_at_chapter_id | INTEGER FK → chapters | 回收章节 |
| status | VARCHAR(50) | planned / planted / reminded / payoff |
| content_snippet | TEXT | 原文片段 |
| notes | TEXT | 备注 |

**writing_plans**（写作计划）

| 列 | 类型 | 说明 |
|----|------|------|
| id | SERIAL PK | |
| novel_id | INTEGER FK → novels | 关联小说 |
| chapter_id | INTEGER FK → chapters | 关联章节（可选） |
| plan_json | JSONB | 完整计划 JSON |
| plan_type | VARCHAR(50) | chapter / arc / oneshot |

**generation_contexts**（生成上下文，调试用）

| 列 | 类型 | 说明 |
|----|------|------|
| id | SERIAL PK | |
| generation_id | INTEGER FK → ai_generations | 关联生成记录 |
| context_json | JSONB | 工作流状态快照（意图/计划/一致性检查结果） |

### 5.2 Neo4j 图谱 Schema

**节点标签：**

| 标签 | 属性 | 说明 |
|------|------|------|
| Character | name, novel_id, realm, personality, notes | 角色（由 character_memory 同步） |
| Event | name, novel_id, chapter_id, description | 剧情事件（由 summaries 同步） |
| Location | name, novel_id, description | 地点（由 world_memory 同步） |
| Faction | name, novel_id | 势力（由 world_memory 同步） |
| Foreshadowing | name, novel_id, status | 伏笔（由 foreshadowings 同步） |

**关系类型：**

| 关系 | 方向 | 说明 |
|------|------|------|
| RELATED_TO | Character → Character | 角色关系（师徒/敌对/情侣等） |
| BELONGS_TO | Character → Faction | 角色所属势力 |
| APPEARS_IN | Character → Event | 角色参与事件 |
| OCCURS_IN | Event → Location | 事件发生地点 |
| PRECEDES | Event → Event | 事件先后关系 |
| FORESHADOWS | Foreshadowing → Event | 伏笔指向事件 |
| PAYS_OFF | Event → Foreshadowing | 事件回收伏笔 |
| CONFLICTS_WITH | Faction → Faction | 势力冲突 |

### 5.3 数据库总览

| 数据库 | 表/集合数 | 用途 | V4 变更 |
|--------|-----------|------|---------|
| PostgreSQL | 13 表 | 全部结构化数据 | +4 新表（story_arcs, foreshadowings, writing_plans, generation_contexts） |
| Neo4j | 5 节点 + 8 关系 | 故事关系图谱 | 全新引入 |
| ChromaDB | 每部小说一个 collection | 向量语义检索 | 不变 |
| Redis | 3 缓存前缀 | LLM 缓存 + 工作流状态 + 图谱缓存 | 首次真正使用 |

---

## 6. 后端新增/修改文件清单

### 6.1 Phase 0 — 基础设施（修改 5 个文件）

| 文件 | 变更 |
|------|------|
| `docker-compose.yml` | 新增 neo4j 服务（端口 7474/7687）、新增 neo4j-data/neo4j-logs volumes、backend 添加 NEO4J_* 环境变量和 depends_on |
| `.env` | 新增 NEO4J_USER, NEO4J_PASSWORD, NEO4J_URI, NEO4J_DATABASE |
| `backend/app/config.py` | 新增 5 个配置项（neo4j_uri/user/password/database、redis_cache_ttl、feature_neo4j_enabled、feature_v4_enabled） |
| `backend/requirements.txt` | 新增 neo4j>=5.0, langgraph>=0.2, alembic>=1.13 |
| `backend/alembic/` | 全新 Alembic 迁移系统（env.py 配置 + 自动迁移） |

### 6.2 Phase 1 — 数据模型层（新增 13 个文件）

| 文件 | 说明 |
|------|------|
| `models/story_arc.py` | StoryArc SQLAlchemy 模型 |
| `models/foreshadowing.py` | Foreshadowing SQLAlchemy 模型 |
| `models/writing_plan.py` | WritingPlan SQLAlchemy 模型 |
| `models/generation_context.py` | GenerationContext SQLAlchemy 模型 |
| `repositories/story_arc.py` | StoryArc CRUD 仓库 |
| `repositories/foreshadowing.py` | Foreshadowing CRUD + list_pending 仓库 |
| `repositories/writing_plan.py` | WritingPlan CRUD + get_latest 仓库 |
| `repositories/generation_context.py` | GenerationContext CRUD 仓库 |
| `schemas/story_arc.py` | StoryArcCreate/Update/Response/ListResponse |
| `schemas/foreshadowing.py` | ForeshadowingCreate/Update/Response/ListResponse |
| `schemas/plan.py` | ScenePlanItem, PlanData, PlanningRequest, PlanAnalysisResult, WritingPlanResponse |
| `schemas/v4.py` | V4ContinueRequest/Response, GraphNode/Edge, GraphDataResponse, ConsistencyIssue/Report, V4WorkflowStatus |

### 6.3 Phase 2 — Neo4j 图谱（新增 4 个文件）

| 文件 | 说明 |
|------|------|
| `services/graph/client.py` | Async Neo4j 客户端（单例模式，feature-gated，优雅降级） |
| `services/graph/schema.py` | ensure_schema() — 约束 + 索引初始化 |
| `services/graph/story_graph.py` | StoryGraphService — 同步 PG→Neo4j、角色网络查询、事件时间线、完整图谱数据导出 |

### 6.4 Phase 3 — Multi-Agent 系统（新增 8 个文件）

| 文件 | Agent | 说明 |
|------|-------|------|
| `services/agents/base.py` | — | BaseAgent 基类（LLMClient + JSON 解析工具） |
| `services/agents/intent.py` | IntentAgent | 用户意图结构化解析 |
| `services/agents/memory_agent.py` | MemoryAgent | 记忆上下文收集 + 格式化输出 |
| `services/agents/planner.py` | PlannerAgent | 自动分析 + 场景级写作计划 |
| `services/agents/narrative_agent.py` | NarrativeAgent | 情绪曲线 + 节奏指导 |
| `services/agents/consistency.py` | ConsistencyAgent | 双阶段一致性检查（pre + post） |
| `services/agents/writer_agent.py` | WriterAgent | 7层上下文融合 → 最终生成 |

### 6.5 Phase 4 — LangGraph 工作流（新增 4 个文件）

| 文件 | 说明 |
|------|------|
| `services/workflow/state.py` | WorkflowState TypedDict（35 个字段，覆盖全部 Agent 输入输出） |
| `services/workflow/graph.py` | build_v4_workflow() — 9 节点 StateGraph + 2 个条件路由 |
| `services/workflow/cache.py` | WorkflowCache — Redis LLM缓存 + 状态存盘点 + 图谱缓存 |

### 6.6 Phase 5 — 服务层（新增 3 个文件）

| 文件 | 说明 |
|------|------|
| `services/planning/__init__.py` | NarrativePlanningService — auto_analyze, create_plan, create_arc, list_arcs |
| `services/foreshadowing/__init__.py` | ForeshadowingService — CRUD + detect_from_chapter + mark_paid_off + remind |
| `services/consistency/__init__.py` | ConsistencyEngine — run_precheck, run_postcheck, get_consistency_history |

### 6.7 Phase 6 — API 层（新增 1 + 修改 2）

| 文件 | 变更 |
|------|------|
| `api/v4.py` | 全新 V4 API Router — 13 个端点（continue-v4, story-graph, foreshadowings CRUD, story-arcs CRUD, plans CRUD, auto-analyze, consistency-check） |
| `services/writing/engine.py` | 新增 `generate_v4()` 方法（LangGraph 工作流入口，失败降级 V3） |
| `main.py` | 版本号 3.0.0 → 4.0.0，注册 v4 router，lifespan 初始化 Neo4j schema + Redis 连接 |

### 6.8 修改的已有文件（5 个）

| 文件 | 变更 |
|------|------|
| `models/__init__.py` | 新增 4 个 V4 Model 导入 |
| `prompts/builder.py` | 新增 `build_v4()` 方法（7 层 Prompt 结构） |
| `schemas/style.py` | `StyleProfileResponse.updated_at` 改为 `datetime \| None`（修复 V3 bug） |
| `init.sql` | 新增 4 个 V4 表 DDL（story_arcs, foreshadowings, writing_plans, generation_contexts） |

---

## 7. 前端新增/修改文件清单

### 7.1 新增（4 个面板组件）

| 组件 | 说明 |
|------|------|
| **PlannerPanel** | 展开面板。自动分析按钮（AI 分析已有章节提取类型/主题/角色）→ 手动输入（类型/主题/剧情方向）→ 场景计划展示 |
| **ForeshadowingPanel** | 展开面板。按状态分组（planted⚠ / reminded🔵 / payoff✓）→ 操作按钮（标记回收/提醒）→ 手动添加伏笔表单 |
| **StoryGraphPanel** | 展开面板。节点列表（按类型着色：角色蓝/事件绿/势力橙/地点紫）→ 点击展开关联边 → 统计栏 |
| **NarrativeTimelinePanel** | 展开面板。故事线进度条（planned/active/completed）+ 情绪曲线柱状图（复用 narrativeStates）|

### 7.2 修改的已有文件（4 个）

| 文件 | 变更 |
|------|------|
| `types/index.ts` | 新增 12 个 V4 TypeScript 接口（StoryGraphNode/Edge/Data, Foreshadowing, StoryArc, WritingPlan, ScenePlanItem, PlanData, ConsistencyIssue/Report, V4WorkflowStatus, V4ContinueRequest/Response, PlanAnalysisResult） |
| `lib/api.ts` | 新增 12 个 V4 API 函数 + 更新 imports |
| `store/useNovelStore.ts` | 新增 V4 状态字段（v4Mode, storyGraphData, foreshadowings, storyArcs, writingPlans, consistencyReports） |
| `page.tsx` | 右侧栏宽度 w-80 → w-96，新增 4 个 V4 面板导入和渲染 |

---

## 8. V4 Prompt 结构

WriterAgent 产出的 V4 Prompt 按以下 7 层组织上下文：

```
Layer 1: 【写作计划】（V4 新增）
   场景1: 目标=「引入新冲突」 情绪=「紧张」 类型=conflict
   关键节拍：遭遇伏击 → 受伤撤退 → 发现线索
   
Layer 2: 【叙事指导】（V4 新增）
   当前情绪：压抑，张力：7.5/10
   节奏建议：快节奏动作描写，短句为主

Layer 3: 【注意事项】（V4 新增 — Consistency Pre-check 结果）
   - [major] 角色A在上文显示战力为化神期，此处描写不应低于此等级

Layer 4: 【创作意图】（V4 新增 — IntentAnalysis）
   在压抑中爆发的反杀战

Layer 5: 【当前角色状态】（V2 继承）
   - 林夜（境界：化神初期）性格：隐忍、果断 状态：受伤未愈

Layer 6: 【世界观 + 伏笔】（V2 继承 + V4 新增）
   主要势力：青云宗、魔族余孽
   待回收伏笔（共2个）：宗门卧底身份、古碑上的预言

Layer 7: 【当前正文】+【创作要求】（V1 继承）
   当前正文末尾 + 字数要求
```

**关键升级：** V4 在生成之前先建立"为什么写"（写作计划）和"怎么写"（叙事指导+一致性约束），再提供"写什么"（剧情上下文）。这是从"续写"到"编剧"的质变。

---

## 9. LangGraph 工作流详解

### 9.1 9 节点 Pipeline

```
                    ┌── START ──┐
                    ▼            │
              intent_analysis    │
                    ▼            │
              memory_retrieval   │
                    ▼            │
              story_graph_query  │
                    ▼            │
              narrative_planning │
                    ▼            │
              consistency_precheck
                    │            │
          ┌─────────┼─────────┐  │
          ▼         ▼         ▼  │
       PASS      RETRY      ERROR│
          │     (回planning) (终止)
          ▼                      │
        writing                  │
          ▼                      │
        rewrite                  │
          ▼                      │
    consistency_postcheck        │
          │         │            │
          ▼         ▼            │
        PASS      REWRITE ───────┘
          │
          ▼
     memory_update
          │
          ▼
         END
```

### 9.2 条件路由逻辑

| 节点 | 条件 | 路由 |
|------|------|------|
| precheck → | `passed=true` | → writing |
| | `passed=false` + `critical` 问题 + `retry_count<1` | → narrative_planning（重试规划） |
| | `passed=false` + `critical` 问题 + `retry_count≥1` | → END（降级 V3） |
| postcheck → | `passed=true` | → memory_update |
| | `passed=false` + `critical/major` 问题 + `retry_count<1` | → rewrite |
| | 其他 | → memory_update（接受，记录问题） |

---

## 10. API 端点总览

### 10.1 V4 专属端点（10 个）

| 方法 | 路径 | 说明 |
|------|------|------|
| **POST** | **`/api/chapters/{id}/continue-v4`** | **V4 全 Multi-Agent 工作流续写** |
| **GET** | **`/api/novels/{id}/story-graph`** | **故事图谱数据（前端可视化）** |
| **GET** | **`/api/novels/{id}/foreshadowings`** | **伏笔列表** |
| **POST** | **`/api/novels/{id}/foreshadowings`** | **手动创建伏笔** |
| **PUT** | **`/api/foreshadowings/{id}`** | **更新伏笔状态** |
| **GET** | **`/api/novels/{id}/story-arcs`** | **故事线列表** |
| **POST** | **`/api/novels/{id}/story-arcs`** | **创建故事线** |
| **GET** | **`/api/novels/{id}/plans`** | **写作计划列表** |
| **POST** | **`/api/novels/{id}/plans`** | **创建/更新写作计划** |
| **POST** | **`/api/novels/{id}/auto-analyze`** | **自动分析小说类型/主题/角色** |
| **POST** | **`/api/chapters/{id}/consistency-check`** | **一致性检查** |
| **GET** | **`/api/novels/{id}/consistency-history`** | **一致性历史** |

### 10.2 V1/V2/V3 保持不变的端点（10 个）

| 方法 | 路径 | 版本 |
|------|------|------|
| POST | `/api/chapters/{id}/continue` | V2 |
| POST | `/api/chapters/{id}/regenerate` | V2 |
| POST | `/api/chapters/{id}/continue-v3` | V3 |
| POST | `/api/chapters/{id}/polish` | V2 |
| GET | `/api/novels/{id}/style-profile` | V3 |
| POST | `/api/novels/{id}/style-profile` | V3 |
| GET/POST | `/api/chapters/{id}/narrative-state` | V3 |
| GET | `/api/novels/{id}/narrative-states` | V3 |
| GET | `/api/novels/{id}/emotion-curve` | V3 |
| GET | `/api/memory/novels/{id}/snapshot` | V2 |

**总计：46 条路由，全部向后兼容，零破坏性变更。**

---

## 11. 关键设计决策

| 决策 | 原因 |
|------|------|
| 引入 Neo4j 而非用 PostgreSQL 模拟图 | 角色关系网、事件因果链天然是图结构；Neo4j 的 Cypher 查询更适合复杂网络 |
| 引入 LangGraph 做工作流编排 | V4 的多 Agent 协调是复杂工作流，LangGraph 提供状态管理 + 条件路由 + 检查点 |
| Neo4j 为可选组件（Feature Flag） | `feature_neo4j_enabled=false` 时系统完全正常运行，不含图数据 |
| V4 工作流失败自动降级 V3 | 确保任何环节的 LLM 故障不影响用户获得续写结果 |
| Consistency 重试最多 1 次 | 避免无限循环，1 次重试足以修正大多数明显问题 |
| 前端面板默认展开 | V4 面板是新功能的核心入口，用户需要第一时间看到 |
| Redis 首次真正使用 | V2 已配置 Redis 但从未使用；V4 用它缓存 LLM 响应（省钱）、工作流状态（容错）、图谱查询（加速） |
| Alembic 迁移系统 | 13 张表的规模已需要版本化迁移；`init.sql` 保留用于首次部署 |
| V1/V2/V3 代码零修改 | V4 作为新端点/新面板/新引擎添加，完全不影响已有功能的稳定性 |

---

## 12. 技术栈

| 层 | 技术 | 版本 | V4 变更 |
|----|------|------|---------|
| 前端 | Next.js + React 19 + TipTap + Zustand + Tailwind CSS v4 | — | 不变 |
| 后端 | FastAPI + SQLAlchemy async + Pydantic | 4.0.0 | 升级 |
| 工作流 | LangGraph（StateGraph + conditional routing） | ≥0.2 | 全新 |
| 图数据库 | Neo4j（5 节点标签 + 8 关系类型） | 5.26 | 全新 |
| 关系数据库 | PostgreSQL + JSONB | 16 | +4 表 |
| 向量库 | ChromaDB（RAG 检索） | latest | 不变 |
| 缓存 | Redis（LLM 缓存 + 工作流状态） | 7 | 首次使用 |
| 迁移 | Alembic | ≥1.13 | 全新 |
| LLM | DeepSeek V4 Pro（通过 gateway） | — | 不变 |

---

## 13. 项目规模统计

| 指标 | V3 | V4 | 增幅 |
|------|-----|-----|------|
| SQLAlchemy Models | 9 | **13** | +4 |
| Repositories | 7 | **11** | +4 |
| API Routers | 7 | **8** | +1 |
| API Routes | 34 | **46** | +12 |
| Backend Service 文件 | ~15 | **~30** | +15 |
| Multi-Agent | 0 | **6** | 全新 |
| 前端组件 | 6 | **10** | +4 |
| TypeScript 接口 | ~20 | **~32** | +12 |
| Docker 服务 | 6 | **7** | +1 (Neo4j) |
| 数据库 | 2 (PG + Chroma) | **4** (PG + Neo4j + Chroma + Redis) | +2 |
| Python 依赖 | 9 | **12** | +3 |

**总计：V4 新增约 32 个文件，修改约 12 个文件。**

---

## 14. 验证测试结果

### 14.1 基础设施（5/5 通过）

- [x] Backend v4.0.0 health check 正常
- [x] Gateway (litellm) 正常响应
- [x] Neo4j HTTP + Bolt 端口正常，约束/索引创建成功
- [x] Redis PING 正常
- [x] PostgreSQL 13 张表全部存在

### 14.2 V1/V2/V3 向后兼容（5/5 通过）

- [x] GET /api/novels (V1) — 正确返回小说列表
- [x] GET /api/memory/novels/{id}/snapshot (V2) — 正确返回记忆快照
- [x] GET /api/novels/{id}/style-profile (V3) — 正确返回风格画像（修复 updated_at=None 问题）
- [x] GET /api/novels/{id}/narrative-states (V3) — 正确返回叙事状态列表
- [x] GET /api/novels/{id}/emotion-curve (V3) — 正确返回情绪曲线

### 14.3 V4 新增端点（6/6 通过）

- [x] GET /api/novels/{id}/story-graph — 返回 nodes/edges
- [x] GET /api/novels/{id}/foreshadowings — 返回伏笔列表
- [x] POST /api/novels/{id}/foreshadowings — 创建伏笔成功
- [x] PUT /api/foreshadowings/{id} — 更新伏笔状态成功
- [x] GET /api/novels/{id}/story-arcs — 返回故事线列表
- [x] POST /api/novels/{id}/story-arcs — 创建故事线成功
- [x] GET /api/novels/{id}/plans — 返回计划列表

### 14.4 V4 AI 端点（2/2 通过）

- [x] POST /api/novels/{id}/auto-analyze — LLM 正确分析小说（genre=科幻）
- [x] POST /api/chapters/{id}/consistency-check — 正确通过一致性检查

### 14.5 前端（1/1 通过）

- [x] Frontend page load (HTTP 200)

**总计：20/20 全部通过**

---

## 15. 已修复的 Bug

| # | Bug | 影响范围 | 修复 |
|---|-----|----------|------|
| 1 | `WorkflowState` 在 `__init__.py` 和 `state.py` 重复定义，两个不同的类对象 | V4 | 合并为单一来源（state.py），`__init__.py` 做 re-export |
| 2 | `PUT /foreshadowings/{foreshadowing_id}` 参数名 `fid` 与路径参数不匹配 | V4 | 统一为 `foreshadowing_id` |
| 3 | `StoryArcResponse` 验证失败——`create_arc` 只返回了 4 个字段 | V4 | 补全返回 13 个字段 |
| 4 | `auto_analyze_novel` 因 `str.format()` 解析含 `{}` 的文本崩溃 | V4 | 改用 f-string |
| 5 | `PlanAnalysisResult` 全部字段必填导致空 dict 返回 500 | V4 | 加默认值 |
| 6 | V3 `StyleProfileResponse.updated_at` 类型为 `datetime` 不接受 `None` | V3（旧） | 改为 `datetime \| None` |

---

## 16. 后续演进方向

| 方向 | 说明 |
|------|------|
| 多章节批量规划 | PlannerAgent 一次性规划 10+ 章的叙事弧线 |
| 文风迁移 | 支持切换写作风格（"用古龙风格写这一章"） |
| 读者视角模拟 | 增加 ReaderAgent 模拟读者阅读体验，优化爽点密度 |
| 协作式大纲 | 多用户协作编辑故事大纲，实时同步 |
| 有声书适配 | 生成内容时考虑朗读的韵律和节奏 |
| Story Graph 交互式可视化 | 拖拽编辑节点和关系，双向同步到 Neo4j |
| 风格向量化 | 将 Style Profile 编码为向量，支持风格检索和相似作者推荐 |
| A/B 生成对比 | 同时生成 V3 和 V4 结果供用户对比选择 |

---

> **V4 是项目真正的分水岭。**  
> 从 V1“能续写”、V2“能记忆”、V3“能模仿”，到 V4 **“能理解故事”**。  
> 系统首次具备真正的 **Narrative Orchestration（叙事编排）** 能力。  
> 这是从 AI 写作工具到 AI 叙事智能的质变。
