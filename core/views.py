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


def seed_school_data():
    t1, _ = Teacher.objects.get_or_create(
        employee_code='DOC001',
        defaults={'full_name': 'Ana Beatriz', 'email': 'ana@escola.edu.br'},
    )
    t2, _ = Teacher.objects.get_or_create(
        employee_code='DOC002',
        defaults={'full_name': 'Rafael Lima', 'email': 'rafael@escola.edu.br'},
    )

    c1, _ = SchoolClass.objects.get_or_create(
        name='1A',
        year=date.today().year,
        shift=SchoolClass.MORNING,
        defaults={'coordinator': t1, 'learning_mode': SchoolClass.IN_PERSON},
    )
    c2, _ = SchoolClass.objects.get_or_create(
        name='2B',
        year=date.today().year,
        shift=SchoolClass.AFTERNOON,
        defaults={'coordinator': t2, 'learning_mode': SchoolClass.REMOTE},
    )
    if c1.coordinator_id is None:
        c1.coordinator = t1
    c1.learning_mode = SchoolClass.IN_PERSON
    c1.save(update_fields=['coordinator', 'learning_mode'])
    if c2.coordinator_id is None:
        c2.coordinator = t2
    c2.learning_mode = SchoolClass.REMOTE
    c2.save(update_fields=['coordinator', 'learning_mode'])

    s1, _ = Subject.objects.get_or_create(
        code='MAT101',
        defaults={'name': 'Matematica', 'workload_hours': 80},
    )
    s2, _ = Subject.objects.get_or_create(
        code='POR101',
        defaults={'name': 'Portugues', 'workload_hours': 80},
    )

    cs1, _ = ClassSubject.objects.get_or_create(school_class=c1, subject=s1, defaults={'teacher': t1})
    cs2, _ = ClassSubject.objects.get_or_create(school_class=c1, subject=s2, defaults={'teacher': t2})
    cs3, _ = ClassSubject.objects.get_or_create(school_class=c2, subject=s1, defaults={'teacher': t1})
    cs4, _ = ClassSubject.objects.get_or_create(school_class=c2, subject=s2, defaults={'teacher': t2})

    st1, _ = Student.objects.update_or_create(
        registration='2026001',
        defaults={
            'full_name': 'Lia Nobre',
            'birth_date': date(2010, 5, 13),
            'guardian_name': 'Responsavel A-17',
            'guardian_phone': '(11) 99999-1111',
            'learning_mode': Student.IN_PERSON,
            'abstract_course': 'Laboratorio Criativo Presencial',
            'status': Student.ACTIVE,
        },
    )
    st2, _ = Student.objects.update_or_create(
        registration='2026002',
        defaults={
            'full_name': 'Caio Vilar',
            'birth_date': date(2010, 8, 23),
            'guardian_name': 'Responsavel B-09',
            'guardian_phone': '(11) 98888-2222',
            'learning_mode': Student.REMOTE,
            'abstract_course': 'Trilha Digital Remota',
            'status': Student.ATTENTION,
        },
    )
    st3, _ = Student.objects.update_or_create(
        registration='2026003',
        defaults={
            'full_name': 'Nina Aster',
            'birth_date': date(2011, 2, 4),
            'guardian_name': 'Responsavel C-21',
            'guardian_phone': '(11) 97777-3333',
            'learning_mode': Student.IN_PERSON,
            'abstract_course': 'Oficina de Projeto Integrado',
            'status': Student.ACTIVE,
        },
    )
    st4, _ = Student.objects.update_or_create(
        registration='2026004',
        defaults={
            'full_name': 'Theo Vale',
            'birth_date': date(2011, 9, 14),
            'guardian_name': 'Responsavel D-04',
            'guardian_phone': '(11) 96666-4444',
            'learning_mode': Student.REMOTE,
            'abstract_course': 'Programa Sincrono Online',
            'status': Student.INACTIVE,
        },
    )

    e1, _ = Enrollment.objects.get_or_create(student=st1, school_class=c1, defaults={'status': Enrollment.ACTIVE})
    e2, _ = Enrollment.objects.get_or_create(student=st2, school_class=c1, defaults={'status': Enrollment.ACTIVE})
    e3, _ = Enrollment.objects.get_or_create(student=st3, school_class=c2, defaults={'status': Enrollment.ACTIVE})
    e4, _ = Enrollment.objects.get_or_create(student=st4, school_class=c2, defaults={'status': Enrollment.TRANSFERRED})

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

    Grade.objects.update_or_create(assessment=a1, enrollment=e1, defaults={'score': 8.5})
    Grade.objects.update_or_create(assessment=a1, enrollment=e2, defaults={'score': 6.5})
    Grade.objects.update_or_create(assessment=a3, enrollment=e3, defaults={'score': 9.1})
    Grade.objects.update_or_create(assessment=a3, enrollment=e4, defaults={'score': 7.3})

    AttendanceRecord.objects.update_or_create(
        class_subject=cs1,
        enrollment=e1,
        attendance_date=date.today() - timedelta(days=1),
        defaults={'present': True},
    )
    AttendanceRecord.objects.update_or_create(
        class_subject=cs1,
        enrollment=e2,
        attendance_date=date.today() - timedelta(days=1),
        defaults={'present': False},
    )
    AttendanceRecord.objects.update_or_create(
        class_subject=cs3,
        enrollment=e3,
        attendance_date=date.today() - timedelta(days=1),
        defaults={'present': True},
    )
    AttendanceRecord.objects.update_or_create(
        class_subject=cs3,
        enrollment=e4,
        attendance_date=date.today() - timedelta(days=1),
        defaults={'present': True},
    )

    Announcement.objects.get_or_create(
        title='Reuniao com responsaveis',
        defaults={'body': 'Sexta-feira as 19h no auditorio principal.', 'level': Announcement.WARNING},
    )
    Announcement.objects.get_or_create(
        title='Diario liberado',
        defaults={'body': 'Lacamento de notas do bimestre disponivel para docentes.', 'level': Announcement.SUCCESS},
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
        ('Projeto Horizonte', InstitutionalProject.RESEARCH, t1, InstitutionalProject.ACTIVE),
        ('Rede Comunidade Viva', InstitutionalProject.EXTENSION, t2, InstitutionalProject.ACTIVE),
        ('Programa Global Campus', InstitutionalProject.INTERNATIONAL, t1, InstitutionalProject.DRAFT),
        ('Painel de Indicadores 2026', InstitutionalProject.DEVELOPMENT, t2, InstitutionalProject.ACTIVE),
        ('Ciclo de Apoio ao Estudante', InstitutionalProject.STUDENT, t1, InstitutionalProject.ACTIVE),
        ('Campanha Institucional 2026', InstitutionalProject.COMMUNICATION, t2, InstitutionalProject.ACTIVE),
        ('Trilha de Conformidade Interna', InstitutionalProject.AUDIT, t1, InstitutionalProject.DRAFT),
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
