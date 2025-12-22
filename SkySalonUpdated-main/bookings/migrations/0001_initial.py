from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Worker",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=100)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["full_name"]},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("time", models.TimeField()),
                (
                    "phone",
                    models.CharField(
                        help_text="Contact phone number",
                        max_length=20,
                        validators=[django.core.validators.RegexValidator("^[0-9+\\-\\s]{7,20}$", "Enter a valid phone number.")],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "worker",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookings", to="bookings.worker"),
                ),
            ],
            options={"ordering": ["-date", "-time"]},
        ),
        migrations.AlterUniqueTogether(name="booking", unique_together={("worker", "date", "time")}),
    ]




