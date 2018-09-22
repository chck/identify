# -*- coding: utf-8 -*-
from typing import Tuple, List

from flask import current_app as app
from google.cloud import datastore
from google.cloud.datastore import Entity
from more_itertools import chunked


# @dataclass
# class _PreprocessedUsers:
#     id: int
#     screen_name: str
#     text: str
#     created_at: datetime


class PreprocessedUsers:
    def __init__(self):
        self.kind = __class__.__name__
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

    def find_all(self, limit=300, cursor=None):
        # can read max 300 entities in a single call
        ds = self.client
        query = ds.query(kind=self.kind)

        query.order = ['created_at']

        query_iter = query.fetch(limit=limit, start_cursor=cursor)
        page = next(query_iter.pages)

        entities = list(map(self.from_ds, page))
        next_cursor = (query_iter.next_page_token if query_iter.next_page_token else None)
        return entities, next_cursor

    def upsert(self, data, excluded_idx: Tuple[str] = ()):
        ds = self.client
        key = ds.key(self.kind, id, parent=ds.key('Users', id))
        entity = Entity(key, exclude_from_indexes=excluded_idx)
        entity.update(data)
        ds.put(entity)
        return self.from_ds(entity)

    def bulk_upsert(self, data_list):
        ds = self.client
        entities = [self._to_entity(data) for data in data_list]
        chunked_entities = list(chunked(entities, 500))  # can write max 500 entities in a single call
        [ds.put_multi(es) for es in chunked_entities]

    def delete(self, id: int):
        ds = self.client
        key = ds.key(self.kind, id, parent=ds.key('Users', id))
        ds.delete(key)

    def bulk_delete(self, ids: List[int]):
        ds = self.client
        keys = [ds.key(self.kind, id, parent=ds.key('Users', id)) for id in ids]
        chunked_keys = list(chunked(keys, 500))  # can write max 500 entities in a single call
        [ds.delete_multi(ks) for ks in chunked_keys]

    def _to_entity(self, data):
        id = data.pop('id')
        entity = Entity(self.client.key(self.kind, int(id), parent=self.client.key('Users', id)))
        entity.update(data)
        return entity


def fetch_all_parsed_users():
    model = PreprocessedUsers()
    entities = []
    chunk, cursor = model.find_all(limit=300)
    entities += chunk
    while cursor:
        chunk, cursor = model.find_all(limit=300, cursor=cursor)
        entities += chunk
    return entities


if __name__ == '__main__':
    pass
