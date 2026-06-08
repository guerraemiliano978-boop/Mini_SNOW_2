from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, ForeignKey, text, CheckConstraint, insert, select


engine = create_engine("sqlite:///database.db")

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("full_name", String, nullable=False),
    Column("username", String, nullable=False, unique=True),
    Column("password", String, nullable=False),
    Column("role", String, nullable=False)
)



metadata.create_all(engine)





#incidents = Table(
    #"incidents",
    #metadata,
    #Column("id", Integer, primary_key=True),
    #Column("short_description", String, nullable=False),
    #Column("description", String, nullable=False),
    #Column("opened_by", Integer, ForeignKey(users.c.id), primary_key=True),
    #Column("opened_for", Integer, ForeignKey(users.c.id), primary_key=True),
    #Column("assigned_to", Integer, ForeignKey),
    #Column("status", CheckConstraint("status IN ('open', 'in progress', 'closed')"), nullable=False, server_default=text("'open'")),
    #Column("resolution_notes", String)
#)
