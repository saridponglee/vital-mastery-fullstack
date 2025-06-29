# Generated by Django 5.0.3 on 2025-06-26 01:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("content", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Comment",
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
                (
                    "content",
                    models.TextField(help_text="Comment content", max_length=2000),
                ),
                (
                    "is_approved",
                    models.BooleanField(
                        default=True,
                        help_text="Whether the comment is approved for display",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Comment",
                "verbose_name_plural": "Comments",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="Like",
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
            ],
            options={
                "verbose_name": "Like",
                "verbose_name_plural": "Likes",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Bookmark",
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
                (
                    "article",
                    models.ForeignKey(
                        help_text="Article that was bookmarked",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookmarks",
                        to="content.article",
                    ),
                ),
            ],
            options={
                "verbose_name": "Bookmark",
                "verbose_name_plural": "Bookmarks",
                "ordering": ["-created_at"],
            },
        ),
    ]
