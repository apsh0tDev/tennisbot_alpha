from db import db

async def upload(info, table):
    response = db.table(table).insert(info).execute()
    return response

async def update(info, table, value, to_match):
    response = db.table(table).update(info).eq(to_match, value).execute()
    return response