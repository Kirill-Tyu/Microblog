from sanic import Blueprint
from sanic import response
from Blueprint.Users.forms import LoginForm, RegisterForm

from .models import Users
from server import jinja
from server import PasswordHasher, VerifyMismatchError
from server import protected, inject_user


bp = Blueprint('users', url_prefix='users')


@bp.route('/auth', methods=['GET'])
async def bp_login(request):
    lform = LoginForm(request)
    return jinja.render("forms.html", request, form=lform, type_form='LoginForm')

@bp.route('/logout', methods=['GET'])
@protected(bp)
async def bp_logout(request):
    #Удалим JWT cookies и авторизация закончится
    responseHTTP = response.redirect('/users/auth')
    if request.cookies.get('access_token_signature') and request.cookies.get('jwt_access_cookies'):
        del responseHTTP.cookies['access_token_signature']
        del responseHTTP.cookies['jwt_access_cookies']
    else:
        del responseHTTP.cookies['jwt_access_cookies']
    return responseHTTP

@bp.route('/register', methods=['GET', 'POST'])
async def bp_register(request):
    rform = RegisterForm(request)
    if request.method == 'POST' and rform.validate():
        name = rform.name.data
        pwd = rform.password.data
        if (await Users.exists(username=name)):
            jinja.flash(request, 'Такой пользователь уже есть!', 'error')
            return jinja.render("forms.html", request, form=rform)
        else:
            ph = PasswordHasher()
            hash = ph.hash(pwd)
            u = await Users.create(username=name, password_hash=hash)
            await u.save()
        return response.redirect('/users/auth')
    return jinja.render("forms.html", request, form=rform)

@bp.route('/profile', methods=['GET'], name='my_data')
@inject_user()
@protected(bp)
async def bp_profile(request, user):
    #список всех пользователей
    users_all_db = await Users.exclude(username=user)
    #список пользователей на которых подписан пользователь
    users_follow = await Users.filter(follower=user.user_id)
    return jinja.render("profile.html", request, user=user, users_all=users_all_db, users_follow=users_follow)

#подписывемся на пользователя
@bp.route('/profile/follow/<username>', methods=['GET'], name='follow')
@inject_user()
@protected(bp)
async def bp_profile(request, username, user):
    followed = await Users.get(username=username)
    follower = await Users.get(username=user)
    await follower.followed.add(followed)

    return response.redirect('/users/profile')

#подписывемся на пользователя
@bp.route('/profile/unfollow/<username>', methods=['GET'], name='unfollow')
@inject_user()
@protected(bp)
async def bp_profile(request, username, user):
    followed = await Users.get(username=username)
    follower = await Users.get(username=user)
    await follower.followed.remove(followed)

    return response.redirect('/users/profile')