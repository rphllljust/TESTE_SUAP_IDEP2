from django.contrib import admin
from .models import (
    Announcement,
    Assessment,
    AttendanceRecord,
    ClassSubject,
    Enrollment,
    Grade,
    SchoolClass,
    Student,
    Subject,
    Teacher,
)

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(SchoolClass)
admin.site.register(Subject)
admin.site.register(ClassSubject)
admin.site.register(Enrollment)
admin.site.register(Assessment)
admin.site.register(Grade)
admin.site.register(AttendanceRecord)
admin.site.register(Announcement)
