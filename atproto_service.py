from atproto import Client, models
from Login import Login

def get_client():
    client = Client()
    client.login(Login().Username(), Login().Password())
    return client

def blob_to_url(blob, did=None):
    """Convert a blob object to a CDN URL or blob fetch URL."""
    if not blob:
        return None
    
    # If it's already a string, return it
    if isinstance(blob, str):
        return blob
    
    # Try to get the CID from the blob object
    cid = None
    if hasattr(blob, 'ref'):
        ref = blob.ref
        if hasattr(ref, 'link'):
            cid = ref.link
    
    if cid:
        # Use the CDN URL for blobs
        return f"https://cdn.bsky.app/img/feed_fullsize/{cid}"
    
    # Fallback - return the string representation
    return str(blob)

def get_current_user_handle():
    client = get_client()
    return client.me.handle

def get_profile(handle=None):
    client = get_client()
    actor = handle if handle else client.me.did
    profile = client.get_profile(actor=actor)
    return profile

def get_posts(handle=None):
    client = get_client()
    actor = handle if handle else client.me.did
    feed = client.get_author_feed(actor=actor)
    return feed.feed

def update_profile(display_name=None, description=None):
    client = get_client()
    # Get current profile record
    params_get = models.ComAtprotoRepoGetRecord.Params(
        repo=client.me.did,
        collection='app.bsky.actor.profile',
        rkey='self'
    )
    record_resp = client.com.atproto.repo.get_record(params=params_get)
    record = record_resp.value
    # Convert to dict if it's a model
    if hasattr(record, 'dict'):
        record = record.dict()
    # Update fields if provided
    if display_name is not None:
        record['displayName'] = display_name
    if description is not None:
        record['description'] = description
    # Put back
    data_put = models.ComAtprotoRepoPutRecord.Data(
        repo=client.me.did,
        collection='app.bsky.actor.profile',
        rkey='self',
        record=record
    )
    client.com.atproto.repo.put_record(data=data_put)

def create_post(text):
    client = get_client()
    response = client.send_post(text=text)
    return response