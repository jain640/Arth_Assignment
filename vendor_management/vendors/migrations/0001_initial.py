from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('contact_person', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(max_length=32)),
                (
                    'status',
                    models.CharField(
                        choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')],
                        default='ACTIVE',
                        max_length=16,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='ServiceContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('expiry_date', models.DateField()),
                ('payment_due_date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('ACTIVE', 'Active'),
                            ('EXPIRED', 'Expired'),
                            ('PAYMENT_PENDING', 'Payment Pending'),
                            ('COMPLETED', 'Completed'),
                        ],
                        default='ACTIVE',
                        max_length=20,
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'vendor',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='services',
                        to='vendors.vendor',
                    ),
                ),
            ],
            options={'ordering': ['expiry_date']},
        ),
    ]
