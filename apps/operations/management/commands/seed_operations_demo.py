from django.core.management.base import BaseCommand

from apps.operations.models import PowerStation, PowerStationModel, ShutdownTarget


class Command(BaseCommand):
    help = "Create realistic demo records for operations CRUD screens."

    def handle(self, *args, **options):
        station, created = PowerStation.objects.get_or_create(
            serial="EF-DELTA3MP-001",
            defaults={
                "friendly_name": "Main Rack Delta",
                "backend_type": PowerStation.BackendType.CLOUD_API,
                "model": PowerStationModel.DELTA_3_MAX_PLUS,
                "grace_period_minutes": 120,
                "polling_interval": 20,
            },
        )

        if not created:
            station.friendly_name = "Main Rack Delta"
            station.backend_type = PowerStation.BackendType.CLOUD_API
            station.model = PowerStationModel.DELTA_3_MAX_PLUS
            station.polling_interval = 20
            station.grace_period_minutes = 120
            station.save()

        targets = [
            {
                "name": "Primary NAS",
                "priority": 1,
                "delay_seconds": 15,
                "shutdown_method": ShutdownTarget.ShutdownMethod.SSH_COMMAND,
                "is_host": False,
                "power_draw_watts": 220,
            },
            {
                "name": "Application VM Host",
                "priority": 2,
                "delay_seconds": 20,
                "shutdown_method": ShutdownTarget.ShutdownMethod.OS_API,
                "is_host": False,
                "power_draw_watts": 320,
            },
            {
                "name": "Network Core",
                "priority": 3,
                "delay_seconds": 25,
                "shutdown_method": ShutdownTarget.ShutdownMethod.SSH_COMMAND,
                "is_host": False,
                "power_draw_watts": 80,
            },
            {
                "name": "EcoRsvGrd Host",
                "priority": 4,
                "delay_seconds": 35,
                "shutdown_method": ShutdownTarget.ShutdownMethod.OS_API,
                "is_host": True,
                "power_draw_watts": 140,
            },
        ]

        for payload in targets:
            ShutdownTarget.objects.update_or_create(
                power_station=station,
                priority=payload["priority"],
                defaults=payload,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete: 1 power station and 4 shutdown targets are ready for CRUD browsing."
            )
        )
