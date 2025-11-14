from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmailCredential",
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
                ("name", models.CharField(default="Primary", max_length=100)),
                (
                    "from_email",
                    models.EmailField(
                        help_text="Sender address for reminder emails",
                        max_length=254,
                    ),
                ),
                ("smtp_host", models.CharField(max_length=255)),
                ("smtp_port", models.PositiveIntegerField(default=587)),
                ("use_tls", models.BooleanField(default=True)),
                ("use_ssl", models.BooleanField(default=False)),
                ("username", models.CharField(blank=True, max_length=255)),
                ("password", models.CharField(blank=True, max_length=255)),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Only active credentials are used when dispatching reminders.",
                    ),
                ),
            ],
            options={
                "verbose_name": "Email credential",
                "verbose_name_plural": "Email credentials",
                "ordering": ["-updated_at"],
            },
        ),
    ]
