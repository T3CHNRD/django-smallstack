from django.contrib import admin

from .models import PowerStation, ShutdownEvent, ShutdownTarget, ShutdownTargetExecutionLog


@admin.register(PowerStation)
class PowerStationAdmin(admin.ModelAdmin):
    list_display = (
        "friendly_name",
        "serial",
        "backend_type",
        "model",
        "extra_battery_model",
        "grace_period_minutes",
        "estimated_runway_hours_display",
    )
    search_fields = ("friendly_name", "serial")
    list_filter = ("backend_type", "model", "extra_battery_model")


@admin.register(ShutdownTarget)
class ShutdownTargetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "power_station",
        "priority",
        "delay_seconds",
        "shutdown_method",
        "is_host",
        "power_draw_watts",
    )
    search_fields = ("name", "power_station__friendly_name", "power_station__serial")
    list_filter = ("shutdown_method", "is_host", "power_station")
    ordering = ("power_station", "priority")


@admin.register(ShutdownEvent)
class ShutdownEventAdmin(admin.ModelAdmin):
    list_display = ("id", "power_station", "started_at", "grid_restored_at")
    list_filter = ("power_station",)
    ordering = ("-started_at",)


@admin.register(ShutdownTargetExecutionLog)
class ShutdownTargetExecutionLogAdmin(admin.ModelAdmin):
    list_display = (
        "shutdown_event",
        "target_name",
        "priority",
        "status",
        "executed_at",
    )
    list_filter = ("status", "shutdown_event__power_station")
    ordering = ("shutdown_event", "priority", "id")
