from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("halls", "0002_hall_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="hall",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
