from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import PowerStation, PowerStationModel, ShutdownTarget
from .services.ecoflow_simulator import EcoFlowSimulator


User = get_user_model()


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


class EcoFlowSimulatorServiceTests(TestCase):
    def test_profile_has_required_state_fields(self):
        simulator = EcoFlowSimulator()
        snapshot = simulator.get_snapshot(profile="river3_plus_eb300", step=0)
        self.assertEqual(snapshot.profile, "river3_plus_eb300")
        self.assertIn("grid", snapshot.state)
        self.assertIn("battery", snapshot.state)
        self.assertIn("soc", snapshot.state)
        self.assertIn("input_w", snapshot.state)
        self.assertIn("output_w", snapshot.state)
        self.assertIn("extra_battery_present", snapshot.state)

    def test_timeline_cycles_through_transitions(self):
        simulator = EcoFlowSimulator()
        timeline = simulator.build_timeline(profile="river3_plus_no_eb", start_step=3, count=3)
        self.assertEqual([entry.step for entry in timeline], [3, 0, 1])
        self.assertEqual(timeline[0].state["extra_battery_present"], False)


class EcoFlowSimulatorApiTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username="opsstaff", password="testpass123", is_staff=True)

    def test_api_requires_authentication(self):
        url = reverse("operations:api_simulated_ecoflow_state")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

    def test_api_returns_simulated_state_for_staff(self):
        self.client.force_login(self.staff_user)
        url = reverse("operations:api_simulated_ecoflow_state")
        response = self.client.get(url, {"profile": "river3_plus_eb300", "step": 2})
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["profile"], "river3_plus_eb300")
        self.assertEqual(payload["step"], 2)
        self.assertEqual(payload["state"]["grid"], False)
        self.assertEqual(payload["state"]["battery"], "discharging")

    def test_api_returns_timeline_when_count_provided(self):
        self.client.force_login(self.staff_user)
        url = reverse("operations:api_simulated_ecoflow_state")
        response = self.client.get(url, {"profile": "river3_plus_no_eb", "step": 2, "count": 4})
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["count"], 4)
        self.assertEqual(len(payload["transitions"]), 4)
        self.assertEqual(payload["transitions"][0]["step"], 2)
