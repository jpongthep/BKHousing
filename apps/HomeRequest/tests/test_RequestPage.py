from django.urls import reverse
from django.contrib.auth import get_user_model
import pytest

from apps.UserData.models import User
from apps.HomeRequest.models import HomeRequest


def login_user():
    username = "test_user"
    password = "bar"
    logined_user = User.objects.create_user(username=username, password=password)
    # perm = Permission.objects.get(codename='can_approve_requests')
    # user.user_permissions.add(perm)
    return logined_user


@pytest.mark.parametrize('param',[
    ('login'),
])
def test_anonymous_views(client,param):
    temp_url = reverse(param)
    resp = client.get(temp_url)
    assert resp.status_code == 200    

@pytest.mark.django_db
def test_user_login(client,create_test_user,user_data):
    assert User.objects.count() == 1
    login_url = reverse('login')
    resp = client.post(login_url, data = user_data)
    assert resp.status_code == 200
    # assert resp.url == reverse('blank')

import pytest
from django.contrib.auth.models import User, Group
from django.test import RequestFactory
from ..views import TeacherView

# @pytest.mark.django_db
# def test_authenticated_user(self, rf):
#     request = rf.get('/myproj/myapp/teacher/')
#     user = User.objects.create_user('person', 'person@example.com', 'password')
#     parents = Group.objects.create(name='parents')
#     user.groups.add(parents)
#     user.save()
#     parents.save()
#     request.user = user
#     response = TeacherView.as_view()(request)

#     assert response.status_code != 200