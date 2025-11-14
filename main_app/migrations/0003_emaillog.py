from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main_app", "0002_emailcredential"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("recipient", models.EmailField(max_length=254)),
                ("sender", models.EmailField(max_length=254)),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("success", models.BooleanField(default=False)),
                ("error_message", models.TextField(blank=True)),
                (
                    "contract",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="email_logs",
                        to="main_app.servicecontract",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
