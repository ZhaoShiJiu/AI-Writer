"""LangGraph V4 workflow — Multi-Agent narrative orchestration.

Pipeline: START → IntentAnalysis → MemoryRetrieval → StoryGraphQuery
→ NarrativePlanning → ConsistencyPrecheck → Writing → Rewrite
→ ConsistencyPostcheck → MemoryUpdate → END
"""

import logging

from langgraph.graph import StateGraph, END

from app.services.workflow.state import WorkflowState

logger = logging.getLogger(__name__)

# ---- Node Functions ----


async def intent_analysis_node(state: WorkflowState) -> dict:
    """Node 1: Analyze user intent."""
    from app.services.agents.intent import IntentAgent

    agent = IntentAgent()
    result = await agent.think(state)
    logger.info("V4 Workflow: Intent analysis complete")
    return {**result, "current_step": "intent_analysis"}


async def memory_retrieval_node(state: WorkflowState) -> dict:
    """Node 2: Gather all memory context (characters, world, summaries, RAG, foreshadowings)."""
    import re
    from app.services.memory.character import CharacterMemoryService
    from app.services.memory.world import WorldMemoryService
    from app.services.summary import SummaryGenerator
    from app.services.rag.retriever import retriever
    from app.repositories.foreshadowing import ForeshadowingRepository

    novel_id = state.get("novel_id")
    chapter_id = state.get("chapter_id")
    chapter_content = state.get("chapter_content", "")
    user_intent = state.get("user_intent", "")

    if not novel_id:
        return {"memory_context": {}, "current_step": "memory_retrieval"}

    db = state.get("_db_session")
    if not db:
        return {"memory_context": {}, "current_step": "memory_retrieval"}

    memory = {}

    # Characters
    try:
        char_service = CharacterMemoryService(db)
        memory["characters"] = await char_service.list_characters(novel_id)
    except Exception as e:
        logger.warning("Memory retrieval: characters failed: %s", e)
        memory["characters"] = []

    # World state
    try:
        world_service = WorldMemoryService(db)
        memory["world_state"] = await world_service.get_world_state_dict(novel_id)
    except Exception as e:
        logger.warning("Memory retrieval: world failed: %s", e)
        memory["world_state"] = {}

    # Recent summaries
    try:
        summary_gen = SummaryGenerator(db)
        memory["recent_summaries"] = await summary_gen.get_recent_summaries(novel_id, limit=5)
    except Exception as e:
        logger.warning("Memory retrieval: summaries failed: %s", e)
        memory["recent_summaries"] = []

    # RAG retrieval
    try:
        clean_content = re.sub(r"<[^>]+>", "", chapter_content)[-500:]
        query = f"{user_intent} {clean_content}"
        memory["rag_events"] = await retriever.retrieve(novel_id, query, top_k=5)
    except Exception as e:
        logger.warning("Memory retrieval: RAG failed: %s", e)
        memory["rag_events"] = []

    # Pending foreshadowings
    try:
        foreshadowing_repo = ForeshadowingRepository(db)
        memory["foreshadowings"] = await foreshadowing_repo.list_pending(novel_id)
    except Exception as e:
        logger.warning("Memory retrieval: foreshadowings failed: %s", e)
        memory["foreshadowings"] = []

    logger.info("V4 Workflow: Memory retrieved (%d chars, %d world, %d summaries, %d rag, %d foreshadowings)",
                len(memory["characters"]), len(memory["world_state"]),
                len(memory["recent_summaries"]), len(memory["rag_events"]),
                len(memory["foreshadowings"]))

    return {"memory_context": memory, "_raw_memory": memory, "current_step": "memory_retrieval"}


async def story_graph_query_node(state: WorkflowState) -> dict:
    """Node 3: Query Neo4j story graph for relationship context."""
    from app.services.graph.story_graph import story_graph_service
    from app.config import settings

    novel_id = state.get("novel_id")

    if not settings.feature_neo4j_enabled:
        return {"graph_context": {}, "current_step": "story_graph_query"}

    try:
        graph_data = await story_graph_service.get_story_graph_data(novel_id)
        logger.info("V4 Workflow: Graph query complete (%d nodes, %d edges)",
                    len(graph_data.get("nodes", [])), len(graph_data.get("edges", [])))
        return {"graph_context": graph_data, "current_step": "story_graph_query"}
    except Exception as e:
        logger.warning("V4 Workflow: Graph query failed: %s", e)
        return {"graph_context": {}, "current_step": "story_graph_query"}


async def narrative_planning_node(state: WorkflowState) -> dict:
    """Node 4: Plan the scene using PlannerAgent + NarrativeAgent."""
    from app.services.agents.planner import PlannerAgent
    from app.services.agents.narrative_agent import NarrativeAgent

    # Run NarrativeAgent (lightweight, provides pacing/emotion guidance)
    narrative_agent = NarrativeAgent()
    narrative_result = await narrative_agent.think(state)

    # Run PlannerAgent (core — generates scene plan)
    planner_agent = PlannerAgent()
    planner_result = await planner_agent.think(state)

    logger.info("V4 Workflow: Narrative planning complete")
    return {**planner_result, **narrative_result, "current_step": "narrative_planning"}


async def consistency_precheck_node(state: WorkflowState) -> dict:
    """Node 5: Pre-check the writing plan for consistency issues."""
    from app.services.agents.consistency import ConsistencyAgent

    agent = ConsistencyAgent()
    result = await agent.precheck(state)

    logger.info("V4 Workflow: Consistency precheck %s", "passed" if result.get("consistency_pre", {}).get("passed") else "FAILED")
    return {**result, "current_step": "consistency_precheck"}


def precheck_router(state: WorkflowState) -> str:
    """Route based on precheck result."""
    pre = state.get("consistency_pre", {})
    if not pre.get("passed", True):
        # Check if there are critical issues
        issues = pre.get("issues", [])
        criticals = [i for i in issues if i.get("severity") == "critical"]
        if criticals:
            retry = state.get("_retry_count", 0)
            if retry < 1:
                return "retry_planning"
            return "error"
    return "continue"


async def writing_node(state: WorkflowState) -> dict:
    """Node 6: Generate the actual text using WriterAgent."""
    from app.services.agents.writer_agent import WriterAgent

    agent = WriterAgent()
    result = await agent.think(state)

    text = result.get("generated_text", "")
    logger.info("V4 Workflow: Writing complete (%d chars)", len(text))
    return {**result, "current_step": "writing"}


async def rewrite_node(state: WorkflowState) -> dict:
    """Node 7: Rewrite if postcheck found issues."""
    from app.services.agents.writer_agent import WriterAgent

    post = state.get("consistency_post", {})
    issues = post.get("issues", [])
    generated = state.get("generated_text", "")

    if not issues or not generated:
        return {"rewritten_text": generated, "current_step": "rewrite"}

    # Add fix instructions
    fix_note = "请修正以下问题后重写：\n" + "\n".join(
        f"- [{i.get('severity')}] {i.get('description')}: {i.get('suggestion')}"
        for i in issues
    )
    state_with_fix = {**state, "user_intent": state.get("user_intent", "") + "\n" + fix_note}

    agent = WriterAgent()
    result = await agent.think(state_with_fix)

    logger.info("V4 Workflow: Rewrite complete")
    return {"rewritten_text": result.get("generated_text", generated), "current_step": "rewrite"}


async def consistency_postcheck_node(state: WorkflowState) -> dict:
    """Node 8: Post-check the generated text for consistency."""
    from app.services.agents.consistency import ConsistencyAgent

    agent = ConsistencyAgent()
    result = await agent.think(state)

    passed = result.get("consistency_post", {}).get("passed", True)
    logger.info("V4 Workflow: Consistency postcheck %s", "passed" if passed else "FAILED")
    return {**result, "current_step": "consistency_postcheck"}


def postcheck_router(state: WorkflowState) -> str:
    """Route based on postcheck result."""
    post = state.get("consistency_post", {})
    if not post.get("passed", True):
        issues = post.get("issues", [])
        majors = [i for i in issues if i.get("severity") in ("critical", "major")]
        if majors:
            retry = state.get("_retry_count", 0)
            if retry < 1:
                new_retry = retry + 1
                return "rewrite"
    return "continue"


async def memory_update_node(state: WorkflowState) -> dict:
    """Node 9: Update all memory systems with new content."""
    # This is handled by the existing WritingEngine.update_memory_after_save()
    # Called from the API layer after the workflow completes.
    logger.info("V4 Workflow: Memory update deferred to API layer")
    return {"current_step": "memory_update"}


# ---- Build Workflow ----


def build_v4_workflow() -> StateGraph:
    """Build and compile the V4 LangGraph workflow."""
    graph = StateGraph(WorkflowState)

    # Add nodes
    graph.add_node("intent_analysis", intent_analysis_node)
    graph.add_node("memory_retrieval", memory_retrieval_node)
    graph.add_node("story_graph_query", story_graph_query_node)
    graph.add_node("narrative_planning", narrative_planning_node)
    graph.add_node("precheck", consistency_precheck_node)
    graph.add_node("writing", writing_node)
    graph.add_node("rewrite", rewrite_node)
    graph.add_node("postcheck", consistency_postcheck_node)
    graph.add_node("memory_update", memory_update_node)

    # Set entry point
    graph.set_entry_point("intent_analysis")

    # Linear edges where no branching needed
    graph.add_edge("intent_analysis", "memory_retrieval")
    graph.add_edge("memory_retrieval", "story_graph_query")
    graph.add_edge("story_graph_query", "narrative_planning")

    # Conditional: precheck → continue / retry / error
    graph.add_edge("narrative_planning", "precheck")
    graph.add_conditional_edges("precheck", precheck_router, {
        "continue": "writing",
        "retry_planning": "narrative_planning",
        "error": END,
    })

    # Writing → rewrite → postcheck chain
    graph.add_edge("writing", "rewrite")
    graph.add_edge("rewrite", "postcheck")

    # Conditional: postcheck → continue / rewrite
    graph.add_conditional_edges("postcheck", postcheck_router, {
        "continue": "memory_update",
        "rewrite": "rewrite",
    })

    graph.add_edge("memory_update", END)

    return graph.compile()


# Module-level compiled workflow (reused across requests)
_v4_workflow = None


def get_v4_workflow():
    global _v4_workflow
    if _v4_workflow is None:
        _v4_workflow = build_v4_workflow()
    return _v4_workflow
