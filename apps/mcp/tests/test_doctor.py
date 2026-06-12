"""mcp_doctor management command."""

import json
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


pytestmark = pytest.mark.django_db
User = get_user_model()


def test_doctor_exits_clean(capsys):
    User.objects.create_user(username="docuser", password="x", is_staff=True)
    call_command("mcp_doctor", "--no-self-test")
    out = capsys.readouterr().out
    assert "SmallStack MCP" in out


def test_doctor_json_emits_parseable_json():
    out = StringIO()
    call_command("mcp_doctor", "--no-self-test", "--json", stdout=out)
    data = json.loads(out.getvalue())
    assert isinstance(data, list)
    assert any(row["name"] == "URL conf" for row in data)


def test_self_test_runs_against_real_user(capsys):
    User.objects.create_user(username="docuser2", password="x", is_staff=True)
    call_command("mcp_doctor")
    out = capsys.readouterr().out
    assert "Self-test" in out
