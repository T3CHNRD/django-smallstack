from __future__ import annotations

from dataclasses import dataclass

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from apps.smallstack.api import api_error, api_view
from apps.smallstack.crud import Action, CRUDView
from apps.smallstack.mixins import StaffRequiredMixin

from .forms import PowerStationForm, ShutdownTargetForm
from .models import PowerStation, ShutdownTarget
from .services.ecoflow_simulator import EcoFlowSimulator, SimulationProfileError


@dataclass(frozen=True)
class PortalPage:
    slug: str
    title: str
    eyebrow: str
    summary: str
    route_name: str


PAGES: tuple[PortalPage, ...] = (
    PortalPage(
        slug="dashboard",
        title="Dashboard",
        eyebrow="Operations Portal",
        summary="Milestone 1 design-system shell with reusable cards, tables, and navigation placeholders.",
        route_name="operations:dashboard",
    ),
    PortalPage(
        slug="power-stations",
        title="Power Stations",
        eyebrow="Inventory",
        summary="Manage device inventory, grace period limits, and runway estimates.",
        route_name="operations:power-stations-list",
    ),
    PortalPage(
        slug="shutdown-targets",
        title="Shutdown Targets",
        eyebrow="Orchestration",
        summary="Define target priority order, shutdown method, and device load data.",
        route_name="operations:shutdown-targets-list",
    ),
    PortalPage(
        slug="events",
        title="Events",
        eyebrow="Timeline",
        summary="Placeholder timeline shell for outage and restore event history.",
        route_name="operations:events",
    ),
    PortalPage(
        slug="reports",
        title="Reports",
        eyebrow="Insights",
        summary="Placeholder reporting shell for future reliability and reserve analytics.",
        route_name="operations:reports",
    ),
    PortalPage(
        slug="notifications",
        title="Notifications",
        eyebrow="Messaging",
        summary="Placeholder page for future notification preferences and delivery history.",
        route_name="operations:notifications",
    ),
    PortalPage(
        slug="nut",
        title="NUT",
        eyebrow="Protocol",
        summary="Placeholder page for future Network UPS Tools integration status.",
        route_name="operations:nut",
    ),
    PortalPage(
        slug="blackout-buddy",
        title="Blackout Buddy",
        eyebrow="Calculator",
        summary="Appliance runtime calculator with EcoFlow recommendation links.",
        route_name="operations:blackout_buddy",
    ),
    PortalPage(
        slug="settings",
        title="Settings",
        eyebrow="Preferences",
        summary="Placeholder settings shell for Operations Portal presentation options.",
        route_name="operations:settings",
    ),
)

PAGE_BY_SLUG = {page.slug: page for page in PAGES}


def _render_runway_hours(value, obj):
    runway = obj.estimated_runway_hours()
    if runway is None:
        return "-"
    return f"{runway:.2f}"


class PowerStationCRUDView(CRUDView):
    model = PowerStation
    form_class = PowerStationForm
    namespace = "operations"
    url_base = "power-stations"
    mixins = [StaffRequiredMixin]
    actions = [Action.LIST, Action.CREATE, Action.DETAIL, Action.UPDATE, Action.DELETE]
    fields = [
        "serial",
        "friendly_name",
        "backend_type",
        "model",
        "extra_battery_model",
        "polling_interval",
        "grace_period_minutes",
    ]
    list_fields = [
        "friendly_name",
        "serial",
        "backend_type",
        "model",
        "grace_period_minutes",
        "estimated_runway_hours_display",
    ]
    detail_fields = [
        "friendly_name",
        "serial",
        "backend_type",
        "model",
        "extra_battery_model",
        "polling_interval",
        "grace_period_minutes",
        "estimated_runway_hours_display",
    ]
    field_transforms = {
        "estimated_runway_hours_display": _render_runway_hours,
    }
    ordering_fields = ["friendly_name", "serial", "backend_type", "model", "grace_period_minutes"]
    search_fields = ["serial", "friendly_name", "model", "extra_battery_model"]
    filter_fields = ["backend_type", "model", "extra_battery_model"]
    link_field = "friendly_name"
    paginate_by = 25
    enable_api = True
    enable_mcp = True


class ShutdownTargetCRUDView(CRUDView):
    model = ShutdownTarget
    form_class = ShutdownTargetForm
    namespace = "operations"
    url_base = "shutdown-targets"
    mixins = [StaffRequiredMixin]
    actions = [Action.LIST, Action.CREATE, Action.DETAIL, Action.UPDATE, Action.DELETE]
    fields = [
        "power_station",
        "name",
        "priority",
        "delay_seconds",
        "shutdown_method",
        "is_host",
        "power_draw_watts",
    ]
    list_fields = [
        "name",
        "power_station",
        "priority",
        "delay_seconds",
        "shutdown_method",
        "is_host",
        "power_draw_watts",
    ]
    detail_fields = [
        "power_station",
        "name",
        "priority",
        "delay_seconds",
        "shutdown_method",
        "is_host",
        "power_draw_watts",
    ]
    ordering_fields = ["power_station", "priority", "name", "shutdown_method", "is_host", "power_draw_watts"]
    search_fields = ["name", "power_station__friendly_name", "power_station__serial"]
    filter_fields = ["power_station", "shutdown_method", "is_host"]
    link_field = "name"
    paginate_by = 25
    enable_api = True
    enable_mcp = True


def _base_context(request: HttpRequest, current_slug: str) -> dict[str, object]:
    current_page = PAGE_BY_SLUG[current_slug]
    return {
        "portal_pages": PAGES,
        "current_page": current_page,
        "current_slug": current_slug,
        "show_sortable_demo": current_slug == "shutdown-targets",
    }


def dashboard_view(request: HttpRequest) -> HttpResponse:
    context = _base_context(request, "dashboard")
    return render(request, "operations/dashboard.html", context)


def page_view(request: HttpRequest, slug: str) -> HttpResponse:
    if slug not in PAGE_BY_SLUG:
        raise Http404("Operations page not found")
    context = _base_context(request, slug)
    if slug == "dashboard":
        return render(request, "operations/dashboard.html", context)
    return render(request, "operations/page.html", context)


def blackout_buddy_view(request: HttpRequest) -> HttpResponse:
    context = _base_context(request, "blackout-buddy")
    return render(request, "operations/blackout_buddy.html", context)


@api_view(methods=["GET"], require_auth=True, require_staff=True)
def api_simulated_ecoflow_state(request: HttpRequest):
    simulator = EcoFlowSimulator()
    profile = request.GET.get("profile", "river3_plus_eb300")

    try:
        step = int(request.GET.get("step", 0))
        count = int(request.GET.get("count", 1))
    except ValueError:
        return api_error("step and count must be integers", 400)

    if count < 1 or count > 50:
        return api_error("count must be between 1 and 50", 400)

    try:
        if count == 1:
            snapshot = simulator.get_snapshot(profile=profile, step=step)
            return {
                "ok": True,
                "profile": snapshot.profile,
                "model": snapshot.model,
                "extra_battery": snapshot.extra_battery,
                "step": snapshot.step,
                "state": snapshot.state,
                "available_profiles": simulator.available_profiles(),
            }

        timeline = simulator.build_timeline(profile=profile, start_step=step, count=count)
        return {
            "ok": True,
            "profile": profile,
            "count": count,
            "start_step": step,
            "available_profiles": simulator.available_profiles(),
            "transitions": [
                {
                    "step": entry.step,
                    "model": entry.model,
                    "extra_battery": entry.extra_battery,
                    "state": entry.state,
                }
                for entry in timeline
            ],
        }
    except SimulationProfileError as exc:
        return api_error(str(exc), 400)
