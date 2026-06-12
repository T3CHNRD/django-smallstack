"""CRUDView factory: introspect, emit, gate."""

import pytest

from apps.mcp.factory import register_mcp_tools_from_crudview
from apps.mcp.server import TOOL_REGISTRY
from apps.smallstack.crud import Action

from .conftest import GadgetCRUDView, WidgetCRUDView


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _wipe(clean_registry):
    yield


def test_enable_mcp_false_emits_nothing():
    class _Disabled(WidgetCRUDView):
        enable_mcp = False

    register_mcp_tools_from_crudview(_Disabled)
    assert not any(n.startswith("list_") for n in TOOL_REGISTRY)


def test_full_actions_emit_all_five_tools(widget_view):
    register_mcp_tools_from_crudview(widget_view)
    expected = {"list_widgets", "get_widget", "create_widget", "update_widget", "delete_widget"}
    assert expected.issubset(TOOL_REGISTRY.keys())


def test_partial_actions_only_list_and_detail(gadget_view):
    register_mcp_tools_from_crudview(gadget_view)
    assert "list_gadgets" in TOOL_REGISTRY
    assert "get_gadget" in TOOL_REGISTRY
    assert "create_gadget" not in TOOL_REGISTRY


def test_mcp_actions_can_narrow_below_actions(widget_view):
    class _ReadOnlyWidget(WidgetCRUDView):
        mcp_actions = [Action.LIST]

    register_mcp_tools_from_crudview(_ReadOnlyWidget)
    assert "list_widgets" in TOOL_REGISTRY
    assert "create_widget" not in TOOL_REGISTRY
    assert "delete_widget" not in TOOL_REGISTRY


def test_mcp_description_used_in_tool(widget_view):
    register_mcp_tools_from_crudview(widget_view)
    assert TOOL_REGISTRY["list_widgets"].description == widget_view.mcp_description


def test_write_actions_marked_write(widget_view):
    register_mcp_tools_from_crudview(widget_view)
    assert TOOL_REGISTRY["create_widget"].write is True
    assert TOOL_REGISTRY["update_widget"].write is True
    assert TOOL_REGISTRY["delete_widget"].write is True
    assert TOOL_REGISTRY["list_widgets"].write is False


def test_idempotent_registration(widget_view):
    register_mcp_tools_from_crudview(widget_view)
    before = dict(TOOL_REGISTRY)
    register_mcp_tools_from_crudview(widget_view)
    assert TOOL_REGISTRY == before


def test_list_schema_includes_filters_and_search(widget_view):
    register_mcp_tools_from_crudview(widget_view)
    schema = TOOL_REGISTRY["list_widgets"].input_schema
    props = schema["properties"]
    assert "q" in props
    assert "owner" in props
    assert "limit" in props
