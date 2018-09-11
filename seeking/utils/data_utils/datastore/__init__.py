# -*- coding: utf-8 -*-
from typing import Tuple

from flask import current_app as app
from google.cloud import datastore
from google.cloud.datastore import Entity
from more_itertools import chunked


class Datastore:
    def __init__(self, kind):
        self.kind = kind
        self.client = datastore.Client(app.config['PROJECT_ID'])

    def from_ds(self, entity):
        if not entity:
            return None
        if isinstance(entity, list):
            entity = entity.pop()
        entity['id'] = str(entity.key.id)
        return entity

    def find(self, id):
        ds = self.client
        key = ds.key(self.kind, int(id))
        return self.from_ds(ds.get(key))

    def find_all(self, limit=50, cursor=None):
        ds = self.client
        query = ds.query(kind=self.kind)
        query_iter = query.fetch(limit=limit, start_cursor=cursor)
        page = next(query_iter.pages)

        entities = list(map(self.from_ds, page))
        next_cursor = (query_iter.next_page_token if query_iter.next_page_token else None)
        return entities, next_cursor

    def upsert(self, data, id=None, excluded_idx: Tuple[str] = ()):
        ds = self.client
        if id:
            key = ds.key(self.kind, id)
        else:
            key = ds.key(self.kind)
        entity = Entity(key, exclude_from_indexes=excluded_idx)
        entity.update(data)
        ds.put(entity)
        return self.from_ds(entity)

    def bulk_upsert(self, data_list):
        ds = self.client
        entities = [self._to_entity(data.__dict__) for data in data_list]
        chunked_entities = list(chunked(entities, 500))  # can write max 500 entities in a single call
        [ds.put_multi(es) for es in chunked_entities]

    def delete(self, id):
        ds = self.client
        key = ds.key(self.kind, id)
        ds.delete(key)

    def bulk_delete(self, ids):
        ds = self.client
        keys = [ds.key(self.kind, id) for id in ids]
        chunked_keys = list(chunked(keys, 500))  # can write max 500 entities in a single call
        [ds.delete_multi(ks) for ks in chunked_keys]

    def _to_entity(self, data):
        id = data.pop('id')
        entity = Entity(self.client.key(self.kind, int(id)))
        entity.update(data)
        return entity
