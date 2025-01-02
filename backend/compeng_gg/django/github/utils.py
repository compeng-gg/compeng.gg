from compeng_gg.django.github.models import (
    Commit,
    Delivery,
    Hook,
    Organization,
    Path,
    Push,
    Repository,
    Team,
    User,
)
from django.conf import settings

def _get_or_create_organization(data):
    if "type" in data:
        assert data["type"] == "Organization"
    login = data["login"]
    organization, created = Organization.objects.get_or_create(
        id=data["id"],
        defaults={
            "login": login
        },
    )
    if not created:
        if organization.login != login:
            organization.login = login
            organization.save()
    return organization

def _get_or_create_user(data):
    if "type" in data:
        assert data["type"] == "User"
    login = data["login"]
    user, created = User.objects.get_or_create(
        id=data["id"],
        defaults={
            "login": login
        },
    )
    if not created:
        if user.login != login:
            user.login = login
            user.save()
    return user

def _get_or_create_organization_or_user(data):
    match data["type"]:
        case "Organization":
            return _get_or_create_organization(data)
        case "User":
            return _get_or_create_user(data)
        case _:
            raise AssertionError("Expected Organization or User")

def _get_or_create_repository(data):
    name = data["name"]
    full_name = data["full_name"]
    owner = _get_or_create_organization_or_user(data["owner"])
    repository, created = Repository.objects.get_or_create(
        id=data["id"],
        defaults={
            "name": name,
            "full_name": full_name,
            "owner": owner,
        },
    )
    if not created:
        changed = False
        if repository.name != name:
            repository.name = name
            changed = True
        if repository.full_name != full_name:
            repository.full_name = full_name
            changed = True
        if repository.owner != owner:
            repository.owner = owner
            changed = True
        if changed:
            repository.save()
    return repository

def _get_or_create_path(repository, relative):
    path, created = Path.objects.get_or_create(
        repository=repository,
        relative=relative,
    )
    return path

def _get_or_create_commit(repository, data):
    sha1 = data["id"]
    commit, created = Commit.objects.get_or_create(
        repository=repository,
        sha1=sha1,
    )
    for relative in data["added"]:
        path = _get_or_create_path(repository, relative)
        commit.paths_added.add(path)
    for relative in data["modified"]:
        path = _get_or_create_path(repository, relative)
        commit.paths_modified.add(path)
    for relative in data["removed"]:
        path = _get_or_create_path(repository, relative)
        commit.paths_removed.add(path)
    return commit

def _create_push(payload):
    sender = _get_or_create_organization_or_user(payload["sender"])
    ref = payload["ref"]
    repository = _get_or_create_repository(payload["repository"])
    head_commit = _get_or_create_commit(repository, payload["head_commit"])
    push = Push.objects.create(
        head_commit=head_commit,
        sender=sender,
        ref=ref,
        repository=repository
    )
    for data in payload["commits"]:
        commit = _get_or_create_commit(repository, data)
        push.commits.add(commit)
    return push

def _get_or_create_team(organization, data):
    name = data["name"]
    slug = data["slug"]
    team, created = Team.objects.get_or_create(
        id=data["id"],
        defaults={
            "organization": organization,
            "slug": slug,
            "name": name,
        },
    )
    if not created:
        changed = False
        if team.name != name:
            team.name = name
            changed = True
        if team.slug != slug:
            team.slug = slug
            changed = True
        if team.organization != organization:
            team.organization = organization
            changed = True
        if changed:
            team.save()
    return team

def _sync_team_membership(payload):
    action = payload["action"]
    organization = _get_or_create_organization(payload["organization"])
    sender = _get_or_create_organization_or_user(payload["sender"])
    member = _get_or_create_user(payload["member"])
    team = _get_or_create_team(organization, payload["team"])
    if action == "added":
        team.members.add(member)
    elif action == "removed":
        team.members.remove(member)

def _sync_membership(payload):
    scope = payload["scope"]
    if scope == "team":
        _sync_team_membership(payload)

def _sync_team(payload):
    action = payload["action"]
    organization = _get_or_create_organization(payload["organization"])
    sender = _get_or_create_organization_or_user(payload["sender"])
    if action == "created":
        team = _get_or_create_team(organization, payload["team"])
        team.members.add(sender)
    elif action == "edited":
        _get_or_create_team(organization, payload["team"])
    elif action == "deleted":
        try:
            team = Team.objects.get(id=payload["team"]["id"])
            team.delete()
        except Team.DoesNotExist:
            pass

def _create_hook(payload):
    hook_id = payload["hook_id"]
    hook_data = payload["hook"]
    assert hook_id == hook_data["id"]
    match hook_data["type"]:
        case "Organization":
            organization = _get_or_create_organization(payload["organization"])
            installation_target = organization
        case "Repository":
            repository = _get_or_create_repository(payload["repository"])
            installation_target = repository
        case _:
            raise AssertionError("Expected Organization")
    sender = _get_or_create_organization_or_user(payload["sender"])
    hook = Hook.objects.create(
        id=hook_id,
        installation_target= installation_target,
    )
    return hook

def _remove_urls(data):
    api_url = settings.GITHUB_API_URL
    keys = list(data.keys())
    for key in keys:
        if key == "url" or key.endswith("_url"):
            value = data[key]
            if isinstance(value, str) and value.startswith(api_url):
                del data[key]
        elif isinstance(data[key], dict):
            _remove_urls(data[key])
        elif isinstance(data[key], list):
            for value in data[key]:
                if isinstance(value, dict):
                    _remove_urls(value)

def get_or_create_delivery(hook_id, delivery_uuid, event, payload):
    try:
        hook = Hook.objects.get(id=hook_id)
    except Hook.DoesNotExist:
        if event == "ping":
            hook = _create_hook(payload)
        else:
            raise

    try:
        return Delivery.objects.get(hook=hook, uuid=delivery_uuid)
    except Delivery.DoesNotExist:
        pass

    _remove_urls(payload)

    content_object = None
    if event == "push":
        push = _create_push(payload)
        content_object = push
    elif event == "team":
        _sync_team(payload)
    elif event == "membership":
        _sync_membership(payload)

    Delivery.objects.create(
        hook=hook,
        uuid=delivery_uuid,
        event=event,
        payload=payload,
        content_object=content_object,
    )
