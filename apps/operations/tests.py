from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import PowerStation, PowerStationModel, ShutdownTarget


class OperationsModelValidationTests(TestCase):
    def setUp(self):
        self.station = PowerStation.objects.create(
            serial="PS-TEST-001",
            friendly_name="Lab Delta",
            backend_type=PowerStation.BackendType.CLOUD_API,
            model=PowerStationModel.DELTA_PRO_3,
            grace_period_minutes=30,
        )

    def test_shutdown_target_power_draw_watts_required(self):
        target = ShutdownTarget(
            power_station=self.station,
            name="NAS",
            priority=1,
            delay_seconds=15,
            shutdown_method=ShutdownTarget.ShutdownMethod.SSH_COMMAND,
            is_host=False,
            power_draw_watts=None,
        )
        with self.assertRaises(ValidationError):
            target.full_clean()

    def test_grace_period_hard_block_triggers_at_boundary_overage(self):
        ShutdownTarget.objects.create(
            power_station=self.station,
            name="NAS",
            priority=1,
            delay_seconds=15,
            shutdown_method=ShutdownTarget.ShutdownMethod.SSH_COMMAND,
            is_host=False,
            power_draw_watts=400,
        )
        # 4096 Wh / 400 W = 10.24h => 614.4m runway; 90% cap = 552.96m
        self.station.grace_period_minutes = 553
        with self.assertRaises(ValidationError):
            self.station.full_clean()

    def test_grace_period_just_under_cap_is_valid(self):
        ShutdownTarget.objects.create(
            power_station=self.station,
            name="NAS",
            priority=1,
            delay_seconds=15,
            shutdown_method=ShutdownTarget.ShutdownMethod.SSH_COMMAND,
            is_host=False,
            power_draw_watts=400,
        )
        self.station.grace_period_minutes = 552
        self.station.full_clean()

    def test_child_power_draw_update_recomputes_grace_block(self):
        self.station.grace_period_minutes = 120
        self.station.save()

        ShutdownTarget.objects.create(
            power_station=self.station,
            name="Storage",
            priority=1,
            delay_seconds=10,
            shutdown_method=ShutdownTarget.ShutdownMethod.SSH_COMMAND,
            is_host=False,
            power_draw_watts=300,
        )

        violating_target = ShutdownTarget(
            power_station=self.station,
            name="VM Host",
            priority=2,
            delay_seconds=10,
            shutdown_method=ShutdownTarget.ShutdownMethod.OS_API,
            is_host=True,
            power_draw_watts=2400,
        )

        with self.assertRaises(ValidationError):
            violating_target.full_clean()
