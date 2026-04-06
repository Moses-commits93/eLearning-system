from django.contrib import admin
from .models import Enrollment,Lesson,Progress,Course, Instructor

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ["name", "email"]


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'content', 'instructor')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor')
    search_fields = ('title', 'instructor')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
    search_fields = ('title',)

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed')
    list_filter = ('completed', 'lesson__course')
    search_fields = ('enrollment__user__userneme', 'lesson_title')

    def get_enrollment_status(self, obj):
        return obj.enrollment.status
    get_enrollment_status.short_description = "Enrollment Status:"

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user','courses','status','enrolled_at')
    
    def get_queryset(self, request):
        qs =  super().get_queryset(request)
        return qs.exclude(user__is_staff=True).exclude(user__is_superuser=True)
    
    list_filter = ('status','courses')
    search_fields = ('course__title', 'instructor__name')
    actions = ['approve_enrollment','reject_enrollment']

    def approve_enrollment(self, request, queryset):
        queryset.update(status='approved')
    approve_enrollment.short_description = "Approve selected enrollmentss"

    def reject_enrollment(self, request, queryset):
        queryset.update(status='rejected')
    reject_enrollment.short_description = "Reject selected enrollment"        
