from datetime import date, timedelta
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from .forms import (
    AttendanceRecordForm,
    EnrollmentForm,
    GradeForm,
    SchoolClassFilterForm,
    StudentFilterForm,
    StudentForm,
)
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


MODULE_PAGES = {
    'documentos-processos': {
        'title': 'Documentos/Processos',
        'description': 'Painel de tramitacao documental, fluxo interno e acompanhamento de processos administrativos.',
        'highlights': ['Protocolos em aberto', 'Caixa de entrada setorial', 'Prazos de despacho'],
        'actions': ['Novo processo', 'Consultar protocolo', 'Relatorio de andamento'],
    },
    'programa-gestao': {
        'title': 'Programa de Gestao',
        'description': 'Acompanhamento de planos de entrega, produtividade e pactuacao de metas institucionais.',
        'highlights': ['Metas em curso', 'Pendencias de aprovacao', 'Ciclos de avaliacao'],
        'actions': ['Abrir plano', 'Validar entregas', 'Emitir consolidado'],
    },
    'ensino': {
        'title': 'Ensino',
        'description': 'Gestao academica de turmas, diarios, horarios, componentes curriculares e calendarios letivos.',
        'highlights': ['Turmas ativas', 'Diarios pendentes', 'Aulas previstas'],
        'actions': ['Abrir diario', 'Montar horario', 'Fechar etapa'],
    },
    'pesquisa': {
        'title': 'Pesquisa',
        'description': 'Controle de editais, projetos, bolsistas e acompanhamento de execucao tecnica.',
        'highlights': ['Projetos vigentes', 'Bolsas ativas', 'Prestacoes pendentes'],
        'actions': ['Novo projeto', 'Avaliar proposta', 'Exportar indicadores'],
    },
    'extensao': {
        'title': 'Extensao',
        'description': 'Gerenciamento de acoes extensionistas, programas, eventos e certificacoes.',
        'highlights': ['Acoes abertas', 'Inscricoes em analise', 'Certificados emitidos'],
        'actions': ['Cadastrar acao', 'Gerar certificado', 'Publicar chamada'],
    },
    'gestao-pessoas': {
        'title': 'Gestao de Pessoas',
        'description': 'Painel de servidores, afastamentos, ferias, lotacoes e autorizacoes funcionais.',
        'highlights': ['Ferias agendadas', 'Solicitacoes em fila', 'Movimentacoes internas'],
        'actions': ['Consultar servidor', 'Registrar afastamento', 'Liberar solicitacao'],
    },
    'administracao': {
        'title': 'Administracao',
        'description': 'Suporte a compras, contratos, patrimonio, almoxarifado e rotinas administrativas.',
        'highlights': ['Requisicoes abertas', 'Contratos vigentes', 'Patrimonio monitorado'],
        'actions': ['Nova requisicao', 'Acompanhar contrato', 'Inventario rapido'],
    },
    'tec-informacao': {
        'title': 'Tec. da Informacao',
        'description': 'Monitoramento de chamados, ativos de TI, acesso a sistemas e catalogo tecnico.',
        'highlights': ['Chamados abertos', 'Equipamentos ativos', 'Acessos pendentes'],
        'actions': ['Abrir chamado', 'Registrar ativo', 'Liberar acesso'],
    },
    'desenvolvimento-institucional': {
        'title': 'Des. Institucional',
        'description': 'Acompanhamento de indicadores, metas estrategicas, planejamento e governanca.',
        'highlights': ['Indicadores criticos', 'Planos em revisao', 'Acoes estrategicas'],
        'actions': ['Abrir painel', 'Atualizar meta', 'Gerar relatorio'],
    },
    'central-servicos': {
        'title': 'Central de Servicos',
        'description': 'Centralizacao de atendimentos, filas, SLA e resolucao de demandas internas.',
        'highlights': ['Solicitacoes ativas', 'SLA no limite', 'Equipes em atendimento'],
        'actions': ['Novo atendimento', 'Priorizar fila', 'Fechar demanda'],
    },
    'internacionalizacao': {
        'title': 'Internacionalizacao',
        'description': 'Gestao de mobilidade, convenios, editais internacionais e acompanhamento de intercambios.',
        'highlights': ['Convenios ativos', 'Editais abertos', 'Mobilidades em curso'],
        'actions': ['Abrir edital', 'Registrar convenio', 'Emitir acompanhamento'],
    },
    'atividades-estudantis': {
        'title': 'Atividades Estudantis',
        'description': 'Acompanhamento de assistencia estudantil, auxilios, participacoes e beneficios.',
        'highlights': ['Auxilios ativos', 'Analises pendentes', 'Atendimentos estudantis'],
        'actions': ['Nova solicitacao', 'Avaliar beneficio', 'Emitir lista'],
    },
    'comunicacao-social': {
        'title': 'Comunicacao Social',
        'description': 'Planejamento de campanhas, publicacoes, agenda institucional e comunicados oficiais.',
        'highlights': ['Campanhas abertas', 'Publicacoes agendadas', 'Demandas de comunicacao'],
        'actions': ['Criar comunicado', 'Agendar publicacao', 'Organizar campanha'],
    },
    'seguranca-institucional': {
        'title': 'Seguranca Institucional',
        'description': 'Controle de ocorrencias, acessos, rondas e protocolos de seguranca.',
        'highlights': ['Ocorrencias recentes', 'Acessos monitorados', 'Protocolos ativos'],
        'actions': ['Registrar ocorrencia', 'Abrir ronda', 'Consultar protocolo'],
    },
    'auditoria': {
        'title': 'Auditoria',
        'description': 'Acompanhamento de evidencias, planos de acao, recomendacoes e conformidade.',
        'highlights': ['Achados abertos', 'Planos em execucao', 'Prazos de resposta'],
        'actions': ['Nova analise', 'Anexar evidencia', 'Emitir parecer'],
    },
    'sair': {
        'title': 'Sair',
        'description': 'Sessao local encerrada. Utilize esta area para finalizar a navegacao e retornar ao inicio.',
        'highlights': ['Sessao finalizada', 'Acesso encerrado', 'Retorno seguro'],
        'actions': ['Voltar ao inicio', 'Abrir painel', 'Encerrar navegador'],
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

    cs1, _ = ClassSubject.objects.get_or_create(
        school_class=c1,
        subject=s1,
        defaults={'teacher': t1},
    )
    cs2, _ = ClassSubject.objects.get_or_create(
        school_class=c1,
        subject=s2,
        defaults={'teacher': t2},
    )
    cs3, _ = ClassSubject.objects.get_or_create(
        school_class=c2,
        subject=s1,
        defaults={'teacher': t1},
    )
    cs4, _ = ClassSubject.objects.get_or_create(
        school_class=c2,
        subject=s2,
        defaults={'teacher': t2},
    )

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
        defaults={
            'body': 'Sexta-feira as 19h no auditorio principal.',
            'level': Announcement.WARNING,
        },
    )
    Announcement.objects.get_or_create(
        title='Diario liberado',
        defaults={
            'body': 'Lacamento de notas do bimestre disponivel para docentes.',
            'level': Announcement.SUCCESS,
        },
    )


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


def module_page(request, module_key):
    seed_school_data()
    module = MODULE_PAGES.get(module_key)
    if module is None:
        raise Http404('Modulo nao encontrado.')

    context = {
        'module_key': module_key,
        'module_title': module['title'],
        'module_description': module['description'],
        'module_highlights': module['highlights'],
        'module_actions': module['actions'],
    }
    return render(request, 'module_page.html', context)
