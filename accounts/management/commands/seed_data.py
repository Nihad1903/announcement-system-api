"""
Management command to seed the database with initial data.
Creates default departments, announcement types, and a manager user.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from announcement_types.models import AnnouncementType
from departments.models import Department

User = get_user_model()

DEFAULT_DEPARTMENTS = [
    {'name': 'IT', 'description': 'Information Technology department'},
    {'name': 'HR', 'description': 'Human Resources department'},
    {'name': 'Marketing', 'description': 'Marketing and Communications department'},
    {'name': 'Finance', 'description': 'Finance and Accounting department'},
    {'name': 'Operations', 'description': 'Operations and Logistics department'},
]

DEFAULT_ANNOUNCEMENT_TYPES = [
    {'name': 'General', 'description': 'General announcements'},
    {'name': 'Urgent', 'description': 'Urgent/critical announcements'},
    {'name': 'Event', 'description': 'Event announcements'},
    {'name': 'Policy Update', 'description': 'Policy and procedure updates'},
    {'name': 'Maintenance', 'description': 'System maintenance notices'},
]


class Command(BaseCommand):
    help = 'Seed database with initial departments, announcement types, and a manager account.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--manager-password',
            type=str,
            default='manager123',
            help='Password for the default manager account (default: manager123)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding database...'))

        # Create departments
        for dept_data in DEFAULT_DEPARTMENTS:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults=dept_data,
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Department: {dept.name} — {status}')

        # Create announcement types
        for type_data in DEFAULT_ANNOUNCEMENT_TYPES:
            atype, created = AnnouncementType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data,
            )
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'  Announcement Type: {atype.name} — {status}')

        # Create manager user
        manager_password = options['manager_password']
        manager, created = User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@example.com',
                'first_name': 'System',
                'last_name': 'Manager',
                'role': 'manager',
                'is_staff': True,
            },
        )
        if created:
            manager.set_password(manager_password)
            manager.save()
            self.stdout.write(f'  Manager account created: manager / {manager_password}')
        else:
            self.stdout.write('  Manager account already exists')

        # Create regular user
        user, created = User.objects.get_or_create(
            username='user',
            defaults={
                'email': 'user@example.com',
                'first_name': 'Regular',
                'last_name': 'User',
                'role': 'user',
            },
        )
        if created:
            user.set_password('user12345')
            user.save()
            self.stdout.write('  User account created: user / user12345')
        else:
            self.stdout.write('  User account already exists')

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
