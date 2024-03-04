"""
Add unique index for the profile nickname
"""
import pymongo.database

name = '1709495379766_add_profile_nickname_unique_index'
dependencies = []


def upgrade(db: pymongo.database.Database):
    db.get_collection("profiles").create_index(
        "nickname",
        name="nickname_unique",
        unique=True
    )


def downgrade(db: pymongo.database.Database):
    db.get_collection("profiles").drop_index("nickname_unique")
