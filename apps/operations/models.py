from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class PowerStationModel(models.TextChoices):
    DELTA_3_MAX_PLUS = "delta_3_max_plus", "DELTA 3 Max Plus (2048 Wh)"
    DELTA_PRO_3 = "delta_pro_3", "DELTA Pro 3 (4096 Wh)"
    DELTA_PRO_ULTRA = "delta_pro_ultra", "DELTA Pro Ultra (6000 Wh)"
    RIVER_3_PLUS = "river_3_plus", "RIVER 3 Plus (286 Wh)"


class ExtraBatteryModel(models.TextChoices):
    NONE = "", "No Extra Battery"
    DELTA_3_EXTRA = "delta_3_extra", "DELTA 3 Extra Battery (1024 Wh)"
    DELTA_PRO_3_EXTRA = "delta_pro_3_extra", "DELTA Pro 3 Extra Battery (4096 Wh)"
    DELTA_PRO_ULTRA_BATTERY = "delta_pro_ultra_battery", "DELTA Pro Ultra Battery (6000 Wh)"
    RIVER_3_PLUS_EXTRA = "river_3_plus_extra", "RIVER 3 Plus Extra Battery (286 Wh)"


NAMEPLATE_WH_BY_MODEL: dict[str, int] = {
    PowerStationModel.DELTA_3_MAX_PLUS: 2048,
    PowerStationModel.DELTA_PRO_3: 4096,
    PowerStationModel.DELTA_PRO_ULTRA: 6000,
    PowerStationModel.RIVER_3_PLUS: 286,
}

EXTRA_BATTERY_WH_BY_MODEL: dict[str, int] = {
    ExtraBatteryModel.NONE: 0,
    ExtraBatteryModel.DELTA_3_EXTRA: 1024,
    ExtraBatteryModel.DELTA_PRO_3_EXTRA: 4096,
    ExtraBatteryModel.DELTA_PRO_ULTRA_BATTERY: 6000,
    ExtraBatteryModel.RIVER_3_PLUS_EXTRA: 286,
}


class PowerStation(models.Model):
    class BackendType(models.TextChoices):
        CLOUD_API = "cloud_api", "Cloud API"
        USB_HID = "usb_hid", "USB HID"

    serial = models.CharField(max_length=64, unique=True)
    friendly_name = models.CharField(max_length=120)
    backend_type = models.CharField(max_length=24, choices=BackendType.choices)
    model = models.CharField(max_length=64, choices=PowerStationModel.choices)
    extra_battery_model = models.CharField(
        max_length=64,
        choices=ExtraBatteryModel.choices,
        blank=True,
        default=ExtraBatteryModel.NONE,
    )
    polling_interval = models.PositiveIntegerField(default=30)
    grace_period_minutes = models.PositiveIntegerField(default=30)

    # Configurable in one place so the cap behavior is explicit and testable.
    GRACE_PERIOD_RUNWAY_SAFETY_FACTOR = Decimal("0.90")

    class Meta:
        ordering = ["friendly_name", "serial"]

    def __str__(self) -> str:
        return f"{self.friendly_name} ({self.serial})"

    @property
    def nameplate_wh(self) -> int:
        return NAMEPLATE_WH_BY_MODEL.get(self.model, 0)

    @property
    def extra_battery_wh(self) -> int:
        return EXTRA_BATTERY_WH_BY_MODEL.get(self.extra_battery_model or ExtraBatteryModel.NONE, 0)

    @property
    def total_capacity_wh(self) -> int:
        return self.nameplate_wh + self.extra_battery_wh

    def total_target_draw_watts(self) -> int:
        if self.pk is None:
            return 0
        agg = self.shutdown_targets.aggregate(total=Sum("power_draw_watts"))
        return int(agg["total"] or 0)

    def estimated_runway_hours(self, total_draw_watts: int | None = None) -> float | None:
        draw = self.total_target_draw_watts() if total_draw_watts is None else int(total_draw_watts)
        if draw <= 0:
            return None
        return self.total_capacity_wh / draw

    def estimated_runway_hours_display(self) -> str:
        runway = self.estimated_runway_hours()
        if runway is None:
            return "-"
        return f"{runway:.2f}"

    estimated_runway_hours_display.short_description = "Estimated Runway (Hours)"

    def validate_grace_period_against_runway(self, total_draw_watts: int | None = None) -> None:
        runway_hours = self.estimated_runway_hours(total_draw_watts=total_draw_watts)
        if runway_hours is None:
            return
        max_minutes = runway_hours * 60 * float(self.GRACE_PERIOD_RUNWAY_SAFETY_FACTOR)
        if self.grace_period_minutes > max_minutes:
            raise ValidationError(
                {
                    "grace_period_minutes": (
                        "Grace period exceeds available runway. "
                        f"Estimated runway is {runway_hours:.2f} hours "
                        f"({runway_hours * 60:.1f} minutes) at current configured load. "
                        f"With the {int(self.GRACE_PERIOD_RUNWAY_SAFETY_FACTOR * 100)}% safety cap, "
                        f"maximum allowed grace period is {max_minutes:.1f} minutes."
                    )
                }
            )

    def clean(self) -> None:
        super().clean()
        self.validate_grace_period_against_runway()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ShutdownTarget(models.Model):
    class ShutdownMethod(models.TextChoices):
        SSH_COMMAND = "ssh_command", "SSH Command"
        OS_API = "os_api", "OS API"

    power_station = models.ForeignKey(
        PowerStation,
        on_delete=models.CASCADE,
        related_name="shutdown_targets",
    )
    name = models.CharField(max_length=120)
    priority = models.PositiveIntegerField()
    delay_seconds = models.PositiveIntegerField(default=0)
    shutdown_method = models.CharField(max_length=24, choices=ShutdownMethod.choices)
    is_host = models.BooleanField(default=False)
    power_draw_watts = models.PositiveIntegerField()

    class Meta:
        ordering = ["power_station", "priority", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["power_station", "priority"],
                name="unique_shutdown_priority_per_power_station",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.power_station.friendly_name}: P{self.priority} {self.name}"

    def clean(self) -> None:
        super().clean()
        if not self.power_station_id:
            return
        sibling_total = (
            ShutdownTarget.objects.filter(power_station=self.power_station)
            .exclude(pk=self.pk)
            .aggregate(total=Sum("power_draw_watts"))
        )
        projected_total = int(sibling_total["total"] or 0) + int(self.power_draw_watts or 0)
        try:
            self.power_station.validate_grace_period_against_runway(total_draw_watts=projected_total)
        except ValidationError as exc:
            msg = exc.message_dict.get("grace_period_minutes", exc.messages)
            if isinstance(msg, list):
                msg = " ".join(msg)
            raise ValidationError(
                {
                    "power_draw_watts": (
                        "This load would violate the parent power station grace-period cap. "
                        f"{msg}"
                    )
                }
            ) from exc

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class ShutdownEvent(models.Model):
    power_station = models.ForeignKey(
        PowerStation,
        on_delete=models.CASCADE,
        related_name="shutdown_events",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    grid_restored_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.power_station.friendly_name} @ {self.started_at:%Y-%m-%d %H:%M:%S}"


class ShutdownTargetExecutionLog(models.Model):
    class Status(models.TextChoices):
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    shutdown_event = models.ForeignKey(
        ShutdownEvent,
        on_delete=models.CASCADE,
        related_name="target_logs",
    )
    shutdown_target = models.ForeignKey(
        ShutdownTarget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="execution_logs",
    )
    target_name = models.CharField(max_length=120)
    priority = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=Status.choices)
    executed_at = models.DateTimeField(null=True, blank=True)
    detail = models.TextField(blank=True)

    class Meta:
        ordering = ["shutdown_event", "priority", "id"]

    def __str__(self) -> str:
        return f"{self.shutdown_event_id} {self.target_name} [{self.status}]"
