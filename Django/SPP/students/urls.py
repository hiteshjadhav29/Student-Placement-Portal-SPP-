from django.urls import path
from . import views

app_name = "students"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("resume/", views.resume, name="resume"),
    path("resume/upload/", views.upload_resume, name="upload_resume"),
    path("skills/", views.skills, name="skills"),
    path("skills/add/", views.add_skill, name="add_skill"),
    path(
    "skills/<int:skill_id>/edit/",
    views.edit_skill,
    name="edit_skill"
),

path(
    "skills/<int:skill_id>/delete/",
    views.delete_skill,
    name="delete_skill"
),

path("projects/", views.projects, name="projects"),

path("projects/add/", views.add_project, name="add_project"),

path(
    "projects/<int:project_id>/edit/",
    views.edit_project,
    name="edit_project"
),

path(
    "projects/<int:project_id>/delete/",
    views.delete_project,
    name="delete_project"
),
path("certifications/", views.certifications, name="certifications"),
path("certifications/add/", views.add_certification, name="add_certification"),
path("certifications/<int:certification_id>/edit/", views.edit_certification, name="edit_certification"),
path("certifications/<int:certification_id>/delete/", views.delete_certification, name="delete_certification"),

]