# -*- coding: utf-8 -*-
from mimetypes import guess_type
from os import remove
from os.path import join, basename

from flask import current_app as app
from google.cloud import storage

from identify.utils.string_utils import to_snake


class Seeking:
    def __init__(self):
        self.bucket = storage.Client(project=app.config['PROJECT_ID']).bucket(to_snake(__class__.__name__))

    def get(self, remotekey):
        blob = self.bucket.get_blob(remotekey)
        localpath = join('/tmp', basename(remotekey))
        blob.download_to_filename(localpath)
        return localpath

    def put(self, remotekey, localpath, public=False):
        content_type = guess_type(localpath)[0]
        blob = self.bucket.blob(remotekey)
        blob.upload_from_string(
            open(localpath, 'rb').read(),
            content_type,
        )
        remove(localpath)
        if public:
            blob.make_public()
            return blob.public_url
        else:
            return blob

    def copy(self, fromkey, tokey):
        fromblob = self.bucket.blob(fromkey)
        return self.bucket.copy_blob(fromblob, self.bucket, tokey)

    def delete(self, remotekey):
        blob = self.bucket.blob(remotekey)
        blob.delete()
        return remotekey
