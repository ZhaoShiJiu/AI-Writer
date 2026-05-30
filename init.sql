CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS novels (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chapters (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL DEFAULT '未命名章节',
    content TEXT NOT NULL DEFAULT '',
    summary TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_generations (
    id SERIAL PRIMARY KEY,
    chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    user_intent TEXT,
    prompt_text TEXT NOT NULL,
    ai_output TEXT NOT NULL,
    accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- V2: 叙事记忆系统

CREATE TABLE IF NOT EXISTS character_memory (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    character_name VARCHAR(255) NOT NULL,
    memory_json JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(novel_id, character_name)
);

CREATE TABLE IF NOT EXISTS world_memory (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    world_state JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(novel_id)
);

CREATE TABLE IF NOT EXISTS summaries (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    summary_type VARCHAR(50) NOT NULL DEFAULT 'chapter',
    summary_text TEXT NOT NULL,
    characters JSONB DEFAULT '[]',
    important_events JSONB DEFAULT '[]',
    emotion VARCHAR(50),
    foreshadowing JSONB DEFAULT '[]',
    embedding_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- V3: 风格画像（每部小说一条记录）
CREATE TABLE IF NOT EXISTS style_profiles (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    style_json JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(novel_id)
);

-- V3: 叙事状态（每章一条记录）
CREATE TABLE IF NOT EXISTS narrative_states (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    chapter_id INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    scene_type VARCHAR(100),
    tension_score REAL DEFAULT 0.5,
    emotion VARCHAR(50),
    pace VARCHAR(50) DEFAULT 'medium',
    goal TEXT,
    emotional_curve JSONB DEFAULT '[]',
    narrative_json JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(chapter_id)
);

-- V4: 故事线
CREATE TABLE IF NOT EXISTS story_arcs (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    arc_type VARCHAR(50) NOT NULL DEFAULT 'main',
    description TEXT,
    start_chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    end_chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'planned',
    emotional_target JSONB,
    pacing_plan JSONB,
    scene_plan JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- V4: 伏笔系统
CREATE TABLE IF NOT EXISTS foreshadowings (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    planted_at_chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    payoff_at_chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'planned',
    content_snippet TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- V4: 写作计划
CREATE TABLE IF NOT EXISTS writing_plans (
    id SERIAL PRIMARY KEY,
    novel_id INTEGER NOT NULL REFERENCES novels(id) ON DELETE CASCADE,
    chapter_id INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    plan_json JSONB NOT NULL DEFAULT '{}',
    plan_type VARCHAR(50) NOT NULL DEFAULT 'chapter',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- V4: 生成上下文（调试用）
CREATE TABLE IF NOT EXISTS generation_contexts (
    id SERIAL PRIMARY KEY,
    generation_id INTEGER REFERENCES ai_generations(id) ON DELETE SET NULL,
    context_json JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 默认用户（V2 单用户模式）
INSERT INTO users (id, name) VALUES (1, '写作者') ON CONFLICT (id) DO NOTHING;
