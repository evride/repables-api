from peewee import *
from datetime import datetime
from config import DATABASE
from playhouse.migrate import *

pg_db = PostgresqlDatabase(DATABASE['NAME'], user=DATABASE['USER'], password=DATABASE['PASSWORD'], host=DATABASE['HOST'], port=DATABASE['PORT'], autorollback=True)
#migrator = PostgresqlMigrator(pg_db)

class User(Model):
    username = CharField(max_length=64, unique=True)
    email = CharField(max_length=128, unique=True)
    password = CharField(max_length=255, default='')
    fullname = CharField(max_length=128, null=True)
    location = CharField(max_length=128, null=True)
    company = CharField(max_length = 128, null=True)
    biography = TextField(null=True)
    website = TextField(null=True)
    birthdate = DateTimeField(null=True)
    email_public = BooleanField(default=False)
    display_birthday = BooleanField(default=False)
    hide_inappropriate = BooleanField(default=True)
    enabled = BooleanField(default=False)
    type = CharField(max_length=11, default="user") #EnumField('administrator', 'moderator', 'user')
    remote_address = CharField(max_length=39, null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    class Meta:
        database = pg_db
        db_table = "users"
    def __str__(self):
        return self.username

class Item(Model):
    user = ForeignKeyField(User)
    revision_id = IntegerField(default=1)
    name = CharField(max_length=255)
    description = TextField(null=True)
    instructions = TextField(null=True)
    tags = TextField(null=True)
    license = CharField(max_length=10) #EnumField
    version = CharField(max_length=50)
    flagged_at = DateTimeField(null=True)
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    class Meta:
        database = pg_db
        db_table = "items"
    def __str__(self):
            return self.name

class ItemRevision(Model):
    item = ForeignKeyField(Item, null=True)
    user = ForeignKeyField(User)
    name = CharField(max_length=255, default="")
    description = TextField(null=True, default="")
    instructions = TextField(null=True, default="")
    tags = TextField(null=True, default="")
    license = CharField(max_length=10, default="") #Enum
    version = CharField(max_length=50, default="")
    deleted_at = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    class Meta:
        database = pg_db
        db_table = "item_revisions"
    def __str__(self):
        return self.name

class ItemImage(Model):
    revision_id = IntegerField()
    path = CharField(max_length=255, default ="")
    upload_id = IntegerField()
    width = IntegerField()
    height = IntegerField()
    type = CharField(max_length=64, default ="")
    class Meta:
        database = pg_db
        db_table = "item_images"
    def __str__(self):
        return self.type

class ItemUpload(Model):
    uploader = ForeignKeyField(User, null=True)
    file_location = CharField(max_length=128)
    filename = CharField(max_length=256)
    file_extension = CharField(max_length=16, null=True) #adding the nullable for testing
    size = IntegerField()#filesize Number (file size in number of bytes)
    mimetype = CharField(max_length=64)#mimetype  varchar(64) NULLABLE (ex: image/png)
    revision_id = ForeignKeyField(ItemRevision)
	#type varchar(1) NULLABLE (either "primary", "secondary") //define it but mostly ignore for now
	#hash String(40) NULLABLE (file hash, md5 ) //define but can ignore for now
	#enabled Boolean
	#deleted Boolean
	#date_uploaded Timestamp
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
	#remote_address varchar(39)id #adding the nullable for testing
    class Meta:
        database = pg_db
        db_table = "item_uploads"
    def __str__(self):
        return self.filename

class ItemView(Model):
    item = ForeignKeyField(Item)
    revision = ForeignKeyField(ItemRevision)
    user = ForeignKeyField(User, null = True)
    timestamp =  DateTimeField(default=datetime.now)
    remote_address = CharField(max_length = 64)
    class Meta:
        database = pg_db
        db_table = "item_views" 

class File(Model):
    item = ForeignKeyField(Item, null = True)
    revision = ForeignKeyField(ItemRevision, null = True)
    name = CharField(max_length = 255)
    downloadable = BooleanField(default=False)
    sort_order = IntegerField()
    render = BooleanField(default=True)
    preview = BooleanField(default=True)

    class Meta:
            database = pg_db
            db_table = "files"


class Download(Model):
    item = ForeignKeyField(Item, null=True)
    revision = ForeignKeyField(ItemRevision, null=True)
    file = ForeignKeyField(File, null=True)
    user = ForeignKeyField(User, null=True)
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = pg_db
        db_table = "downloads"


class PasswordReset(Model):
    user = ForeignKeyField(User)
    reset_key = CharField(max_length=32)
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = pg_db
        db_table = "reset_passwords"

class Upload(Model):
    user = ForeignKeyField(User)
    revision = ForeignKeyField(ItemRevision, null=True)
    file_location = CharField(max_length=256)
    filename = CharField(max_length=256)
    file_extension = CharField(max_length=10)
    filesize = IntegerField()
    mimetype = CharField(max_length=128)
    hash = CharField(max_length=256)
    remote_address = CharField(max_length=39)
    uploaded_at = DateTimeField(default=datetime.now)
    class Meta:
        database = pg_db
        db_table = "uploads"