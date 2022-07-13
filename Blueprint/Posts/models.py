from tortoise import fields, models, Tortoise
from Blueprint.Users.models import Users


class Posts(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100)
    text = fields.TextField()
    author: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        'models.Users', related_name='posts'
    )

    def __str__(self):
        return self.title