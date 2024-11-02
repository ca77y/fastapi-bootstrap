import json
from datetime import datetime
from uuid import UUID

from server.common.http import DEFAULT_DATETIME_FORMAT


class TypeAwareEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.strftime(DEFAULT_DATETIME_FORMAT)
        return json.JSONEncoder._old_default(self, obj)  # type: ignore
