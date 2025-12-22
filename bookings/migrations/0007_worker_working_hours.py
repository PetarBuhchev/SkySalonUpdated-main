from __future__ import annotations

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0006_alter_booking_service"),
    ]

    operations = [
        migrations.AddField(
            model_name="worker",
            name="working_hours_end",
            field=models.TimeField(default=datetime.time(18, 0)),
        ),
        migrations.AddField(
            model_name="worker",
            name="working_hours_start",
            field=models.TimeField(default=datetime.time(9, 0)),
        ),
    ]

