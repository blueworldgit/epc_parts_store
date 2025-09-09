# Generated migration to change phone_number field from PhoneNumberField to CharField
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0006_auto_20181115_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraddress',
            name='phone_number',
            field=models.CharField(
                blank=True, 
                max_length=32, 
                verbose_name='Phone number',
                help_text='Enter any phone number format'
            ),
        ),
    ]
