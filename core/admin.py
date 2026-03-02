from django.contrib import admin
from .models import (
    AdministrativeProcess,
    Announcement,
    Assessment,
    AttendanceRecord,
    ClassSubject,
    Enrollment,
    Grade,
    InstitutionalProject,
    ManagementPlan,
    SchoolClass,
    ServiceDeskTicket,
    Student,
    Subject,
    Teacher,
)

admin.site.register(AdministrativeProcess)
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
admin.site.register(ManagementPlan)
admin.site.register(InstitutionalProject)
admin.site.register(ServiceDeskTicket)
