from django.db import models
from django.contrib.auth.models import User

class Instructor(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    bio  = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    instructor = models.CharField(max_length=100)
    pdf = models.FileField(upload_to='courses/pdfs/',blank=True,null=True)
    video = models.FileField(upload_to='courses/videos/', blank=True,null=True)
    video_url = models.URLField(blank=True,null=True, help_text="Click the link to watch tutorial")
    learning_outcomes = models.TextField(blank=True,null=True) 
    image = models.ImageField(upload_to="images/",blank=True, null=True)

    def embed_url(self):
        url = self.video_url
        if "watch?v=" in url:
            viddeo_id=url.split("watch?v=")[-1].split("&")[0]
            return f"https://www.youtube.com/embed/{viddeo_id}"
        
        if "youtu.be/" in url:
            viddeo_id = url.split("youtu.be/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{viddeo_id}"
        return url
    

        


    def __str__(self):
        return self.title
    
    def is_enrolled(self, user):
        return self.enrollment_set.filter(user=user).exists()

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    courses = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,default='pending')
    overall_progress = models.FloatField(default=0)

    class Meta:
        unique_together = ('user', 'courses')
    

    def __str__(self):
        return f"{self.user.username} enrolled in {self.courses.title} ({self.status})"


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Progress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    Learning_status = models.CharField(max_length=20,null=True, choices=[("in_progress","In Progress"),("complete","Completed")])
    percentage_complete = models.FloatField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    complete_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.title} ({self.Learning_status})"