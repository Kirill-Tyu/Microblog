from tortoise import fields, models, Tortoise


class Users(models.Model):
    user_id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    password_hash = fields.CharField(max_length=128, null=True)
    posts: fields.ReverseRelation['Posts']

    follower: fields.ManyToManyRelation['Users'] = fields.ManyToManyField(
        'models.Users',
        forward_key='follower',
        backward_key='followed',
        related_name='followed'
    )
    followed: fields.ManyToManyRelation['Users']

    def __str__(self):
        return self.username

    def to_dict(self):
        return {"user_id": self.user_id, "username": self.username}

