from pydal.validators import *
from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
import re
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid, GridClassStyleBulma


def get_reportings(user_id):
   return db(db.person.manager_id == user_id).select('user_id')

def can_edit_task(created_by, user_id):
   return created_by == user_id or created_by in [r.user_id for r in get_reportings(user_id)]

def is_managed_users(current_user_id, filter_user_id):
    return filter_user_id in [r.user_id for r in  get_reportings(current_user_id)]



@action("index")
@action.uses("index.html", auth)
def index():
    user = auth.get_user()
    if not user:
        redirect(URL("auth/login"))
    else:
        redirect(URL("tasks"))


@action("tasks", method=["GET", "POST"])
@action('tasks/<path:path>', method=['POST', 'GET'])
@action.uses("grid.html", auth.user, session, db)
def tasks(path=None):
    user_id = auth.get_user().get("id")
    grid = Grid(
        path,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        show_id=True,
        query = db.task,
        editable= lambda row: can_edit_task(row.created_by, user_id),
        deletable= False,
        details=False,
    )
    return dict(grid=grid)


@action("filter_tasks", method=["GET", "POST"])
@action('filter_tasks/<path:path>', method=['POST', 'GET'])
@action.uses("filter.html", auth.user, session, db)
def filter_tasks(path=None):
    user_id = auth.get_user().get("id")
    
    grid = Grid(
        path,
        db.task,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        show_id=True,
        left=[db.auth_user.on(db.task.created_by == db.auth_user.id),
              db.task_assignment.on(db.task_assignment.task_id == db.task.id),
              db.task_comment.on(db.task_comment.task_id == db.task.id)],
        columns=[db.task.id, db.task.title, db.task.description, db.task.created_on, db.task.created_by, db.task.modified_by, db.auth_user.first_name, db.task.deadline, db.task.status, db.task_assignment.assigned_user_id, db.task_comment.body],
        headings=['Id', 'Title', 'Description', 'Created on', 'Created by', 'Modified_by', 'Name', 'Deadline', 'Status', 'Assigned Userid', 'Comments'],
        search_queries=[
            ["date created", lambda value: db.task.created_on == value],
            ["deadline", lambda value: db.task.deadline == value],
            ["status", lambda value: db.task.status == value],
            ["created by self", lambda value: db.task.created_by == value],
            ["posted by self", lambda value: db.task.modified_by == value],
            ["created by a specific user", lambda value: db.task.created_by == value],
            ["assigned to a specific user", lambda value: db.task_assignment.assigned_user_id == value],
            ["created by any managed user", lambda value: db.task.created_by == value if is_managed_users(user_id, int(value)) else db.task.created_by == ''],
            ["assigned to any managed user", lambda value: db.task_assignment.assigned_user_id == value if is_managed_users(user_id, int(value)) else db.task_assignment.assigned_user_id == ''],
        ],
        create=False,
        details=False,
        editable= False,
        deletable= False,
    )
    return dict(grid=grid)

@action("task_comments", method=["GET", "POST"])
@action('task_comments/<path:path>', method=['POST', 'GET'])
@action.uses("grid.html", auth.user, session, db)
def task_comments(path=None):
    grid = Grid(
        path,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        query=db.task_comment,
        columns=[db.task_comment.task_id, db.task_comment.body, db.task_comment.created_on, db.auth_user.first_name],
        left=[db.auth_user.on(db.task_comment.created_by == db.auth_user.id)],
        headings=['TaskId', 'Comment', 'Created on', 'Created by'],
        search_queries=[
            ["Task", lambda value: db.task_comment.task_id == value],
            ["Comment", lambda value: db.task_comment.body.contains(value)],
            ["Created by", lambda value: db.auth_user.first_name.contains(value)],
        ],
    )
    return dict(grid=grid)

@action("task_assignment", method=["GET", "POST"])
@action('task_assignment/<path:path>', method=['POST', 'GET'])
@action.uses("grid.html", auth.user, session, db)   
def task_assignments(path=None):
    grid = Grid(
        path,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        query=db.task_assignment,
        columns=[db.task_assignment.task_id, db.task_assignment.assigned_user_id, db.auth_user.first_name, db.auth_user.email],
        left=[db.auth_user.on(db.task_assignment.created_by == db.auth_user.id)],
        headings=['Task', 'Assigned Userid', 'Assigned name', 'Email'],
        search_queries=[
            ["Task", lambda value: db.task_assignment.task_id == value],
            ["Assigned Userid", lambda value: db.task_assignment.assigned_user_id == value],
            ["Assigned to", lambda value: db.auth_user.first_name.contains(value)],
            ["Email", lambda value: db.auth_user.email.contains(value)],
        ],
    )
    return dict(grid=grid)

@action("person", method=["GET", "POST"])
@action('person/<path:path>', method=['POST', 'GET'])
@action.uses("grid.html", auth.user, session, db)
def persons(path=None):
    grid = Grid(
        path,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        query=db.person,
        columns=[db.person.user_id, db.person.manager_id, db.person.title],
        search_queries=[
            ["User", lambda value: db.person.user_id == value],
            ["Manager", lambda value: db.person.manager_id == value],
            ["title", lambda value: db.person.title.contains(value)]
        ],
        # create=False,
    )
    return dict(grid=grid)

@action("employee", method=["GET", "POST"])
@action('employee/<path:path>', method=['POST', 'GET'])
@action.uses("grid.html", auth.user, session, db)
def employee(path=None):
    grid = Grid(
        path,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        query=db.auth_user,
        create=False,
        deletable=False,
    )
    return dict(grid=grid)