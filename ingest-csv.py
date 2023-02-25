import csv
from datetime import datetime, date
from models import Item, User, ItemUpload, ItemRevision
def ingest_items():        
    with open('ingest/data/Repables-Items.csv', mode='r', encoding='utf-8-sig') as csvfile:

        itemsreader = csv.DictReader(csvfile)

        for row in itemsreader:        
            i = Item()
            i.id = row['ItemID']
            i.user_id = row['UserID']
            i.revision_id = row['RevisionID']
            i.name = row['Name']
            i.description = row['Description']
            i.instructions = row['Instructions']
            i.tags = row['Tags']
            i.license = row['License']
            i.version = "1.0"
            i.created_at = datetime.fromisoformat(row['DateCreated'])
            i.updated_at = datetime.fromisoformat(row['DateUpdated'])
            if row['Deleted'] == 1:
                i.deleted_at = datetime.fromisoformat(row['DateUpdated'])
            if row['Flagged'] == 1:
                i.flagged_at =  datetime.fromisoformat(row['DateUpdated'])
            if int(i.user_id) != 0:
                i.save(force_insert=True)

def ingest_item_revisions():        
    with open('ingest/data/Repables-ItemRevisions.csv', mode='r', encoding='utf-8-sig') as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:        
            i = ItemRevision()
            i.id = row['RevisionID']
            #i.item_id = row['ItemID']
            i.user_id = 6
            i.name = row['Name']
            i.description = row['Description']
            i.instructions = row['Instructions']
            i.tags = row['Tags']
            i.license = row['License']
            i.version = row['Version']
            i.upload_session_id = row['UploadSessionID']
            i.save(force_insert=True)

def ingest_uploads():        
    with open('ingest/data/Repables-Uploads.csv', mode='r', encoding='utf-8-sig') as csvfile:

        reader = csv.DictReader(csvfile)

        for row in reader:        
            i = ItemUpload()
            i.id = row['UploadID']
            i.user_id = row['UploaderID']
            i.revision_id = 1
            i.file_location = row['FileLocation']
            i.filename = row['Filename']
            i.file_extension = row['FileExtension']
            i.size = row['Filesize']
            i.mimetype = row['MimeType']
            i.upload_session_id = row['UploadSessionID']
            #i.type = row['Type']
            #i.hash = row['Hash']
            i.enabled = row['Enabled']
            i.remote_address = row['RemoteAddress']
            #if row['Deleted'] == 1:
            #    i.deleted_at = datetime.fromisoformat(row['DateUpdated'])
            #if row['Flagged'] == 1:
            #    i.flagged_at =  datetime.fromisoformat(row['DateUpdated'])
            #if int(i.user_id) != 0:
            i.save(force_insert=True)


def ingest_users():
    with open('ingest/data/Repables-Users.csv', mode='r', encoding='utf-8-sig') as csvfile:
        usersreader = csv.DictReader(csvfile)

        for row in usersreader:
            u = User()
            user_found = False
            u.email = row['Email']
            if row['Email'] == "":
                u.email = "MANUALLY_INSERT_EMAIL" + row['UserID'] + "@REPABLES.COM"
            else:
                emailSplit = row['Email'].split('@')
                if emailSplit[1] == 'bigmir.net':
                    continue
                
            u.id = row['UserID']
            u.username = row['Username']
            u.password = "$00$" + row['Salt'] + "/" + row['Password']

            u.location = row['Location']
            u.company = row['Company']
            u.biography = row['Bio']
            u.website = row['Website']
            if row['Birthdate'] != '0000-00-00':
                u.birthdate = date.fromisoformat(row['Birthdate'])

            u.email_public = row['EmailPublic']
            u.hide_inappropriate = row['HideInappropriate']
            if row['DateJoined'] == '0000-00-00 00:00:00':
                u.created_at = datetime.fromisoformat('2013-08-20 16:37:28')
            else:
                u.created_at = datetime.fromisoformat(row['DateJoined'])
            
            if row['DateUpdated'] == '0000-00-00 00:00:00':
                u.updated_at = u.created_at
            else:
                u.updated_at = datetime.fromisoformat(row['DateUpdated'])
            u.remote_address = row['RemoteAddress']
            
            if row['Enabled'] == 0:
                u.deleted_at = datetime.fromisoformat(row['DateUpdated'])
            force_insert = user_found != True
            u.save(force_insert=force_insert)
#ingest_items()
#ingest_users()
#ingest_uploads()
#ingest_item_revisions()
