from .common import db, Field, auth
from pydal.validators import *

db.define_table(
    "task",
    Field("title", requires=IS_NOT_EMPTY()),
    Field("description", "text"),
    Field("deadline", 'date', default=None, requires=IS_EMPTY_OR(IS_DATE())),
    Field("status", options=("pending", "ackowledged", "rejected", "completed", "failed"), default="pending"),
    auth.signature
)

db.define_table(
    "task_comment",
    Field("body", "text", requires=IS_NOT_EMPTY()),
    Field("task_id", "reference task"),
    auth.signature
)
db.define_table(
    "task_assignment",
    Field("task_id", "reference task"),
    Field("assigned_user_id", "reference auth_user"),
    auth.signature
)

db.define_table(
    "person",
    Field("user_id", "reference auth_user", editable=False),
    Field("manager_id", "reference auth_user"),
    Field("title", "string", requires=IS_IN_SET([
        "CEO",
        "Manager",
        "Employee",
    ]))
)

db.commit()