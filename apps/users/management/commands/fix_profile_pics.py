# apps/users/management/commands/fix_profile_pics.py
from django.core.management.base import BaseCommand
from apps.users.models import User

class Command(BaseCommand):
    help = 'Agrega prefijo data:image a profile_pic_base64 existentes'

    def handle(self, *args, **options):
        users = User.objects.exclude(profile_pic_base64__isnull=True).exclude(profile_pic_base64='')
        
        fixed_count = 0
        for user in users:
            if not user.profile_pic_base64.startswith('data:image'):
                # Agregar prefijo
                user.profile_pic_base64 = f"data:image/jpeg;base64,{user.profile_pic_base64}"
                user.save(update_fields=['profile_pic_base64'])
                fixed_count += 1
                self.stdout.write(f"✅ Fixed: {user.username}")
            else:
                self.stdout.write(f"⏭️  Skipped: {user.username} (already has prefix)")
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Fixed {fixed_count} profile pictures'))