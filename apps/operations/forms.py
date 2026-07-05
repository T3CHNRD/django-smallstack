from __future__ import annotations

from django import forms

from .models import PowerStation, ShutdownTarget


class PowerStationForm(forms.ModelForm):
    class Meta:
        model = PowerStation
        fields = [
            "serial",
            "friendly_name",
            "backend_type",
            "model",
            "extra_battery_model",
            "polling_interval",
            "grace_period_minutes",
        ]

    def clean(self):
        cleaned = super().clean()
        # Mirror model-level guard so validation is visible in CRUD form flow.
        self.instance.serial = cleaned.get("serial", self.instance.serial)
        self.instance.friendly_name = cleaned.get("friendly_name", self.instance.friendly_name)
        self.instance.backend_type = cleaned.get("backend_type", self.instance.backend_type)
        self.instance.model = cleaned.get("model", self.instance.model)
        self.instance.extra_battery_model = cleaned.get("extra_battery_model", self.instance.extra_battery_model)
        self.instance.polling_interval = cleaned.get("polling_interval", self.instance.polling_interval)
        self.instance.grace_period_minutes = cleaned.get(
            "grace_period_minutes", self.instance.grace_period_minutes
        )
        self.instance.validate_grace_period_against_runway()
        return cleaned


class ShutdownTargetForm(forms.ModelForm):
    class Meta:
        model = ShutdownTarget
        fields = [
            "power_station",
            "name",
            "priority",
            "delay_seconds",
            "shutdown_method",
            "is_host",
            "power_draw_watts",
        ]

    def clean(self):
        cleaned = super().clean()
        self.instance.power_station = cleaned.get("power_station", self.instance.power_station)
        self.instance.name = cleaned.get("name", self.instance.name)
        self.instance.priority = cleaned.get("priority", self.instance.priority)
        self.instance.delay_seconds = cleaned.get("delay_seconds", self.instance.delay_seconds)
        self.instance.shutdown_method = cleaned.get("shutdown_method", self.instance.shutdown_method)
        self.instance.is_host = cleaned.get("is_host", self.instance.is_host)
        self.instance.power_draw_watts = cleaned.get("power_draw_watts", self.instance.power_draw_watts)
        self.instance.clean()
        return cleaned
