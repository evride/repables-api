from models import Item, User, ItemRevision, ItemUpload, ItemView, ItemImage, ItemLike
from playhouse.shortcuts import *



def getItemsRevisionImages(limit:int = 20, offset:int = 0):
    itemBase =  Item.select().where(Item.revision_id > 1)

    itemCount = itemBase.count()
    items = itemBase.order_by(Item.id.asc()).limit(limit).offset(offset).execute()

    items = list(items)

    revision_ids = []
    
    for item in items:
        revision_ids.append(item.revision_id)
    
    item_revisions = ItemRevision.enable_relationships().select().where(ItemRevision.id << revision_ids).execute()
    item_revisions = list(item_revisions)
    
    revisions = dict()
    for item_revision in item_revisions:
        revisions[item_revision.id] = item_revision

    
    item_images = ItemImage.select().where(ItemImage.revision_id << revision_ids).execute()
    revision_images = dict()
    item_images = list(item_images)
    for image in item_images:
        if image.revision.id not in revision_images:
            revision_images[image.revision.id] = dict()
        if image.upload_id not in revision_images[image.revision.id]:
            revision_images[image.revision.id][image.upload_id] = dict()
        imageObj = {'url': image.path, 'width': image.width, 'height':image.height}
        revision_images[image.revision.id][image.upload_id][image.type] = imageObj
    
    itemObjects = []
    for item in items:
        itemObject = model_to_dict(item)
        itemObject['item_revision'] = model_to_dict(revisions[item.revision_id])
        if item.revision_id in revision_images:          
            itemObject['images'] = list(revision_images[item.revision_id].values())
            #imagesArray = list(revision_images[item.revision_id].values())
            imagesArray = itemObject['images']
            itemObject['previewImage'] = imagesArray[0]
        else:
            print("Item Without Images" + str(item.revision_id))
        itemObjects.append(itemObject)
        #item.revision = revisions[item.revision_id]
        #item.images = revision_images[item.revision_id]
    

    return { 'count': itemCount, 'results': itemObjects }



def getItemRevisionsImages(id:int, revision_id:int = 0):
    
    item = Item.select().where(Item.id == id).where(Item.revision_id > 1).get()

    if revision_id == 0:
        revision_id = item.revision_id
    
    item_revisions = ItemRevision.disable_relationships().select().where(ItemRevision.item_id == id).execute()
    item_revisions = list(item_revisions)
    item_revisions = [model_to_dict(item_revision) for item_revision in item_revisions]

    item_images = ItemImage.disable_relationships().select().where(ItemImage.revision_id == revision_id).execute()


    item_uploads = ItemUpload.disable_relationships().select().where(ItemUpload.revision_id == revision_id).execute()
    item_uploads = list(item_uploads)
    
    item_upload_types = dict()
    for item_upload in item_uploads:
        is_3dmodel = item_upload.file_extension in ['stl', 'obj'] 
        item_upload_types[item_upload.id] = is_3dmodel
    item_uploads = [model_to_dict(item_upload) for item_upload in item_uploads]

    

    item_images = list(item_images)
    
    upload_images = dict()
    for image in item_images:
        if image.upload_id not in upload_images:
            upload_images[image.upload_id] = { 'is_3dmodel': item_upload_types[image.upload_id], 'upload_id': image.upload_id }
        imageObj = { 'url': image.path, 'width': image.width, 'height':image.height}
        upload_images[image.upload_id][image.type] = imageObj

    item_response = model_to_dict(item)
    item_response['images'] = list(upload_images.values())
    item_response['item_revisions'] = item_revisions
    item_response['uploads'] = item_uploads

    

    return item_response
