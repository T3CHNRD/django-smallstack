from django.urls import path

from . import views
from .views import PowerStationCRUDView, ShutdownTargetCRUDView

app_name = "operations"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    *PowerStationCRUDView.get_urls(),
    *ShutdownTargetCRUDView.get_urls(),
    path("api/operations/simulated-ecoflow/state/", views.api_simulated_ecoflow_state, name="api_simulated_ecoflow_state"),
    path("events/", views.page_view, {"slug": "events"}, name="events"),
    path("reports/", views.page_view, {"slug": "reports"}, name="reports"),
    path("notifications/", views.page_view, {"slug": "notifications"}, name="notifications"),
    path("nut/", views.page_view, {"slug": "nut"}, name="nut"),
    path("blackout-buddy/", views.blackout_buddy_view, name="blackout_buddy"),
    path("settings/", views.page_view, {"slug": "settings"}, name="settings"),
]
