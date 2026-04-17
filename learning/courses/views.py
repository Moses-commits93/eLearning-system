from django.shortcuts import render, redirect,get_object_or_404
from .models import Course,Enrollment
from .models import Course, Enrollment, Progress,Lesson
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.http import FileResponse,Http404,HttpResponseForbidden
from django.conf import settings
import os
from django.db.models import Avg
from django.http import HttpResponse

@login_required
def view_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    enrollment = Enrollment.objects.filter(user=request.user, courses=course).first()
    if not enrollment or enrollment.status != "approved":
        messages.error(request, "You must be enrolled to view this lesson")
        return redirect("course_details", course_id=course.id)

    progress, created = Progress.objects.get_or_create(
        user=request.user,
        course=course,
        enrollment=enrollment,
        lesson=lesson,
        defaults={"Learning_status": "in_progress", "percentage_complete": 0},
    )

    # If not complete, keep it in progress
    if progress.Learning_status != "complete":
        progress.Learning_status = "in_progress"
        progress.save()

    # Calculate overall progress
    total_lessons = course.lessons.count()
    completed_lessons = Progress.objects.filter(
        user=request.user,
        course=course,
        Learning_status="complete"
    ).count()
    overall_progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0

    # ✅ Always return a response
    return render(request, "courses/lesson.html", {
        "lesson": lesson,
        "progress": progress,
        "overall_progress": overall_progress,
        "enrollment": enrollment,
    })


def index(request):
    return HttpResponse("Hello world! Django is serving contents live.")
    #return render(request, "courses/index.html")

@login_required
def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course)

    enrollment = Enrollment.objects.filter(user=request.user, courses=course).first()
    status = enrollment.status if enrollment else "Your Are Not Enrolled"
    
    progress = Progress.objects.filter(enrollment=enrollment) if enrollment else []
    Learning_status = progress.last().Learning_status if progress else "You Have Not Started Learnig Yet!"
    

    overall_progress = (
        progress.aggregate(Avg("percentage_complete")).get("percentage_complete__avg") or 0  if progress else 0
        if progress else 0
    )
    context = {
        "course": course,
        "lessons": lessons,
        "progress": progress,
        "overall_progress":overall_progress or 0,
        "Learning_status": Learning_status,
        "enrolled": bool(enrollment and status =="approved"),
        "status": status,
    }
    return render(request, "courses/course_details.html", context)
        

def about(request):
    return render(request, 'courses/about.html')

@login_required
def enrolled_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user,status='approved')
    return render(request, "courses/enrolled_courses.html",{
        "enrollments":enrollments
    })


@login_required
def enroll(request, course_id):
    course = get_object_or_404(Course,id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        courses=course,
        defaults={'status':'pending'}
    )
    if created:
        messages.info(request, "Enrollment request submitted. Awaitind Admin approval!")
    elif enrollment.status == 'pending':
        messages.info(request, 'Your enrollment is still pending approval')
    elif enrollment.status == 'approved':
        messages.info(request, "Your are already enrolled in this course.")
    elif enrollment.status == "rejected":
        messages.info(request,"Your enrollment request was rejected!")    
    elif request.user.is_staff or request.user.is_superuser:
        return HttpResponseForbidden("Admins cannot enroll in courses")
    return redirect('course_details', course_id=course.id)    

   
    

@login_required
def complete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course

    enrollment = Enrollment.objects.filter(user=request.user, courses=course).first()
    if not enrollment or enrollment.status != "approved":
        messages.error(request, "You must be enrolled to complete this course!")
        return redirect("course_details", course_id=course.id)

    progress, created = Progress.objects.get_or_create(
        enrollment=enrollment,
        course=course,
        lesson=lesson,
        user=request.user,
        defaults={"Learning_status": "in_progress", "percentage_complete": 0, "completed": False},
    )

    # Update progress
    progress.Learning_status = "complete"
    progress.percentage_complete = 100
    progress.completed = True
    progress.save()
    print("Progress updated:", progress.Learning_status, progress.completed)

    progress.Learning_status="complete"
    progress.percentage_complete=100
    progress.completed=True
    progress.save()

    total_lessons = course.lessons.count()
    completed_lessons = Progress.objects.filter(
        enrollment =enrollment,
        user=request.user,
        course=course,
        Learning_status="complete"
    ).count()
    overall_progress=(completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
    enrollment.overall_progress=overall_progress
    enrollment.save()

    if completed_lessons==0:
        enrollment.Learning_status="not_started"
    elif completed_lessons < total_lessons:
        enroll.Learning_status="in_progress"
    else:
        enrollment.Learning_status="completed"
    progress.save() 

    messages.success(request, f"You completed {lesson.title}!")
    return redirect("course_progress", course_id=course.id)
    
    
def search_courses(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'courses/search_courses.html', {
        'results': results, 
        'query': query
        })


def course_progress(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment=Enrollment.objects.filter(user=request.user, courses=course).first()
    
    if not enrollment:
        messages.error(request, "You must be enrolled to view progress!")
        return redirect("course_details", course_id=course.id)
    
    overall_progress= enrollment.overall_progress
 
    return render(request, "courses/course_progress.html",{
        "course":course,
        "enrollment": enrollment,
        "overall_progress": overall_progress,   
    })

@login_required
def protected_file(request, course_id, filename):
    course = get_object_or_404(Course, id=course_id)

    if not Enrollment.objects.filter(user=request.user, course=course).exists():

     file_path = os.path.join(settings.MEDIA_ROOT, "courses", str(course_id), filename)
     if os.path.exists(file_path):
         return FileResponse(open(file_path, "rb"))
     raise Http404    
