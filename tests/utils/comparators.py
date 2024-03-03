import typing
from datetime import datetime
from unittest.mock import ANY

from bson import ObjectId

ANY = ANY.__class__


class ANY_DATE(ANY):
    "A helper object that compares dates"

    def __init__(self, before: datetime | None = None, after: datetime | None = None) -> None:
        self.before = before
        self.after = after

    def __eq__(self, o: typing.Any):
        if not isinstance(o, datetime):
            return False

        equal = True
        other = typing.cast(datetime, o)

        if self.before is not None:
            equal = other.timestamp() < self.before.timestamp()
        if self.after is not None:
            equal = other.timestamp() > self.after.timestamp()

        return equal

    def __ne__(self, o: typing.Any):
        return not self.__eq__(o)

    def __repr__(self):
        return '<ANYDATE>'


class ANY_OBJECTID(ANY):
    "A helper object that compares object id"

    def __eq__(self, o: typing.Any):
        return isinstance(o, ObjectId)

    def __ne__(self, o: typing.Any):
        return not self.__eq__(o)

    def __repr__(self):
        return '<ANY_OBJECTID>'


class ANY_STR(ANY):
    "A helper object that compares object id"

    def __eq__(self, o: typing.Any):
        return isinstance(o, str)

    def __ne__(self, o: typing.Any):
        return not self.__eq__(o)

    def __repr__(self):
        return '<ANY_STR>'
