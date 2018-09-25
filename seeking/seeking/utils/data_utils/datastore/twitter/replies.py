# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Tuple

from dataclasses import dataclass
from google.cloud.datastore import Entity
from more_itertools import chunked

from seeking.utils.data_utils.datastore import Datastore


@dataclass
class Reply:
    id: int
    user_id: int
    screen_name: str
    target_text: str
    source_text: str
    created_at: datetime


class Replies(Datastore):
    def __init__(self):
        super().__init__(kind=__class__.__name__)

    def find_all(self, user_id, limit=300, cursor=None):
        ds = self.client
        query = ds.query(kind=self.kind, ancestor=ds.key('Users', user_id))

        query.order = ['created_at']

        query_iter = query.fetch(limit=limit, start_cursor=cursor)
        page = next(query_iter.pages)

        entities = list(map(self.from_ds, page))
        next_cursor = (query_iter.next_page_token if query_iter.next_page_token else None)
        return entities, next_cursor.decode(encoding='utf-8')

    def upsert(self, data, user_id: int, excluded_idx: Tuple[str] = ()):
        ds = self.client
        key = ds.key(self.kind, id, parent=ds.key('Users', user_id))
        entity = Entity(key, exclude_from_indexes=excluded_idx)
        entity.update(data)
        ds.put(entity)
        return self.from_ds(entity)

    def bulk_upsert(self, data_list, user_id: int):
        ds = self.client
        entities = [self._to_entity(data.__dict__, user_id) for data in data_list]
        chunked_entities = list(chunked(entities, 500))  # can write max 500 entities in a single call
        [ds.put_multi(es) for es in chunked_entities]

    def _to_entity(self, data, user_id: int):
        id = data.pop('id')
        entity = Entity(self.client.key(self.kind, int(id), parent=self.client.key('Users', user_id)))
        entity.update(data)
        return entity
