from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Hook(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, editable=False)

    installation_target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        editable=False,
    )
    installation_target_id = models.PositiveBigIntegerField(
        editable=False,
    )
    installation_target = GenericForeignKey(
        "installation_target_content_type",
        "installation_target_id",
    )

    def __str__(self):
        return f"{self.id}"

class Delivery(models.Model):

    hook = models.ForeignKey(
        Hook,
        on_delete=models.CASCADE,
        editable=False,
        related_name="deliveries",
    )
    uuid = models.UUIDField(editable=False)
    received = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length=150, editable=False)
    payload = models.JSONField(editable=False)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        editable=False,
    )
    object_id = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        editable=False,
    )
    content_object = GenericForeignKey("content_type", "object_id")

    @property
    def push(self):
        return Push.objects.get(
            id=self.object_id,
        )

    def __str__(self):
        return f"{self.uuid} {self.event}"

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
        ordering = ["-received"]
        unique_together = [
            ["hook", "uuid"],
            ["content_type", "object_id"],
        ]
        verbose_name = "delivery"
        verbose_name_plural = "deliveries"

class Repository(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=150, editable=False)
    full_name = models.CharField(max_length=150, editable=False, unique=True)

    owner_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        editable=False,
    )
    owner_id = models.PositiveBigIntegerField(
        editable=False,
    )
    owner = GenericForeignKey("owner_content_type", "owner_id")

    def __str__(self):
        return f"{self.full_name}"

    class Meta:
        indexes = [
            models.Index(fields=["owner_content_type", "owner_id"]),
        ]
        verbose_name = "repository"
        verbose_name_plural = "repositories"

class User(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="github",
    )
    id = models.PositiveBigIntegerField(primary_key=True, editable=False)
    login = models.CharField(max_length=150, editable=False, unique=True)

    owned_repositories = GenericRelation(
        Repository,
        content_type_field="owner_content_type",
        object_id_field="owner_id",
    )

    def __str__(self):
        return f"{self.login}"

class Path(models.Model):

    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        editable=False,
        related_name="paths",
    )
    relative = models.TextField(editable=False)

    def __str__(self):
        return f"{self.relative}"

    class Meta:
        unique_together = ["repository", "relative"]

class Commit(models.Model):

    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        editable=False,
        related_name="commits",
    )
    sha1 = models.CharField(max_length=150, editable=False)
    paths_added = models.ManyToManyField(
        Path,
        editable=False,
        related_name="commits_added",
    )
    paths_modified = models.ManyToManyField(
        Path,
        editable=False,
        related_name="commits_modified",
    )
    paths_removed = models.ManyToManyField(
        Path,
        editable=False,
        related_name="commits_removed",
    )

    def __str__(self):
        return f"{self.sha1}"

    class Meta:
        unique_together = ["repository", "sha1"]

class Push(models.Model):

    ref = models.CharField(max_length=150, editable=False)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        related_name="pushes",
    )
    head_commit = models.ForeignKey(
        Commit,
        on_delete=models.CASCADE,
        editable=False,
        related_name="pushes_head",
    )
    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        editable=False,
        related_name="pushes",
    )
    commits = models.ManyToManyField(
        Commit,
        editable=False,
        related_name="pushes",
    )

    @property
    def delivery(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return Delivery.objects.get(
            content_type=content_type,
            object_id=self.id,
        )

    def __str__(self):
        return f"{self.sender.login} {self.head_commit}"

    class Meta:
        verbose_name = "push"
        verbose_name_plural = "pushes"

class Organization(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, editable=False)
    login = models.CharField(max_length=150, editable=False, unique=True)
    members = models.ManyToManyField(
        User,
        editable=False,
        related_name="organizations",
    )

    owned_repositories = GenericRelation(
        Repository,
        content_type_field="owner_content_type",
        object_id_field="owner_id",
    )

    def __str__(self):
        return f"{self.login}"

class Team(models.Model):

    id = models.PositiveBigIntegerField(primary_key=True, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        editable=False,
        related_name="teams",
    )
    slug = models.SlugField(editable=False)
    name = models.TextField(max_length=150, editable=False)
    members = models.ManyToManyField(
        User,
        editable=False,
        related_name="teams",
    )

    def __str__(self):
        return f"{self.organization}/{self.slug}"

    class Meta:
        unique_together = ["organization", "slug"]
