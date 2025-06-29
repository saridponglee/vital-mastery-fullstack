# Generated by Django 5.0.3 on 2025-06-26 01:27

import django.db.models.deletion
import parler.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("content", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="author",
            field=models.ForeignKey(
                help_text="Article author",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="articles",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="articletag",
            name="article",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="content.article"
            ),
        ),
        migrations.AddField(
            model_name="articletranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="content.article",
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="category",
            field=models.ForeignKey(
                blank=True,
                help_text="Article category",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="articles",
                to="content.category",
            ),
        ),
        migrations.AddField(
            model_name="categorytranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="content.category",
            ),
        ),
        migrations.AddField(
            model_name="articletag",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="content.tag"
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                help_text="Tags for this article",
                related_name="articles",
                through="content.ArticleTag",
                to="content.tag",
            ),
        ),
        migrations.AddField(
            model_name="tagtranslation",
            name="master",
            field=parler.fields.TranslationsForeignKey(
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="translations",
                to="content.tag",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="articletranslation",
            unique_together={("language_code", "master")},
        ),
        migrations.AlterUniqueTogether(
            name="categorytranslation",
            unique_together={("language_code", "master")},
        ),
        migrations.AlterUniqueTogether(
            name="articletag",
            unique_together={("article", "tag")},
        ),
        migrations.AlterUniqueTogether(
            name="tagtranslation",
            unique_together={("language_code", "master")},
        ),
    ]
