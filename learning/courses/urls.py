from django.urls import path
from . import views

urlpatterns = [
    path("courses/<int:course_id>/", views.course_details, name="course_details"),
    path("about/", views.about, name="about"),
    path("enrolled/", views.enrolled_courses, name='enrolled_courses'),
    path("courses/<int:course_id>/enroll/", views.enroll, name='enroll'),
    path("search/", views.search_courses, name="search_courses"),
    path("course/<int:course_id>/progress/", views.course_progress, name="course_progress"),
    path("courses/<int:lesson_id>/lesson/", views.view_lesson, name="view_lesson"),
    path("courses/<int:lesson_id>/complete/", views.complete_lesson, name="complete_lesson")
]
