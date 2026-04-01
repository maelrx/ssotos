"""Smoke tests for MCP servers — per Phase 10 Wave 3."""
import pytest


class TestVaultMCP:
    def test_vault_mcp_has_list_notes_tool(self):
        from src.mcp.vault_server import vault_mcp
        tool_names = [t.name for t in vault_mcp._tool_manager.list_tools()]
        assert "vault_list_notes" in tool_names

    def test_vault_mcp_has_crud_tools(self):
        from src.mcp.vault_server import vault_mcp
        tool_names = [t.name for t in vault_mcp._tool_manager.list_tools()]
        assert "vault_create_note" in tool_names
        assert "vault_update_note" in tool_names
        assert "vault_delete_note" in tool_names


class TestAgentMCP:
    def test_agent_mcp_has_brain_tools(self):
        from src.mcp.agent_server import agent_mcp
        tool_names = [t.name for t in agent_mcp._tool_manager.list_tools()]
        assert "brain_get_soul" in tool_names
        assert "brain_get_memory" in tool_names


class TestResearchMCP:
    def test_research_mcp_has_job_tools(self):
        from src.mcp.research_server import research_mcp
        tool_names = [t.name for t in research_mcp._tool_manager.list_tools()]
        assert "research_create_brief" in tool_names
        assert "research_cancel_job" in tool_names


class TestRetrievalMCP:
    def test_retrieval_mcp_has_search_tools(self):
        from src.mcp.retrieval_server import retrieval_mcp
        tool_names = [t.name for t in retrieval_mcp._tool_manager.list_tools()]
        assert "retrieval_search" in tool_names
        assert "retrieval_get_context" in tool_names
