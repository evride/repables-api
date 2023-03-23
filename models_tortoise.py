from tortoise.models import Model
from tortoise import fields
from datetime import datetime


class TimestampMixin():
    created_at = fields.DatetimeField(null=True, auto_now_add=True)
    updated_at = fields.DatetimeField(null=True, auto_now=True)

class SoftDeleteModel(Model):
    deleted_at = fields.DatetimeField(null=True)

    async def hard_delete(self):
        await super().delete()
    async def soft_delete(self):
        self.deleted_at = datetime.now()
        await self.save()        
    async def delete(self):
        await self.soft_delete()
    


class User(TimestampMixin, SoftDeleteModel):
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    email = fields.CharField(max_length=128, unique=True)
    password = fields.CharField(max_length=255, default='')
    fullname = fields.CharField(max_length=128, null=True)
    location = fields.CharField(max_length=128, null=True)
    company = fields.CharField(max_length = 128, null=True)
    biography = fields.TextField(null=True)
    website = fields.TextField(null=True)
    birthdate = fields.DateField(null=True)
    email_public = fields.BooleanField(default=False)
    display_birthday = fields.BooleanField(default=False)
    hide_inappropriate = fields.BooleanField(default=True)
    enabled = fields.BooleanField(default=False)
    type = fields.CharField(max_length=11, default="user") #EnumField('administrator', 'moderator', 'user')
    remote_address = fields.CharField(max_length=39, null=True)

    # Defining ``__str__`` is also optional, but gives you pretty
    # represent of model in debugger and interpreter
    class Meta:
        table = "users"
    def __str__(self):
        return self.username

class Item(TimestampMixin, SoftDeleteModel):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField('models.User', related_name='items')
    revision = fields.ForeignKeyField('models.ItemRevision')
    upload_session_id = fields.IntField(null=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    instructions = fields.TextField(null=True)
    tags = fields.TextField(null=True)
    license = fields.CharField(max_length=10) #EnumField
    version = fields.CharField(max_length=50)
    flagged_at = fields.DatetimeField(null=True)
    item_likes = fields.IntField(default=0)
    item_dislikes = fields.IntField(default=0)
    item_views = fields.IntField(default=0)

    class Meta:
        table = "items"
    def __str__(self):
        return self.name


class ItemRevision(TimestampMixin, SoftDeleteModel):
    item = fields.ForeignKeyField('models.Item', null=True, related_name='revisions')
    user = fields.ForeignKeyField('models.User')
    name = fields.CharField(max_length=255, default="")
    description = fields.TextField(null=True, default="")
    instructions = fields.TextField(null=True, default="")
    tags = fields.TextField(null=True, default="")
    license = fields.CharField(max_length=10, default="") #Enum
    version = fields.CharField(max_length=50, default="")
    upload_session_id = fields.IntField(null=True)
    class Meta:
        table = "item_revisions"
    def __str__(self):
        return self.name


class ItemImage(Model):
    revision = fields.ForeignKeyField('models.ItemRevision', null=True, related_name='images')
    path = fields.CharField(max_length=255, default ="")
    upload_id = fields.IntField()
    width = fields.IntField()
    height = fields.IntField()
    type = fields.CharField(max_length=64, default ="")
    class Meta:
        table = "item_images"
    def __str__(self):
        return self.type



class ItemLike(Model):
    item = fields.ForeignKeyField('models.Item', related_name='likes')
    user = fields.ForeignKeyField('models.User', related_name='likes')
    score = fields.IntField()
    remote_address = fields.CharField(max_length = 64)

    class Meta:
        table = "item_likes"
    def __str__(self):
        return self.type


class ItemUpload(TimestampMixin, Model):
    uploader = fields.ForeignKeyField('models.User', null=True)
    file_location = fields.CharField(max_length=128)
    filename = fields.CharField(max_length=256)
    file_extension = fields.CharField(max_length=16, null=True) #adding the nullable for testing
    size = fields.IntField()#filesize Number (file size in number of bytes)
    mimetype = fields.CharField(max_length=64)#mimetype  varchar(64) NULLABLE (ex: image/png)
    upload_session_id = fields.IntField(null=True)
    revision = fields.ForeignKeyField('models.ItemRevision', null=True, related_name='uploads')
	#type varchar(1) NULLABLE (either "primary", "secondary") //define it but mostly ignore for now
	#hash String(40) NULLABLE (file hash, md5 ) //define but can ignore for now
	#enabled Boolean
	#deleted Boolean
	#date_uploaded Timestamp
	#remote_address varchar(39)id #adding the nullable for testing
    class Meta:
        table = "item_uploads"
    def __str__(self):
        return self.filename

class ItemView(Model):
    item = fields.ForeignKeyField('models.Item')
    revision = fields.ForeignKeyField('models.ItemRevision', null=True)
    user = fields.ForeignKeyField('models.User', null = True, related_name='item_views')
    timestamp =  fields.DatetimeField(default=datetime.now)
    remote_address = fields.CharField(max_length = 64)
    class Meta:
        table = "item_views" 

class File(Model):
    revision = fields.ForeignKeyField('models.ItemRevision', null = True, related_name='files')
    name = fields.CharField(max_length = 255)
    downloadable = fields.BooleanField(default=False)
    sort_order = fields.IntField()
    render = fields.BooleanField(default=True)
    preview = fields.BooleanField(default=True)

    class Meta:
        table = "files"


class Download(Model):
    item = fields.ForeignKeyField('models.Item', null=True)
    revision = fields.ForeignKeyField('models.ItemRevision', null=True)
    file = fields.ForeignKeyField('models.File', null=True)
    user = fields.ForeignKeyField('models.User', null=True, related_name='downloads')
    created_at = fields.DatetimeField(default=datetime.now)
    class Meta:
        table = "downloads"


class PasswordReset(Model):
    user = fields.ForeignKeyField('models.User')
    reset_key = fields.CharField(max_length=32)
    created_at = fields.DatetimeField(default=datetime.now)
    class Meta:
        table = "reset_passwords"
