from atproto import Client, models
from Login import Login

def get_client():
    client = Client()
    client.login(Login().Username(), Login().Password())
    return client

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