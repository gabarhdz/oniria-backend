# Generated migration file
# apps/community/migrations/0003_add_owner_to_community.py

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0002_alter_community_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='owned_communities',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]