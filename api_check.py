import requests
register_url = 'http://127.0.0.1:8000/api/register'
login_url = 'http://127.0.0.1:8000/api/login'
user_url = 'http://127.0.0.1:8000/api/user'
data = {
    "email": "ravindra@gmail.com",
    "password": "ravi",
}


def login_response():
    return requests.post(url=login_url, data=data)


def get_response():
    return requests.get(url=user_url, data='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
                                           'eyJpZCI6MTUsImV4cCI6MTY2OTU2NTg2OSwiaWF0IjoxNjY5NTY1NTY5fQ.'
                                           'U_FIFIdN4l_mU25Mn56JJv4bk2awQExtd-mmJraMzSc')

print(login_response().json())
# print(get_response().json())