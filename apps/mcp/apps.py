"""AppConfig for the MCP (Model Context Protocol) server.

CRITICAL: `label = "mcp_server"` (not "mcp"). The `mcp` PyPI package owns the
"mcp" Python module name, and Django keys app config by label — using "mcp"
collides with importable name and silently breaks signal wiring.
"""

import importlib
import logging

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger("smallstack.mcp")


class MCPConfig(AppConfig):
    name = "apps.mcp"
    label = "mcp_server"
    verbose_name = "Model Context Protocol"

    def ready(self):
        # Step 1: import any project-supplied tool modules so their @tool
        # decorators self-register against the singleton server.
        for path in getattr(settings, "MCP_TOOL_MODULES", []) or []:
            try:
                importlib.import_module(path)
            except Exception:
                logger.exception("Failed to import MCP_TOOL_MODULES entry %s", path)

        # Step 2: walk the CRUDView registry and emit factory tools for
        # anything opted in via enable_mcp = True.
        try:
            from apps.smallstack.crud import CRUDView

            from .factory import register_mcp_tools_from_crudview
        except ImportError:
            return

        for view_cls in list(CRUDView._registry.values()):
            if getattr(view_cls, "enable_mcp", False):
                try:
                    register_mcp_tools_from_crudview(view_cls)
                except Exception:
                    logger.exception("Failed to register MCP tools for %s", view_cls)
