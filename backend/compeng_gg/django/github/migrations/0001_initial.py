import django.db.models.deletion

from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.PositiveBigIntegerField(editable=False, primary_key=True, serialize=False)),
                ('login', models.CharField(editable=False, max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hook',
            fields=[
                ('id', models.PositiveBigIntegerField(editable=False, primary_key=True, serialize=False)),
                ('installation_target_id', models.PositiveBigIntegerField(editable=False)),
                ('installation_target_content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.PositiveBigIntegerField(editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(editable=False, max_length=150)),
                ('full_name', models.CharField(editable=False, max_length=150, unique=True)),
                ('owner_id', models.PositiveBigIntegerField(editable=False)),
                ('owner_content_type', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'repository',
                'verbose_name_plural': 'repositories',
            },
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relative', models.TextField(editable=False)),
                ('repository', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='paths', to='github.repository')),
            ],
        ),
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sha1', models.CharField(editable=False, max_length=150)),
                ('paths_added', models.ManyToManyField(editable=False, related_name='commits_added', to='github.path')),
                ('paths_modified', models.ManyToManyField(editable=False, related_name='commits_modified', to='github.path')),
                ('paths_removed', models.ManyToManyField(editable=False, related_name='commits_removed', to='github.path')),
                ('repository', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='commits', to='github.repository')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.PositiveBigIntegerField(editable=False, primary_key=True, serialize=False)),
                ('login', models.CharField(editable=False, max_length=150, unique=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='github', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.PositiveBigIntegerField(editable=False, primary_key=True, serialize=False)),
                ('slug', models.SlugField(editable=False)),
                ('name', models.TextField(editable=False, max_length=150)),
                ('organization', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='teams', to='github.organization')),
                ('members', models.ManyToManyField(editable=False, related_name='teams', to='github.user')),
            ],
        ),
        migrations.CreateModel(
            name='Push',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ref', models.CharField(editable=False, max_length=150)),
                ('commits', models.ManyToManyField(editable=False, related_name='pushes', to='github.commit')),
                ('head_commit', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='pushes_head', to='github.commit')),
                ('repository', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='pushes', to='github.repository')),
                ('sender', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='pushes', to='github.user')),
            ],
            options={
                'verbose_name': 'push',
                'verbose_name_plural': 'pushes',
            },
        ),
        migrations.AddField(
            model_name='organization',
            name='members',
            field=models.ManyToManyField(editable=False, related_name='organizations', to='github.user'),
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(editable=False)),
                ('received', models.DateTimeField(auto_now_add=True)),
                ('event', models.CharField(editable=False, max_length=150)),
                ('payload', models.JSONField(editable=False)),
                ('object_id', models.PositiveBigIntegerField(blank=True, editable=False, null=True)),
                ('content_type', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('hook', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='deliveries', to='github.hook')),
            ],
            options={
                'verbose_name': 'delivery',
                'verbose_name_plural': 'deliveries',
                'ordering': ['-received'],
                'indexes': [models.Index(fields=['content_type', 'object_id'], name='github_deli_content_d1d93b_idx')],
                'unique_together': {('content_type', 'object_id'), ('hook', 'uuid')},
            },
        ),
        migrations.AddIndex(
            model_name='repository',
            index=models.Index(fields=['owner_content_type', 'owner_id'], name='github_repo_owner_c_2edb92_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='path',
            unique_together={('repository', 'relative')},
        ),
        migrations.AlterUniqueTogether(
            name='commit',
            unique_together={('repository', 'sha1')},
        ),
        migrations.AlterUniqueTogether(
            name='team',
            unique_together={('organization', 'slug')},
        ),
    ]
