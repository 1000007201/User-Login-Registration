import mongoengine as me


class Users(me.Document):
    UserName = me.StringField(max_length=50, required=True)
    Name = me.StringField(max_length=50, required=True)
    Email = me.StringField()
    Password = me.StringField(max_length=40)
    Is_active = me.BooleanField(default=False)
