from sanic import Blueprint, response
from Blueprint.Posts.forms import AddPostForm
from server import jinja
from .models import Posts
from Blueprint.Users.models import Users
from server import protected, inject_user

bp = Blueprint('posts', url_prefix='posts')

def get_list_posts(query_res, my_list):
    res_list = my_list
    for element in query_res:
        for post in element.posts:
            l=[]
            l.append(post.title)
            l.append(post.text)
            l.append(element.username)
            res_list.append(l)
    return res_list

@bp.route('/', name='all_posts')
@inject_user()
@protected(bp)
async def bp_root(request, user):
    posts = await Users.all().prefetch_related('posts')
    posts_all_db = get_list_posts(posts,[])

    return jinja.render("posts.html", request, user=user, posts=posts_all_db, my_posts='many')

@bp.route('/my_posts', name='my_posts')
@inject_user()
@protected(bp)
async def bp_my_posts(request, user):
    #будут выводиться собственные посты и посты пользователей на которых подписан текущий пользователь
    f_post = await Users.filter(follower=int(user.user_id)).prefetch_related('posts')
    posts_all_db = get_list_posts(f_post, [])

    own_post = await Users.filter(user_id=int(user.user_id)).prefetch_related('posts')
    posts_all_db = get_list_posts(own_post, posts_all_db)

    return jinja.render("posts.html", request, user=user, posts=posts_all_db, my_posts = 'single')

@bp.route('/<username>', name='user_posts')
@inject_user()
@protected(bp)
async def bp_users_posts(request, username, user):
    posts = await Users.filter(username=username).prefetch_related('posts')
    posts_all_db = get_list_posts(posts, [])
    if len(posts_all_db) == 0:
        jinja.flash(request, 'У пользователя нет постов!', 'error')
    return jinja.render("posts.html", request, user=user, posts=posts_all_db, my_posts='single')

@bp.route('/add_post', methods=['GET', 'POST'], name='add_post')
@inject_user()
@protected(bp)
async def bp_add_post(request, user):
    rform = AddPostForm(request)
    if request.method == 'POST' and rform.validate():
        title = rform.title.data
        text = rform.text.data
        post = await Posts.create(title=title, text=text, author=user)
        await post.save()
        return response.redirect('/posts')
    return jinja.render("forms.html", request, form=rform, user=user)