from datetime import date, timedelta

from django.contrib import messages
from django.db.models import Avg, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AdministrativeProcessForm,
    AttendanceRecordForm,
    EnrollmentForm,
    GradeForm,
    InstitutionalProjectForm,
    ManagementPlanForm,
    SchoolClassFilterForm,
    ServiceDeskTicketForm,
    StudentFilterForm,
    StudentForm,
)
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


MODULE_CONFIG = {
    'documentos-processos': {
        'title': 'Documentos/Processos',
        'kind': 'process',
        'description': 'Cadastro e acompanhamento de processos administrativos com prazo e setor responsavel.',
    },
    'programa-gestao': {
        'title': 'Programa de Gestao',
        'kind': 'plan',
        'description': 'Planos de entrega, progresso das metas e organizacao de pactuacoes.',
    },
    'ensino': {
        'title': 'Ensino',
        'kind': 'teaching',
        'description': 'Visao consolidada de alunos, turmas, avaliacoes e frequencia.',
    },
    'pesquisa': {
        'title': 'Pesquisa',
        'kind': 'project',
        'project_type': InstitutionalProject.RESEARCH,
        'description': 'Projetos de pesquisa, coordenacao e situacao de execucao.',
    },
    'extensao': {
        'title': 'Extensao',
        'kind': 'project',
        'project_type': InstitutionalProject.EXTENSION,
        'description': 'Acoes extensionistas, programas e situacao atual.',
    },
    'gestao-pessoas': {
        'title': 'Gestao de Pessoas',
        'kind': 'people',
        'description': 'Quadro de servidores docentes e distribuicao operacional.',
    },
    'administracao': {
        'title': 'Administracao',
        'kind': 'ticket',
        'area': ServiceDeskTicket.ADMIN,
        'description': 'Demandas administrativas, prioridades e fila de atendimento.',
    },
    'tec-informacao': {
        'title': 'Tec. da Informacao',
        'kind': 'ticket',
        'area': ServiceDeskTicket.IT,
        'description': 'Chamados tecnicos, priorizacao e acompanhamento de suporte.',
    },
    'desenvolvimento-institucional': {
        'title': 'Des. Institucional',
        'kind': 'project',
        'project_type': InstitutionalProject.DEVELOPMENT,
        'description': 'Projetos estrategicos e indicadores de governanca.',
    },
    'central-servicos': {
        'title': 'Central de Servicos',
        'kind': 'ticket',
        'area': ServiceDeskTicket.CENTRAL,
        'description': 'Demandas centralizadas com SLA e acompanhamento de fila.',
    },
    'internacionalizacao': {
        'title': 'Internacionalizacao',
        'kind': 'project',
        'project_type': InstitutionalProject.INTERNATIONAL,
        'description': 'Convenios, editais e iniciativas de mobilidade.',
    },
    'atividades-estudantis': {
        'title': 'Atividades Estudantis',
        'kind': 'project',
        'project_type': InstitutionalProject.STUDENT,
        'description': 'Acoes e programas voltados ao apoio estudantil.',
    },
    'comunicacao-social': {
        'title': 'Comunicacao Social',
        'kind': 'project',
        'project_type': InstitutionalProject.COMMUNICATION,
        'description': 'Campanhas, pautas e iniciativas de comunicacao institucional.',
    },
    'seguranca-institucional': {
        'title': 'Seguranca Institucional',
        'kind': 'ticket',
        'area': ServiceDeskTicket.SECURITY,
        'description': 'Ocorrencias, rondas e filas de atendimento de seguranca.',
    },
    'auditoria': {
        'title': 'Auditoria',
        'kind': 'project',
        'project_type': InstitutionalProject.AUDIT,
        'description': 'Frentes de auditoria, evidencias e situacao de acompanhamento.',
    },
    'sair': {
        'title': 'Sair',
        'kind': 'exit',
        'description': 'Area de encerramento seguro da sessao local.',
    },
}

IN_PERSON_COURSES = [
    'Tecnico em Administracao Integrada',
    'Tecnico em Logistica Presencial',
    'Tecnico em Informatica para Internet',
    'Tecnico em Edificacoes Integrado',
    'Tecnico em Mecanica Aplicada',
    'Tecnico em Eletrotecnica Industrial',
    'Tecnico em Eventos e Cerimonial',
    'Tecnico em Quimica de Processos',
    'Tecnico em Seguranca do Trabalho',
    'Tecnico em Multimeios Didaticos',
]

REMOTE_COURSES = [
    'Tecnico em Secretaria Escolar EAD',
    'Tecnico em Administracao Publica EAD',
    'Tecnico em Servicos Juridicos Remoto',
    'Tecnico em Redes de Computadores EAD',
    'Tecnico em Marketing Digital Remoto',
    'Tecnico em Transacoes Imobiliarias EAD',
    'Tecnico em Recursos Humanos EAD',
    'Tecnico em Financas Remoto',
    'Tecnico em Comercio Exterior EAD',
    'Tecnico em Desenvolvimento de Sistemas Remoto',
]

FIRST_NAMES = [
    'Ana', 'Bruno', 'Camila', 'Diego', 'Elisa', 'Felipe', 'Gabriela', 'Hugo', 'Isabela', 'Joao',
    'Karen', 'Lucas', 'Marina', 'Nathan', 'Olivia', 'Paulo', 'Quezia', 'Rafael', 'Sofia', 'Tiago',
]

LAST_NAMES = [
    'Almeida', 'Barros', 'Cardoso', 'Duarte', 'Esteves', 'Ferraz', 'Gomes', 'Henrique', 'Ivo', 'Jardim',
    'Klein', 'Lacerda', 'Moraes', 'Nogueira', 'Oliveira', 'Pereira', 'Queiroz', 'Ramos', 'Santana', 'Teixeira',
]

TEACHER_SEED = [
    ('DOC001', 'Ana Beatriz', 'ana@escola.edu.br'),
    ('DOC002', 'Rafael Lima', 'rafael@escola.edu.br'),
    ('DOC003', 'Carla Menezes', 'carla@escola.edu.br'),
    ('DOC004', 'Daniel Rocha', 'daniel@escola.edu.br'),
    ('DOC005', 'Fernanda Sousa', 'fernanda@escola.edu.br'),
    ('DOC006', 'Guilherme Prado', 'guilherme@escola.edu.br'),
]


def _build_student_name(index):
    first_name = FIRST_NAMES[(index - 1) % len(FIRST_NAMES)]
    last_name = LAST_NAMES[((index - 1) * 3) % len(LAST_NAMES)]
    return f'{first_name} {last_name} {index:03d}'


def seed_school_data():
    teachers = []
    for employee_code, full_name, email in TEACHER_SEED:
        teacher, _ = Teacher.objects.update_or_create(
            employee_code=employee_code,
            defaults={'full_name': full_name, 'email': email},
        )
        teachers.append(teacher)

    class_defaults = [
        ('1A', SchoolClass.MORNING, SchoolClass.IN_PERSON, teachers[0]),
        ('1B', SchoolClass.AFTERNOON, SchoolClass.IN_PERSON, teachers[2]),
        ('2A', SchoolClass.NIGHT, SchoolClass.IN_PERSON, teachers[4]),
        ('2B', SchoolClass.MORNING, SchoolClass.REMOTE, teachers[1]),
        ('3A', SchoolClass.AFTERNOON, SchoolClass.REMOTE, teachers[3]),
        ('3B', SchoolClass.NIGHT, SchoolClass.REMOTE, teachers[5]),
    ]
    classes = []
    for name, shift, learning_mode, coordinator in class_defaults:
        school_class, _ = SchoolClass.objects.get_or_create(
            name=name,
            year=date.today().year,
            shift=shift,
            defaults={'coordinator': coordinator, 'learning_mode': learning_mode},
        )
        school_class.coordinator = coordinator
        school_class.learning_mode = learning_mode
        school_class.save(update_fields=['coordinator', 'learning_mode'])
        classes.append(school_class)

    in_person_classes = [item for item in classes if item.learning_mode == SchoolClass.IN_PERSON]
    remote_classes = [item for item in classes if item.learning_mode == SchoolClass.REMOTE]

    s1, _ = Subject.objects.get_or_create(
        code='MAT101',
        defaults={'name': 'Matematica', 'workload_hours': 80},
    )
    s2, _ = Subject.objects.get_or_create(
        code='POR101',
        defaults={'name': 'Portugues', 'workload_hours': 80},
    )

    for index, school_class in enumerate(classes):
        math_teacher = teachers[index % len(teachers)]
        math_assignment, _ = ClassSubject.objects.get_or_create(
            school_class=school_class,
            subject=s1,
            defaults={'teacher': math_teacher},
        )
        if math_assignment.teacher_id != math_teacher.id:
            math_assignment.teacher = math_teacher
            math_assignment.save(update_fields=['teacher'])

        language_teacher = teachers[(index + 1) % len(teachers)]
        language_assignment, _ = ClassSubject.objects.get_or_create(
            school_class=school_class,
            subject=s2,
            defaults={'teacher': language_teacher},
        )
        if language_assignment.teacher_id != language_teacher.id:
            language_assignment.teacher = language_teacher
            language_assignment.save(update_fields=['teacher'])

    primary_in_person_class = in_person_classes[0]
    primary_remote_class = remote_classes[0]
    cs1 = ClassSubject.objects.get(school_class=primary_in_person_class, subject=s1)
    cs2 = ClassSubject.objects.get(school_class=primary_in_person_class, subject=s2)
    cs3 = ClassSubject.objects.get(school_class=primary_remote_class, subject=s1)
    cs4 = ClassSubject.objects.get(school_class=primary_remote_class, subject=s2)

    a1, _ = Assessment.objects.get_or_create(
        class_subject=cs1,
        title='Prova B1',
        defaults={'max_score': 10, 'assessment_date': date.today() - timedelta(days=5)},
    )
    Assessment.objects.get_or_create(
        class_subject=cs2,
        title='Redacao B1',
        defaults={'max_score': 10, 'assessment_date': date.today() - timedelta(days=3)},
    )
    a3, _ = Assessment.objects.get_or_create(
        class_subject=cs3,
        title='Quiz Online B1',
        defaults={'max_score': 10, 'assessment_date': date.today() - timedelta(days=2)},
    )
    Assessment.objects.get_or_create(
        class_subject=cs4,
        title='Forum Avaliativo B1',
        defaults={'max_score': 10, 'assessment_date': date.today() - timedelta(days=1)},
    )

    for index in range(1, 101):
        registration = f'2026{index:03d}'
        is_in_person = index <= 50
        if index % 10 == 0:
            student_status = Student.INACTIVE
        elif index % 4 == 0:
            student_status = Student.ATTENTION
        else:
            student_status = Student.ACTIVE

        if is_in_person:
            course_name = IN_PERSON_COURSES[(index - 1) % len(IN_PERSON_COURSES)]
            class_choice = in_person_classes[(index - 1) % len(in_person_classes)]
        else:
            course_name = REMOTE_COURSES[(index - 51) % len(REMOTE_COURSES)]
            class_choice = remote_classes[(index - 51) % len(remote_classes)]

        student, _ = Student.objects.update_or_create(
            registration=registration,
            defaults={
                'full_name': _build_student_name(index),
                'birth_date': date(2008 + (index % 5), ((index - 1) % 12) + 1, ((index - 1) % 28) + 1),
                'guardian_name': f'Responsavel {index:03d}',
                'guardian_phone': f'(11) 9{(index % 9) + 1}{(index * 37) % 1000:03d}-{(index * 83) % 10000:04d}',
                'learning_mode': Student.IN_PERSON if is_in_person else Student.REMOTE,
                'abstract_course': course_name,
                'status': student_status,
            },
        )

        Enrollment.objects.filter(student=student).exclude(school_class=class_choice).delete()
        enrollment_status = Enrollment.TRANSFERRED if student_status == Student.INACTIVE else Enrollment.ACTIVE
        enrollment, _ = Enrollment.objects.update_or_create(
            student=student,
            school_class=class_choice,
            defaults={'status': enrollment_status},
        )

        assessment = a1 if is_in_person else a3
        score = round(6 + ((index * 7) % 35) / 10, 1)
        Grade.objects.update_or_create(assessment=assessment, enrollment=enrollment, defaults={'score': score})

        attendance_subject = cs1 if is_in_person else cs3
        AttendanceRecord.objects.update_or_create(
            class_subject=attendance_subject,
            enrollment=enrollment,
            attendance_date=date.today() - timedelta(days=1),
            defaults={'present': index % 6 != 0 and student_status != Student.INACTIVE},
        )

    valid_registrations = [f'2026{index:03d}' for index in range(1, 101)]
    Student.objects.filter(registration__startswith='2026').exclude(registration__in=valid_registrations).delete()

    valid_class_pairs = {(name, shift) for name, shift, _learning_mode, _coordinator in class_defaults}
    for stale_class in SchoolClass.objects.filter(year=date.today().year, name__in=[item[0] for item in class_defaults]):
        if (stale_class.name, stale_class.shift) not in valid_class_pairs and not stale_class.enrollments.exists():
            stale_class.delete()

    Announcement.objects.get_or_create(
        title='Reuniao com responsaveis',
        defaults={'body': 'Sexta-feira as 19h no auditorio principal.', 'level': Announcement.WARNING},
    )
    Announcement.objects.get_or_create(
        title='Diario liberado',
        defaults={'body': 'Lacamento de notas do bimestre disponivel para docentes.', 'level': Announcement.SUCCESS},
    )
    Announcement.objects.get_or_create(
        title='Ata docente homologada',
        defaults={'body': 'Documento oficial da reuniao pedagogica publicado para consulta interna.', 'level': Announcement.INFO},
    )

    AdministrativeProcess.objects.get_or_create(
        protocol='PROC-2026-001',
        defaults={
            'subject': 'Aquisição de kits de laboratorio',
            'sector': 'Administracao',
            'status': AdministrativeProcess.IN_PROGRESS,
            'deadline': date.today() + timedelta(days=7),
        },
    )
    AdministrativeProcess.objects.get_or_create(
        protocol='PROC-2026-002',
        defaults={
            'subject': 'Contratacao de plataforma educacional',
            'sector': 'Tec. da Informacao',
            'status': AdministrativeProcess.OPEN,
            'deadline': date.today() + timedelta(days=12),
        },
    )

    ManagementPlan.objects.get_or_create(
        title='Plano de entregas do bimestre',
        defaults={
            'owner': 'Diretoria Academica',
            'progress': 62,
            'status': ManagementPlan.ACTIVE,
            'due_date': date.today() + timedelta(days=15),
        },
    )
    ManagementPlan.objects.get_or_create(
        title='Pactuacao de metas administrativas',
        defaults={
            'owner': 'Coordenacao Administrativa',
            'progress': 35,
            'status': ManagementPlan.DRAFT,
            'due_date': date.today() + timedelta(days=20),
        },
    )

    project_defaults = [
        ('Projeto Horizonte', InstitutionalProject.RESEARCH, teachers[0], InstitutionalProject.ACTIVE),
        ('Rede Comunidade Viva', InstitutionalProject.EXTENSION, teachers[1], InstitutionalProject.ACTIVE),
        ('Programa Global Campus', InstitutionalProject.INTERNATIONAL, teachers[0], InstitutionalProject.DRAFT),
        ('Painel de Indicadores 2026', InstitutionalProject.DEVELOPMENT, teachers[1], InstitutionalProject.ACTIVE),
        ('Ciclo de Apoio ao Estudante', InstitutionalProject.STUDENT, teachers[2], InstitutionalProject.ACTIVE),
        ('Campanha Institucional 2026', InstitutionalProject.COMMUNICATION, teachers[3], InstitutionalProject.ACTIVE),
        ('Trilha de Conformidade Interna', InstitutionalProject.AUDIT, teachers[4], InstitutionalProject.DRAFT),
    ]
    for idx, project in enumerate(project_defaults, start=1):
        title, project_type, coordinator, status = project
        InstitutionalProject.objects.get_or_create(
            title=title,
            defaults={
                'project_type': project_type,
                'coordinator': coordinator,
                'status': status,
                'start_date': date.today() - timedelta(days=idx * 3),
            },
        )

    ticket_defaults = [
        (ServiceDeskTicket.CENTRAL, 'Setor Academico', 'Atualizacao de atendimento', ServiceDeskTicket.MEDIUM, ServiceDeskTicket.WORKING),
        (ServiceDeskTicket.IT, 'Laboratorio 02', 'Falha em rede local', ServiceDeskTicket.HIGH, ServiceDeskTicket.OPEN),
        (ServiceDeskTicket.SECURITY, 'Portaria Norte', 'Revisao de acesso', ServiceDeskTicket.MEDIUM, ServiceDeskTicket.WORKING),
        (ServiceDeskTicket.ADMIN, 'Compras', 'Analise de requisicao 418', ServiceDeskTicket.LOW, ServiceDeskTicket.OPEN),
    ]
    for area, requester, subject, priority, status in ticket_defaults:
        ServiceDeskTicket.objects.get_or_create(
            area=area,
            requester=requester,
            subject=subject,
            defaults={'priority': priority, 'status': status},
        )


# Existing app pages

def dashboard(request):
    seed_school_data()

    total_students = Student.objects.count()
    total_classes = SchoolClass.objects.count()
    total_enrollments = Enrollment.objects.filter(status=Enrollment.ACTIVE).count()
    avg_grade = Grade.objects.aggregate(value=Avg('score')).get('value') or 0
    in_person_students = Student.objects.filter(learning_mode=Student.IN_PERSON).count()
    remote_students = Student.objects.filter(learning_mode=Student.REMOTE).count()
    in_person_classes = SchoolClass.objects.filter(learning_mode=SchoolClass.IN_PERSON).count()
    remote_classes = SchoolClass.objects.filter(learning_mode=SchoolClass.REMOTE).count()

    class_distribution = list(
        Enrollment.objects.values('school_class__name').annotate(total=Count('id')).order_by('school_class__name')
    )

    context = {
        'total_students': total_students,
        'total_classes': total_classes,
        'total_enrollments': total_enrollments,
        'avg_grade': round(avg_grade, 2),
        'in_person_students': in_person_students,
        'remote_students': remote_students,
        'in_person_classes': in_person_classes,
        'remote_classes': remote_classes,
        'announcements': Announcement.objects.all()[:4],
        'recent_enrollments': Enrollment.objects.select_related('student', 'school_class')[:8],
        'recent_attendance': AttendanceRecord.objects.select_related('enrollment__student').order_by('-attendance_date')[:8],
        'class_distribution': class_distribution,
        'total_courses': len(IN_PERSON_COURSES) + len(REMOTE_COURSES),
    }
    return render(request, 'dashboard.html', context)


def students_page(request):
    seed_school_data()
    form = StudentFilterForm(request.GET or None)
    students = Student.objects.all()

    if form.is_valid():
        query = form.cleaned_data.get('query')
        class_filter = form.cleaned_data.get('class_filter')
        learning_mode = form.cleaned_data.get('learning_mode')
        status = form.cleaned_data.get('status')

        if query:
            students = students.filter(full_name__icontains=query)
        if class_filter:
            students = students.filter(enrollments__school_class=class_filter).distinct()
        if learning_mode:
            students = students.filter(learning_mode=learning_mode)
        if status:
            students = students.filter(status=status)

    return render(request, 'students.html', {'students': students, 'filter_form': form})


def student_create(request):
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Aluno cadastrado com sucesso.')
        return redirect('students_page')
    return render(request, 'student_form.html', {'form': form, 'page_title': 'Novo Aluno'})


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Aluno atualizado com sucesso.')
        return redirect('students_page')
    return render(request, 'student_form.html', {'form': form, 'page_title': 'Editar Aluno'})


def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Aluno excluido com sucesso.')
        return redirect('students_page')
    return render(request, 'student_confirm_delete.html', {'student': student})


def classes_page(request):
    seed_school_data()
    form = SchoolClassFilterForm(request.GET or None)
    classes = SchoolClass.objects.select_related('coordinator').prefetch_related('subjects__subject', 'subjects__teacher').all()
    if form.is_valid():
        learning_mode = form.cleaned_data.get('learning_mode')
        shift = form.cleaned_data.get('shift')
        if learning_mode:
            classes = classes.filter(learning_mode=learning_mode)
        if shift:
            classes = classes.filter(shift=shift)
    return render(
        request,
        'classes.html',
        {
            'filter_form': form,
            'in_person_classes': classes.filter(learning_mode=SchoolClass.IN_PERSON),
            'remote_classes': classes.filter(learning_mode=SchoolClass.REMOTE),
        },
    )


def enrollments_page(request):
    seed_school_data()
    form = EnrollmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Matricula registrada com sucesso.')
        return redirect('enrollments_page')

    enrollments = Enrollment.objects.select_related('student', 'school_class').all()[:30]
    return render(request, 'enrollments.html', {'form': form, 'enrollments': enrollments})


def grades_page(request):
    seed_school_data()
    form = GradeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Grade.objects.update_or_create(
            assessment=form.cleaned_data['assessment'],
            enrollment=form.cleaned_data['enrollment'],
            defaults={'score': form.cleaned_data['score']},
        )
        messages.success(request, 'Nota salva com sucesso.')
        return redirect('grades_page')

    grades = Grade.objects.select_related(
        'assessment__class_subject__school_class',
        'assessment__class_subject__subject',
        'enrollment__student',
    ).order_by('-assessment__assessment_date')
    return render(
        request,
        'grades.html',
        {
            'form': form,
            'in_person_grades': grades.filter(
                assessment__class_subject__school_class__learning_mode=SchoolClass.IN_PERSON
            )[:30],
            'remote_grades': grades.filter(
                assessment__class_subject__school_class__learning_mode=SchoolClass.REMOTE
            )[:30],
        },
    )


def attendance_page(request):
    seed_school_data()
    form = AttendanceRecordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        AttendanceRecord.objects.update_or_create(
            class_subject=form.cleaned_data['class_subject'],
            enrollment=form.cleaned_data['enrollment'],
            attendance_date=form.cleaned_data['attendance_date'],
            defaults={'present': form.cleaned_data['present']},
        )
        messages.success(request, 'Frequencia salva com sucesso.')
        return redirect('attendance_page')

    records = AttendanceRecord.objects.select_related(
        'class_subject__school_class',
        'class_subject__subject',
        'enrollment__student',
    ).all()
    return render(
        request,
        'attendance.html',
        {
            'form': form,
            'in_person_records': records.filter(class_subject__school_class__learning_mode=SchoolClass.IN_PERSON)[:30],
            'remote_records': records.filter(class_subject__school_class__learning_mode=SchoolClass.REMOTE)[:30],
        },
    )


def agenda_page(request):
    seed_school_data()
    upcoming = [
        {'date': date.today() + timedelta(days=1), 'title': 'Conselho de classe', 'type': 'Academico'},
        {'date': date.today() + timedelta(days=3), 'title': 'Reuniao de pais', 'type': 'Institucional'},
        {'date': date.today() + timedelta(days=7), 'title': 'Simulado geral', 'type': 'Avaliacao'},
    ]
    return render(request, 'agenda.html', {'events': upcoming})


def class_diary_page(request):
    seed_school_data()
    classes = SchoolClass.objects.select_related('coordinator').order_by('learning_mode', 'name')
    requested_class_id = request.GET.get('class_id')
    selected_class = classes.filter(pk=requested_class_id).first() if requested_class_id else classes.first()

    diary_rows = []
    attendance_rate = 0
    subject_load = []
    if selected_class is not None:
        class_subjects = list(selected_class.subjects.select_related('subject', 'teacher').all())
        enrollments = list(
            Enrollment.objects.filter(school_class=selected_class)
            .select_related('student')
            .order_by('student__full_name')
        )

        subject_load = [
            {'name': item.subject.name, 'teacher': item.teacher.full_name, 'code': item.subject.code}
            for item in class_subjects
        ]

        records = AttendanceRecord.objects.filter(
            class_subject__school_class=selected_class,
            enrollment__in=enrollments,
        )
        total_attendance = records.count()
        present_attendance = records.filter(present=True).count()
        attendance_rate = round((present_attendance / total_attendance) * 100, 1) if total_attendance else 0

        for enrollment in enrollments:
            latest_grade = (
                Grade.objects.filter(
                    enrollment=enrollment,
                    assessment__class_subject__school_class=selected_class,
                )
                .order_by('-assessment__assessment_date')
                .first()
            )
            student_records = records.filter(enrollment=enrollment)
            total_records = student_records.count()
            present_records = student_records.filter(present=True).count()
            student_attendance = round((present_records / total_records) * 100, 1) if total_records else 0
            diary_rows.append(
                {
                    'student': enrollment.student.full_name,
                    'registration': enrollment.student.registration,
                    'course': enrollment.student.abstract_course,
                    'mode': enrollment.student.get_learning_mode_display(),
                    'status': enrollment.student.get_status_display(),
                    'grade': latest_grade.score if latest_grade else '-',
                    'attendance': f'{student_attendance}%',
                }
            )

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'diary_rows': diary_rows,
        'attendance_rate': attendance_rate,
        'total_courses': len(IN_PERSON_COURSES) + len(REMOTE_COURSES),
        'active_count': Student.objects.filter(status=Student.ACTIVE).count(),
        'subject_load': subject_load,
    }
    return render(request, 'class_diary.html', context)


def teachers_minutes_page(request):
    seed_school_data()
    deliberations = [
        'Ratificada a distribuicao de 20 cursos institucionais, sendo 10 presenciais e 10 remotos, para atendimento regular do periodo letivo.',
        'Aprovado o acompanhamento semanal do diario de classe com prioridade para turmas com alunos em situacao de atencao.',
        'Definida a comunicacao formal aos responsaveis de estudantes inativos para regularizacao academica e documental.',
        'Homologado o cronograma de revisao pedagogica e de consolidacao das notas parciais pelas coordenacoes.',
    ]
    context = {
        'meeting_date': date.today(),
        'teachers': Teacher.objects.all(),
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(status=Student.ACTIVE).count(),
        'attention_students': Student.objects.filter(status=Student.ATTENTION).count(),
        'inactive_students': Student.objects.filter(status=Student.INACTIVE).count(),
        'in_person_students': Student.objects.filter(learning_mode=Student.IN_PERSON).count(),
        'remote_students': Student.objects.filter(learning_mode=Student.REMOTE).count(),
        'total_courses': len(IN_PERSON_COURSES) + len(REMOTE_COURSES),
        'deliberations': deliberations,
    }
    return render(request, 'teachers_minutes.html', context)


# Module pages

def module_page(request, module_key):
    seed_school_data()
    config = MODULE_CONFIG.get(module_key)
    if config is None:
        raise Http404('Modulo nao encontrado.')

    kind = config['kind']
    if kind == 'process':
        return _process_module_page(request, module_key, config)
    if kind == 'plan':
        return _plan_module_page(request, module_key, config)
    if kind == 'project':
        return _project_module_page(request, module_key, config)
    if kind == 'ticket':
        return _ticket_module_page(request, module_key, config)
    if kind == 'teaching':
        return _teaching_module_page(request, module_key, config)
    if kind == 'people':
        return _people_module_page(request, module_key, config)
    if kind == 'exit':
        return _exit_module_page(request, module_key, config)
    raise Http404('Modulo nao configurado.')


def _render_operational_module(request, config, module_key, form, items, table_headers, row_builder):
    rows = [row_builder(item) for item in items]
    context = {
        'module_key': module_key,
        'module_title': config['title'],
        'module_description': config['description'],
        'form': form,
        'table_headers': table_headers,
        'table_rows': rows,
    }
    return render(request, 'module_operational.html', context)


def _process_module_page(request, module_key, config):
    form = AdministrativeProcessForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Processo registrado com sucesso.')
        return redirect('module_page', module_key=module_key)

    items = AdministrativeProcess.objects.all()[:20]
    return _render_operational_module(
        request,
        config,
        module_key,
        form,
        items,
        ['Protocolo', 'Assunto', 'Setor', 'Status', 'Prazo'],
        lambda item: [item.protocol, item.subject, item.sector, item.get_status_display(), item.deadline.strftime('%d/%m/%Y')],
    )


def _plan_module_page(request, module_key, config):
    form = ManagementPlanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Plano registrado com sucesso.')
        return redirect('module_page', module_key=module_key)

    items = ManagementPlan.objects.all()[:20]
    return _render_operational_module(
        request,
        config,
        module_key,
        form,
        items,
        ['Plano', 'Responsavel', 'Progresso', 'Status', 'Prazo'],
        lambda item: [item.title, item.owner, f'{item.progress}%', item.get_status_display(), item.due_date.strftime('%d/%m/%Y')],
    )


def _project_module_page(request, module_key, config):
    form = InstitutionalProjectForm(request.POST or None)
    form.fields['project_type'].initial = config['project_type']
    form.fields['project_type'].disabled = True
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        project.project_type = config['project_type']
        project.save()
        messages.success(request, 'Projeto registrado com sucesso.')
        return redirect('module_page', module_key=module_key)

    items = InstitutionalProject.objects.filter(project_type=config['project_type']).select_related('coordinator')[:20]
    return _render_operational_module(
        request,
        config,
        module_key,
        form,
        items,
        ['Projeto', 'Coordenacao', 'Status', 'Inicio'],
        lambda item: [
            item.title,
            item.coordinator.full_name if item.coordinator else 'Nao definida',
            item.get_status_display(),
            item.start_date.strftime('%d/%m/%Y'),
        ],
    )


def _ticket_module_page(request, module_key, config):
    form = ServiceDeskTicketForm(request.POST or None)
    form.fields['area'].initial = config['area']
    form.fields['area'].disabled = True
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.area = config['area']
        ticket.save()
        messages.success(request, 'Chamado registrado com sucesso.')
        return redirect('module_page', module_key=module_key)

    items = ServiceDeskTicket.objects.filter(area=config['area'])[:20]
    return _render_operational_module(
        request,
        config,
        module_key,
        form,
        items,
        ['Solicitante', 'Assunto', 'Prioridade', 'Status'],
        lambda item: [item.requester, item.subject, item.get_priority_display(), item.get_status_display()],
    )


def _teaching_module_page(request, module_key, config):
    context = {
        'module_key': module_key,
        'module_title': config['title'],
        'module_description': config['description'],
        'summary_cards': [
            {'label': 'Alunos ativos', 'value': Student.objects.filter(status=Student.ACTIVE).count(), 'badge': 'Cadastro em dia'},
            {'label': 'Turmas abertas', 'value': SchoolClass.objects.count(), 'badge': 'Ano letivo atual'},
            {'label': 'Avaliacoes', 'value': Assessment.objects.count(), 'badge': 'Ciclos registrados'},
        ],
        'table_headers': ['Area', 'Indicador', 'Valor'],
        'table_rows': [
            ['Ensino', 'Media geral', f"{round(Grade.objects.aggregate(value=Avg('score')).get('value') or 0, 2)}"],
            ['Ensino', 'Frequencias registradas', str(AttendanceRecord.objects.count())],
            ['Ensino', 'Matriculas ativas', str(Enrollment.objects.filter(status=Enrollment.ACTIVE).count())],
        ],
        'quick_links': [
            {'label': 'Abrir Alunos', 'url_name': 'students_page'},
            {'label': 'Abrir Turmas', 'url_name': 'classes_page'},
            {'label': 'Abrir Notas', 'url_name': 'grades_page'},
            {'label': 'Abrir Frequencia', 'url_name': 'attendance_page'},
        ],
    }
    return render(request, 'module_overview.html', context)


def _people_module_page(request, module_key, config):
    teachers = Teacher.objects.all()[:20]
    context = {
        'module_key': module_key,
        'module_title': config['title'],
        'module_description': config['description'],
        'summary_cards': [
            {'label': 'Docentes cadastrados', 'value': Teacher.objects.count(), 'badge': 'Base institucional'},
            {'label': 'Turmas coordenadas', 'value': SchoolClass.objects.exclude(coordinator=None).count(), 'badge': 'Distribuicao ativa'},
            {'label': 'Disciplinas alocadas', 'value': ClassSubject.objects.count(), 'badge': 'Alocacao atual'},
        ],
        'table_headers': ['Servidor', 'Matricula', 'Email'],
        'table_rows': [[item.full_name, item.employee_code, item.email or '-'] for item in teachers],
        'quick_links': [
            {'label': 'Abrir Turmas', 'url_name': 'classes_page'},
            {'label': 'Abrir Ensino', 'url_name': 'module_page', 'url_arg': 'ensino'},
        ],
    }
    return render(request, 'module_overview.html', context)


def _exit_module_page(request, module_key, config):
    context = {
        'module_key': module_key,
        'module_title': config['title'],
        'module_description': config['description'],
        'summary_cards': [
            {'label': 'Sessao local', 'value': 'Encerrar', 'badge': 'Controle manual'},
            {'label': 'Retorno rapido', 'value': 'Painel', 'badge': 'Acesso seguro'},
            {'label': 'Estado', 'value': 'Ativo', 'badge': 'Sistema online'},
        ],
        'table_headers': ['Acao', 'Descricao'],
        'table_rows': [
            ['Voltar ao inicio', 'Retorna para a pagina principal do sistema.'],
            ['Fechar navegador', 'Encerramento manual no dispositivo local.'],
            ['Manter sessao', 'Continuar navegando nos modulos.'],
        ],
        'quick_links': [
            {'label': 'Voltar ao Painel', 'url_name': 'dashboard'},
        ],
    }
    return render(request, 'module_overview.html', context)
