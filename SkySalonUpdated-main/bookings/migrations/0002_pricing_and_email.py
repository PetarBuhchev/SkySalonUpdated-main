from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="WorkerServicePrice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("price", models.DecimalField(decimal_places=2, max_digits=8)),
                ("duration_minutes", models.PositiveIntegerField(default=60)),
                ("service", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="worker_prices", to="bookings.service")),
                ("worker", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="service_prices", to="bookings.worker")),
            ],
            options={"ordering": ["worker__full_name", "service__name"]},
        ),
        migrations.AlterUniqueTogether(name="workerserviceprice", unique_together={("worker", "service")}),
    ]





