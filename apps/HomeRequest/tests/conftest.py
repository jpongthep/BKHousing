from datetime import date
import pytest

from apps.UserData.models import User

@pytest.fixture
def user_data():
    return {
            'email':'abc@abc.com', 
            'username':'user_name', 
            'password':'user_password123',
            'PersonID':'1254685954756'
        }


@pytest.fixture
def create_test_user(user_data):
    test_user = User.objects.create_user(**user_data)
    test_user.set_password(user_data.get('password'))
    return test_user

# @pytest.fixture
# def patient_data(create_test_user):
#     test_user = User.objects.get(username = 'user_name')

#     return {
#                 'FullName' : "NewPatient",
#                 'PersonID' : "1234567890123",
#                 'Date' : date.today(),
#                 'AirforceType' : 1,
#                 'RightMedicalTreatment' : 1,
#                 'CurrentStatus' : 0,
#                 'CurrentTreatment' : 0

#         }    