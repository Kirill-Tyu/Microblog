from sanic import Sanic
from sanic.response import json, redirect
from sanic_session import Session, InMemorySessionInterface

from sanic_jinja2 import SanicJinja2
from tortoise.contrib.sanic import register_tortoise

from sanic_jwt import Initialize, protected, exceptions, inject_user
from Blueprint.Users.jwt_utils import AddRedirectToResponse
from Blueprint.Users.models import Users

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


app = Sanic(__name__)
#app.config['SECRET_KEY'] = 'top secret !!!' #для форм
app.config['WTF_CSRF_SECRET_KEY'] = 'protect'

#session = InMemorySessionInterface(expiry=600) - ver.1
session = Session(app, interface=InMemorySessionInterface(expiry=600))

jinja = SanicJinja2(app, session=session)

#jwt token generation
async def authenticate(request, *args, **kwargs):
    name = request.form.get('name')
    pwd = request.form.get('password')
    res = await Users.filter(username=name).values("password_hash","user_id")
    if res:
        try:
            ph = PasswordHasher()
            hash = ph.hash(pwd)
            ph.verify(res[0]['password_hash'], pwd)
        except VerifyMismatchError:
            raise exceptions.AuthenticationFailed("PWD not found.")
    else:
        raise exceptions.AuthenticationFailed("User not found.")
    return dict(user_id=res[0]['user_id'])

async def retrieve_user(request, payload, *args, **kwargs):
    if payload:
        user_id = payload.get('user_id', None)
        user = await Users.get(user_id=user_id)
        return user
    else:
        return None

Initialize(app,
           authenticate=lambda:False,
           retrieve_user=retrieve_user,
           cookie_set=True,
           cookie_split=True,
           cookie_access_token_name='jwt_access_cookies',
           secret = 'New secret_123',
           responses_class=AddRedirectToResponse,
           )

#регистрируем blueprints
from Blueprint.Users.bp_users import bp as bp_users
#import Blueprint.Users.bp_users as bp_users
from Blueprint.Posts.bp_posts import bp as bp_posts

Initialize(bp_users, app=app,
           authenticate=authenticate,
           path_to_authenticate='/users',
           retrieve_user=retrieve_user,
           cookie_set=True,
           cookie_split=True,
           cookie_access_token_name='jwt_access_cookies',
           secret = 'New secret_123',
           responses_class = AddRedirectToResponse,
           debug=True
           )

Initialize(bp_posts, app=app,
           authenticate=lambda:False,
           cookie_set=True,
           cookie_split=True,
           cookie_access_token_name='jwt_access_cookies',
           secret = 'New secret_123',
           )
app.blueprint(bp_users)
app.blueprint(bp_posts)

@app.middleware('response')
async def check_authentication(request, response):
    if response.status in [400, 401]:
        return redirect('/users/auth')

@app.get("/")
@inject_user()
@protected()
async def start_page(request, user):
    return jinja.render("base.html", request, user=user)

register_tortoise(
    app,
    db_url="postgres://postgres:@127.0.0.1:5432/PostDB", modules={"models": ["Blueprint.Users.models",
                                                                             "Blueprint.Posts.models"
                                                                             ]},
    generate_schemas=True
)

app.run(debug=False, workers=4)