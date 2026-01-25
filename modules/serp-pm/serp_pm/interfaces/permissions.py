"""Permission definitions for Project Management module."""

from serp_core.auth.permissions import Permission


# Project permissions
PROJECT_LIST = Permission(name="pm.project.list", description="List projects")
PROJECT_READ = Permission(name="pm.project.read", description="Read project details")
PROJECT_CREATE = Permission(name="pm.project.create", description="Create projects")
PROJECT_UPDATE = Permission(name="pm.project.update", description="Update projects")
PROJECT_DELETE = Permission(name="pm.project.delete", description="Delete projects")

# Task permissions
TASK_LIST = Permission(name="pm.task.list", description="List tasks")
TASK_READ = Permission(name="pm.task.read", description="Read task details")
TASK_CREATE = Permission(name="pm.task.create", description="Create tasks")
TASK_UPDATE = Permission(name="pm.task.update", description="Update tasks")
TASK_DELETE = Permission(name="pm.task.delete", description="Delete tasks")
TASK_ASSIGN = Permission(name="pm.task.assign", description="Assign tasks to users")

# Team permissions
TEAM_LIST = Permission(name="pm.team.list", description="List teams")
TEAM_READ = Permission(name="pm.team.read", description="Read team details")
TEAM_CREATE = Permission(name="pm.team.create", description="Create teams")
TEAM_MANAGE_MEMBERS = Permission(name="pm.team.manage_members", description="Manage team members")

ALL_PERMISSIONS = [
    PROJECT_LIST, PROJECT_READ, PROJECT_CREATE, PROJECT_UPDATE, PROJECT_DELETE,
    TASK_LIST, TASK_READ, TASK_CREATE, TASK_UPDATE, TASK_DELETE, TASK_ASSIGN,
    TEAM_LIST, TEAM_READ, TEAM_CREATE, TEAM_MANAGE_MEMBERS,
]
