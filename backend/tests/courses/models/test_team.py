import courses.models as db
import pytest
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db import IntegrityError, transaction
from django.conf import settings


def create_offering() -> db.Offering:
    intitution = db.Institution.objects.create()
    course = db.Course.objects.create(institution=intitution)
    offering = db.Offering.objects.create(
        course=course,
        start=datetime.now(),
        end=datetime.now() + timedelta(days=100),
        active=True
    )

    return offering


@pytest.mark.django_db
def test_team_create_and_retrieve():
    offering = create_offering()
    team_name = 'Team 1'

    team = db.Team.objects.create(offering=offering, name=team_name)

    retrieved_team = db.Team.objects.get(id=team.id)

    assert retrieved_team == team


@pytest.mark.django_db
def test_team_add_retrieve_and_remove_members():
    offering = create_offering()
    
    team = db.Team.objects.create(offering=offering, name='Team 1')
    
    student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)

    # Number of members should be 0 initially
    assert team.members.count() == 0

    user_1 = User.objects.create(username='Nick')
    user_2 = User.objects.create(username='Abdullah')

    # Create an enrollment with the team
    enrollment_1 = db.Enrollment.objects.create(user=user_1, role=student_role)

    team.members.add(enrollment_1)

    assert team.members.count() == 1

    enrollment_2 = db.Enrollment.objects.create(user=user_2, role=student_role)

    team.members.add(enrollment_2)

    assert team.members.count() == 2

    retrieved_team = db.Team.objects.prefetch_related('members').get(id=team.id)

    team_members_set = set(retrieved_team.members.all())
    expected_team_members_set = {
        enrollment_1,
        enrollment_2,
    }

    assert team_members_set == expected_team_members_set
  

@pytest.mark.django_db
def test_team_remove_members():
    offering = create_offering()
    
    team = db.Team.objects.create(offering=offering, name='Team 1')

    user_1 = User.objects.create(username='Nick')
    user_2 = User.objects.create(username='Abdullah')
    
    student_role = db.Role.objects.create(kind=db.Role.Kind.STUDENT, offering=offering)

    enrollment_1 = db.Enrollment.objects.create(user=user_1, role=student_role)
    enrollment_2 = db.Enrollment.objects.create(user=user_2, role=student_role)

    team.members.add(enrollment_1)
    team.members.add(enrollment_2)

    assert team.members.count() == 2

    # Remove enrollment 1 from team
    team.members.remove(enrollment_1)
    enrollment_1.save()

    retrieved_team = db.Team.objects.prefetch_related('members').get(id=team.id)

    team_members_set = set(retrieved_team.members.all())

    expected_team_members_set = {
        enrollment_2,
    }

    assert team_members_set == expected_team_members_set

    # Remove enrollment 2 from team
    team.members.remove(enrollment_2)
    enrollment_1.save()

    assert team.members.count() == 0


@pytest.mark.django_db
def test_team_retrieve_teams_for_offering():
    offering = create_offering()

    assert offering.teams.count() == 0
    
    team_1 = db.Team.objects.create(offering=offering, name='Team 1')
    team_2 = db.Team.objects.create(offering=offering, name='Team 2')

    assert offering.teams.count() == 2
    
    teams_set = set(offering.teams.all())
    expected_teams_set = {
        team_1,
        team_2,
    }

    assert teams_set == expected_teams_set


@pytest.mark.django_db
def test_team_duplicate_names_for_offering_raises_error():
    offering = create_offering()

    db.Team.objects.create(offering=offering, name='Team 1')
    db.Team.objects.create(offering=offering, name='Team 2')

    assert db.Team.objects.count() == 2

    # We expect IntegrityError to be raised
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            db.Team.objects.create(offering=offering, name='Team 2')

    assert db.Team.objects.count() == 2


@pytest.mark.django_db
def test_team_duplicate_names_for_different_offerings_succeeds():
    offering_1 = create_offering()
    offering_2= create_offering()

    db.Team.objects.create(offering=offering_1, name='Team 1')
    db.Team.objects.create(offering=offering_2, name='Team 1')

    assert db.Team.objects.count() == 2
