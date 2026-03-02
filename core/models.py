from django.db import models


class Teacher(models.Model):
    full_name = models.CharField(max_length=150)
    employee_code = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class SchoolClass(models.Model):
    MORNING = 'morning'
    AFTERNOON = 'afternoon'
    NIGHT = 'night'
    IN_PERSON = 'in_person'
    REMOTE = 'remote'
    SHIFT_CHOICES = [
        (MORNING, 'Manha'),
        (AFTERNOON, 'Tarde'),
        (NIGHT, 'Noite'),
    ]
    LEARNING_MODE_CHOICES = [
        (IN_PERSON, 'Presencial'),
        (REMOTE, 'Remota'),
    ]

    name = models.CharField(max_length=30)
    year = models.PositiveIntegerField()
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    learning_mode = models.CharField(max_length=12, choices=LEARNING_MODE_CHOICES, default=IN_PERSON)
    coordinator = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-year', 'name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'year', 'shift'], name='unique_class_by_year_shift'),
        ]

    def __str__(self):
        return f'{self.name} - {self.year} ({self.get_shift_display()})'


class Subject(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    workload_hours = models.PositiveSmallIntegerField(default=60)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'


class ClassSubject(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT)

    class Meta:
        ordering = ['school_class__name', 'subject__name']
        constraints = [
            models.UniqueConstraint(fields=['school_class', 'subject'], name='unique_subject_per_class'),
        ]

    def __str__(self):
        return f'{self.school_class} - {self.subject.name}'


class Student(models.Model):
    ACTIVE = 'active'
    ATTENTION = 'attention'
    INACTIVE = 'inactive'
    IN_PERSON = 'in_person'
    REMOTE = 'remote'
    STATUS_CHOICES = [
        (ACTIVE, 'Ativo'),
        (ATTENTION, 'Atencao'),
        (INACTIVE, 'Inativo'),
    ]
    LEARNING_MODE_CHOICES = [
        (IN_PERSON, 'Presencial'),
        (REMOTE, 'Remoto'),
    ]

    full_name = models.CharField(max_length=180)
    registration = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField()
    guardian_name = models.CharField(max_length=180)
    guardian_phone = models.CharField(max_length=30)
    learning_mode = models.CharField(max_length=12, choices=LEARNING_MODE_CHOICES, default=IN_PERSON)
    abstract_course = models.CharField(max_length=120, default='Trilha Geral')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f'{self.full_name} ({self.registration})'


class Enrollment(models.Model):
    ACTIVE = 'active'
    TRANSFERRED = 'transferred'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (ACTIVE, 'Ativa'),
        (TRANSFERRED, 'Transferida'),
        (COMPLETED, 'Concluida'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.PROTECT, related_name='enrollments')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=ACTIVE)
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-enrollment_date']
        constraints = [
            models.UniqueConstraint(fields=['student', 'school_class'], name='unique_student_enrollment_class'),
        ]

    def __str__(self):
        return f'{self.student.full_name} - {self.school_class}'


class Assessment(models.Model):
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=120)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=10)
    assessment_date = models.DateField()

    class Meta:
        ordering = ['-assessment_date', 'title']

    def __str__(self):
        return f'{self.title} ({self.class_subject})'


class Grade(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='grades')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='grades')
    score = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ['assessment__assessment_date']
        constraints = [
            models.UniqueConstraint(fields=['assessment', 'enrollment'], name='unique_grade_by_assessment_enrollment'),
        ]

    def __str__(self):
        return f'{self.enrollment.student.full_name} - {self.score}'


class AttendanceRecord(models.Model):
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='attendance_records')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendance_records')
    attendance_date = models.DateField()
    present = models.BooleanField(default=True)

    class Meta:
        ordering = ['-attendance_date']
        constraints = [
            models.UniqueConstraint(
                fields=['class_subject', 'enrollment', 'attendance_date'],
                name='unique_attendance_by_class_enrollment_date',
            ),
        ]

    def __str__(self):
        state = 'Presente' if self.present else 'Falta'
        return f'{self.enrollment.student.full_name} - {self.attendance_date} - {state}'


class Announcement(models.Model):
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    LEVEL_CHOICES = [
        (INFO, 'Informativo'),
        (SUCCESS, 'Sucesso'),
        (WARNING, 'Atencao'),
    ]

    title = models.CharField(max_length=140)
    body = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=INFO)
    published_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class AdministrativeProcess(models.Model):
    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (OPEN, 'Aberto'),
        (IN_PROGRESS, 'Em andamento'),
        (COMPLETED, 'Concluido'),
    ]

    protocol = models.CharField(max_length=30, unique=True)
    subject = models.CharField(max_length=180)
    sector = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['deadline', 'protocol']

    def __str__(self):
        return f'{self.protocol} - {self.subject}'


class ManagementPlan(models.Model):
    DRAFT = 'draft'
    ACTIVE = 'active'
    APPROVED = 'approved'
    STATUS_CHOICES = [
        (DRAFT, 'Rascunho'),
        (ACTIVE, 'Em execucao'),
        (APPROVED, 'Aprovado'),
    ]

    title = models.CharField(max_length=180)
    owner = models.CharField(max_length=150)
    progress = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    due_date = models.DateField()

    class Meta:
        ordering = ['due_date', 'title']

    def __str__(self):
        return self.title


class InstitutionalProject(models.Model):
    RESEARCH = 'research'
    EXTENSION = 'extension'
    INTERNATIONAL = 'international'
    DEVELOPMENT = 'development'
    STUDENT = 'student'
    COMMUNICATION = 'communication'
    AUDIT = 'audit'
    PROJECT_TYPE_CHOICES = [
        (RESEARCH, 'Pesquisa'),
        (EXTENSION, 'Extensao'),
        (INTERNATIONAL, 'Internacionalizacao'),
        (DEVELOPMENT, 'Desenvolvimento Institucional'),
        (STUDENT, 'Atividades Estudantis'),
        (COMMUNICATION, 'Comunicacao Social'),
        (AUDIT, 'Auditoria'),
    ]
    DRAFT = 'draft'
    ACTIVE = 'active'
    CLOSED = 'closed'
    STATUS_CHOICES = [
        (DRAFT, 'Planejamento'),
        (ACTIVE, 'Em execucao'),
        (CLOSED, 'Concluido'),
    ]

    title = models.CharField(max_length=180)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES)
    coordinator = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    start_date = models.DateField()

    class Meta:
        ordering = ['project_type', 'title']

    def __str__(self):
        return self.title


class ServiceDeskTicket(models.Model):
    CENTRAL = 'central'
    IT = 'it'
    SECURITY = 'security'
    ADMIN = 'admin'
    AREA_CHOICES = [
        (CENTRAL, 'Central de Servicos'),
        (IT, 'Tec. da Informacao'),
        (SECURITY, 'Seguranca Institucional'),
        (ADMIN, 'Administracao'),
    ]
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    PRIORITY_CHOICES = [
        (LOW, 'Baixa'),
        (MEDIUM, 'Media'),
        (HIGH, 'Alta'),
    ]
    OPEN = 'open'
    WORKING = 'working'
    RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (OPEN, 'Aberto'),
        (WORKING, 'Em atendimento'),
        (RESOLVED, 'Resolvido'),
    ]

    area = models.CharField(max_length=20, choices=AREA_CHOICES)
    requester = models.CharField(max_length=150)
    subject = models.CharField(max_length=180)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_area_display()} - {self.subject}'
