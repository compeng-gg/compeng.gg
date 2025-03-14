import pytest
from django.core.exceptions import ValidationError
from github_app.utils import create_student_sub_team

def test_create_student_sub_team_success(mocker):
    mock_api = mocker.patch('myapp.github_api.GitHubRestAPI')  # Mock GitHubRestAPI
    mock_api.return_value.create_child_team_for_org.return_value = {"id": 123}

    result = create_student_sub_team("Team Name", "student-repo-slug")

    mock_api.return_value.create_child_team_for_org.assert_called_once_with("Team Name", "student-repo-slug")
    assert result is None


def test_create_student_sub_team_failure(mocker):
    mock_api = mocker.patch('myapp.github_api.GitHubRestAPI')
    mock_api.return_value.create_child_team_for_org.return_value = None

    with pytest.raises(ValidationError):
        create_student_sub_team("Team Name", "student-repo-slug")
