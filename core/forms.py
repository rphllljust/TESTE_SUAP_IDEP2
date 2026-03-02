from django import forms
from django.core.exceptions import ValidationError
from .models import (
    AdministrativeProcess,
    AttendanceRecord,
    Enrollment,
    Grade,
    InstitutionalProject,
    ManagementPlan,
    SchoolClass,
    ServiceDeskTicket,
    Student,
)


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'full_name',
            'registration',
            'birth_date',
            'guardian_name',
            'guardian_phone',
            'learning_mode',
            'abstract_course',
            'status',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class StudentFilterForm(forms.Form):
    query = forms.CharField(label='Buscar aluno', max_length=100, required=False)
    class_filter = forms.ModelChoiceField(label='Turma', queryset=SchoolClass.objects.none(), required=False)
    learning_mode = forms.ChoiceField(
        label='Modalidade',
        required=False,
        choices=[('', 'Todas')] + list(Student.LEARNING_MODE_CHOICES),
    )
    status = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[('', 'Todos')] + list(Student.STATUS_CHOICES),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['class_filter'].queryset = SchoolClass.objects.all()


class SchoolClassFilterForm(forms.Form):
    learning_mode = forms.ChoiceField(
        label='Modalidade',
        required=False,
        choices=[('', 'Todas')] + list(SchoolClass.LEARNING_MODE_CHOICES),
    )
    shift = forms.ChoiceField(
        label='Turno',
        required=False,
        choices=[('', 'Todos')] + list(SchoolClass.SHIFT_CHOICES),
    )


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'school_class', 'status']


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['assessment', 'enrollment', 'score']

    def clean(self):
        cleaned = super().clean()
        assessment = cleaned.get('assessment')
        score = cleaned.get('score')
        if assessment and score is not None and score > assessment.max_score:
            raise ValidationError(f'A nota nao pode ser maior que {assessment.max_score}.')
        if score is not None and score < 0:
            raise ValidationError('A nota nao pode ser negativa.')
        return cleaned


class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['class_subject', 'enrollment', 'attendance_date', 'present']
        widgets = {
            'attendance_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AdministrativeProcessForm(forms.ModelForm):
    class Meta:
        model = AdministrativeProcess
        fields = ['protocol', 'subject', 'sector', 'status', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }


class ManagementPlanForm(forms.ModelForm):
    class Meta:
        model = ManagementPlan
        fields = ['title', 'owner', 'progress', 'status', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class InstitutionalProjectForm(forms.ModelForm):
    class Meta:
        model = InstitutionalProject
        fields = ['title', 'project_type', 'coordinator', 'status', 'start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ServiceDeskTicketForm(forms.ModelForm):
    class Meta:
        model = ServiceDeskTicket
        fields = ['area', 'requester', 'subject', 'priority', 'status']
