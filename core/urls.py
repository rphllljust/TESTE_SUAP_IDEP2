from django.urls import path
from .views import (
    agenda_page,
    attendance_page,
    classes_page,
    dashboard,
    enrollments_page,
    grades_page,
    module_page,
    student_create,
    student_delete,
    student_update,
    students_page,
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('alunos/', students_page, name='students_page'),
    path('alunos/novo/', student_create, name='student_create'),
    path('alunos/<int:pk>/editar/', student_update, name='student_update'),
    path('alunos/<int:pk>/excluir/', student_delete, name='student_delete'),
    path('turmas/', classes_page, name='classes_page'),
    path('matriculas/', enrollments_page, name='enrollments_page'),
    path('notas/', grades_page, name='grades_page'),
    path('frequencia/', attendance_page, name='attendance_page'),
    path('agenda/', agenda_page, name='agenda_page'),
    path('modulos/<slug:module_key>/', module_page, name='module_page'),
]
