from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_administrativeprocess_managementplan_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiaryEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('content', models.TextField()),
                ('notes', models.TextField(blank=True)),
                ('observations', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Rascunho'), ('review', 'Em verificacao'), ('closed', 'Fechado')], default='draft', max_length=12)),
                ('verified_by', models.CharField(blank=True, max_length=120)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='diary_entries', to='core.classsubject')),
                ('school_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='diary_entries', to='core.schoolclass')),
            ],
            options={
                'ordering': ['-date', '-updated_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='diaryentry',
            constraint=models.UniqueConstraint(fields=('class_subject', 'date'), name='unique_diary_per_subject_date'),
        ),
    ]
