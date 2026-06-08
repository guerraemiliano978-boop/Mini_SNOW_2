from tables import engine, users
from sqlalchemy import insert
from hasher import hash_password



new_users = [
    {
        "full_name": "Kevin",
        "username": "kevinbananalover123",
        "password": "ilovebananas",
        "role": "admin"
    },
    {
        "full_name": "Stuart",
        "username": "rockstar123",
        "password": "ilovewaterhydrants",
        "role": "agent"
    },
    {
        "full_name": "Bob",
        "username": "sweetbob",
        "password": "gruiscool",
        "role": "user"
    }
]


for row in new_users:
    hashed_password = hash_password(row["password"])
    row["password"] = hashed_password

print(new_users)


with engine.begin() as conn:
    stmt = insert(users).values(new_users)
    conn.execute(stmt)