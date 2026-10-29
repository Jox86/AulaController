import streamlit as st
import pandas as pd
import json, csv, io, os, sqlite3, hashlib, hmac, secrets, time
from datetime import date, timedelta
st.set_page_config(page_title='AulaControl · Gestión académica', page_icon='🎓', layout='wide')

# Autenticación MVP: contraseñas PBKDF2, bloqueo temporal y roles.
AUTH_DB = os.environ.get("AULACONTROL_AUTH_DB", "aulacontrol_auth.sqlite3")
ROLES = {"admin": "Administrador", "profesor": "Profesor", "estudiante": "Estudiante"}

def auth_connect():
    con = sqlite3.connect(AUTH_DB, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, display_name TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','profesor','estudiante')), student_code TEXT, salt TEXT NOT NULL, password_hash TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
    con.commit()
    return con

def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 310000).hex()
    return salt, hashed

def verify_password(password, salt, expected):
    return hmac.compare_digest(password_hash(password, salt)[1], expected)

def secret_value(key):
    try:
        value = st.secrets.get(key, None)
        if value: return str(value)
    except Exception:
        pass
    return os.environ.get(key)

# Bootstrap seguro: no se crea ninguna contraseña predeterminada.
con = auth_connect()
if con.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
    bootstrap_user = secret_value('BOOTSTRAP_ADMIN_USERNAME')
    bootstrap_pass = secret_value('BOOTSTRAP_ADMIN_PASSWORD')
    if bootstrap_user and bootstrap_pass and len(bootstrap_pass) >= 12:
        salt, hashed = password_hash(bootstrap_pass)
        con.execute('INSERT OR IGNORE INTO users(username,display_name,role,salt,password_hash) VALUES(?,?,?,?,?)', (bootstrap_user.strip().lower(), 'Administrador principal', 'admin', salt, hashed))
        con.commit()
con.close()

if 'auth_user' not in st.session_state:
    st.session_state.auth_user = None
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
if 'login_locked_until' not in st.session_state:
    st.session_state.login_locked_until = 0

if not st.session_state.auth_user:
    st.markdown('# 🎓 AulaControl')
    st.subheader('Acceso seguro')
    st.caption('Inicia sesión con la cuenta institucional o la cuenta creada por el administrador.')
    con = auth_connect()
    has_users = con.execute('SELECT COUNT(*) FROM users').fetchone()[0] > 0
    con.close()
    if not has_users:
        st.error('AulaControl aún no está configurado. El administrador debe definir BOOTSTRAP_ADMIN_USERNAME y BOOTSTRAP_ADMIN_PASSWORD en Streamlit → Settings → Secrets. La contraseña inicial debe tener al menos 12 caracteres. No se habilita un registro público para evitar que un visitante tome el control del sistema.')
        st.stop()
    if time.time() < st.session_state.login_locked_until:
        st.error('Demasiados intentos. Espera 15 minutos antes de volver a intentarlo.')
        st.stop()
    with st.form('login_form', clear_on_submit=True):
        username = st.text_input('Usuario').strip().lower()
        password = st.text_input('Contraseña', type='password')
        submitted = st.form_submit_button('Iniciar sesión', use_container_width=True)
    if submitted:
        con = auth_connect()
        user = con.execute('SELECT * FROM users WHERE username=? AND active=1', (username,)).fetchone()
        con.close()
        if user and verify_password(password, user['salt'], user['password_hash']):
            st.session_state.auth_user = {'id': user['id'], 'username': user['username'], 'display_name': user['display_name'], 'role': user['role'], 'student_code': user['student_code']}
            st.session_state.login_attempts = 0
            st.rerun()
        else:
            st.session_state.login_attempts += 1
            if st.session_state.login_attempts >= 5:
                st.session_state.login_locked_until = time.time() + 900
                st.session_state.login_attempts = 0
                st.error('Demasiados intentos fallidos. Acceso bloqueado durante 15 minutos en esta sesión.')
            else:
                st.error('Usuario o contraseña incorrectos.')
    st.caption('Las cuentas se crean desde la administración. No compartas tu contraseña.')
    st.stop()


# AulaControl full Streamlit adaptation of the included React MVP.
def seed():
    return {
      'students':[
        {'id':1,'name':'Ana Rodríguez','code':'IC-2401','group':'2A','attendance':92,'grades':[9,8,9,8],'published':True},
        {'id':2,'name':'Carlos Méndez','code':'IC-2402','group':'2A','attendance':78,'grades':[7,6,8,7],'published':True},
        {'id':3,'name':'Lucía Pérez','code':'IC-2403','group':'2A','attendance':48,'grades':[8,9,None,None],'published':False},
        {'id':4,'name':'Daniel Torres','code':'IC-2404','group':'2A','attendance':86,'grades':[6,7,7,None],'published':False},
        {'id':5,'name':'María Suárez','code':'IC-2405','group':'2A','attendance':96,'grades':[10,9,10,9],'published':True},
        {'id':6,'name':'Jorge Díaz','code':'IC-2406','group':'2A','attendance':61,'grades':[5,6,7,6],'published':True}],
      'sessions':[{'id':1,'date':str(date.today()),'topic':'Estructuras de datos: listas','type':'Clase','status':'Planificada'}, {'id':2,'date':str(date.today()+timedelta(days=1)),'topic':'Práctica de laboratorio','type':'Práctica','status':'Pendiente'}],
      'lessons':[{'id':1,'title':'Introducción a la asignatura','unit':'Unidad 1','date':'2026-10-20','notes':'Presentación, objetivos y entorno de trabajo.'}],
      'tasks':[{'id':1,'title':'Tarjeta de presentación con HTML y CSS','due':'2026-11-03','status':'Abierta'}],
      'resources':[{'title':'Documentación HTML','author':'MDN Web Docs','url':'https://developer.mozilla.org/es/docs/Web/HTML'}]
    }
if 'db' not in st.session_state: st.session_state.db=seed()
if 'subject' not in st.session_state: st.session_state.subject='Programación Web'
if 'term' not in st.session_state: st.session_state.term='2026 · Semestre 1'
if 'active' not in st.session_state: st.session_state.active='Resumen'
if 'dark' not in st.session_state: st.session_state.dark=True

db=st.session_state.db

def avg(nums):
    v=[float(n) for n in nums if n is not None and n!='']
    return sum(v)/len(v) if v else None
def metrics(s):
    sys=avg(s['grades'][:2]); c1=(sys+s['grades'][2])/2 if sys is not None and s['grades'][2] is not None else None; c2=(sys+s['grades'][3])/2 if sys is not None and s['grades'][3] is not None else None
    return {'Promedio sistemático':sys,'Corte 1':c1,'Corte 2':c2,'Final / 40':2*(c1+c2) if c1 is not None and c2 is not None else None}
def f(v): return '—' if v is None else f'{v:.2f}'
def next_id(items): return max([x.get('id',0) for x in items] or [0])+1
def students_df(rows):
    out=[]
    for s in rows:
        m=metrics(s); out.append({'Código':s['code'],'Estudiante':s['name'],'Grupo':s['group'],'Sistemática':f(m['Promedio sistemático']),'Parcial 1':s['grades'][2] if s['grades'][2] is not None else '—','Parcial 2':s['grades'][3] if s['grades'][3] is not None else '—','Corte 1':f(m['Corte 1']),'Corte 2':f(m['Corte 2']),'Final / 40':f(m['Final / 40']) if s['published'] else 'No publicada','Asistencia %':s['attendance'],'Publicada':'Sí' if s['published'] else 'No'})
    return pd.DataFrame(out)

with st.sidebar:
    st.markdown('# 🎓 AulaControl')
    st.caption('GESTIÓN ACADÉMICA · ESPACIO DOCENTE')
    st.divider()
    pages={'GENERAL':['Resumen','Libro de notas','Asistencia'],'DOCENCIA':['Cursos y grupos','Clases y temas','Bibliografía','Tareas'],'SEGUIMIENTO':['Analítica','Informes','Configuración']}
    if st.session_state.auth_user['role'] == 'admin': pages['ADMINISTRACIÓN']=['Usuarios y roles']
    if st.session_state.auth_user['role'] == 'estudiante': pages={'MI ESPACIO':['Mi espacio']}
    for section,items in pages.items():
        st.caption(section)
        for p in items:
            label=f'⚠️ {p}' if p=='Asistencia' and sum(s['attendance']<50 for s in db['students']) else p
            if st.button(label, key='nav_'+p, use_container_width=True, type='primary' if st.session_state.active==p else 'secondary'):
                st.session_state.active=p; st.rerun()
    st.divider()
    st.write('**'+st.session_state.auth_user['display_name']+'**')
    st.caption(ROLES[st.session_state.auth_user['role']])
    if st.button('Cerrar sesión', use_container_width=True):
        st.session_state.auth_user = None
        st.rerun()
    st.caption('Versión MVP · datos de demostración')

active=st.session_state.active
role=st.session_state.auth_user['role']
if role == 'estudiante': active='Mi espacio'; st.session_state.active='Mi espacio'
st.markdown(f"<div style='padding:4px 0 0;color:#64748b;font-size:0.9rem'>ESPACIO DOCENTE　/　{active.upper()}</div>",unsafe_allow_html=True)
st.title(('Mi espacio académico' if role=='estudiante' else ('Buenos días, '+st.session_state.auth_user['display_name'] if active=='Resumen' else active)))
st.caption('Consulta tu información académica.' if role=='estudiante' else 'Administra y consulta la información de tu actividad académica.')
if role != 'estudiante':
    col1,col2,col3=st.columns([2,2,3])
    with col1: st.session_state.subject=st.selectbox('Asignatura activa',['Programación Web','Introducción a la Informática','Bases de Datos'],index=['Programación Web','Introducción a la Informática','Bases de Datos'].index(st.session_state.subject))
    with col2: st.session_state.term=st.selectbox('Período académico',['2026 · Semestre 1','2026 · Semestre 2','2027 · Semestre 1'],index=['2026 · Semestre 1','2026 · Semestre 2','2027 · Semestre 1'].index(st.session_state.term))
    with col3: st.write(''); st.write(''); st.caption('MVP: para persistencia y concurrencia multiusuario se necesita base de datos compartida.')
st.divider()
students=db['students']; at_risk=[s for s in students if s['attendance']<50]; course_avg=avg([metrics(s)['Promedio sistemático'] for s in students]); published=sum(s['published'] for s in students)

if role == 'estudiante':
    account_code = st.session_state.auth_user.get('student_code')
    mine = [x for x in students if account_code and x['code'].casefold() == account_code.casefold()]
    if not account_code:
        st.warning('Tu cuenta todavía no está vinculada a un código de matrícula. Contacta con el administrador.')
    elif not mine:
        st.info('No se encontraron datos académicos asociados a tu cuenta. Contacta con el profesor o administrador.')
    else:
        me = mine[0]
        m = metrics(me)
        a,b,c = st.columns(3)
        a.metric('Asistencia', f"{me['attendance']}%")
        b.metric('Promedio sistemático', f(m['Promedio sistemático'])+'/10' if m['Promedio sistemático'] is not None else '—')
        c.metric('Estado de notas', 'Publicadas' if me['published'] else 'Pendientes de publicación')
        st.subheader('Mis notas')
        if me['published']:
            grade_rows = [{'Evaluación':'Sistemática 1','Nota':me['grades'][0] if me['grades'][0] is not None else 'Pendiente'}, {'Evaluación':'Sistemática 2','Nota':me['grades'][1] if me['grades'][1] is not None else 'Pendiente'}, {'Evaluación':'Parcial 1','Nota':me['grades'][2] if me['grades'][2] is not None else 'Pendiente'}, {'Evaluación':'Parcial 2','Nota':me['grades'][3] if me['grades'][3] is not None else 'Pendiente'}, {'Evaluación':'Corte 1','Nota':f(m['Corte 1'])}, {'Evaluación':'Corte 2','Nota':f(m['Corte 2'])}, {'Evaluación':'Final / 40','Nota':f(m['Final / 40'])}]
            st.dataframe(pd.DataFrame(grade_rows), use_container_width=True, hide_index=True)
        else:
            st.info('El profesor todavía no ha publicado tus notas.')
        st.caption('Solo puedes consultar tu propia información. No puedes modificar notas, asistencia ni contenidos.')
    st.subheader('Próximas clases')
    st.dataframe(pd.DataFrame(sorted(db['sessions'], key=lambda x:x['date'])), use_container_width=True, hide_index=True)
    st.subheader('Tareas')
    st.dataframe(pd.DataFrame(db['tasks']), use_container_width=True, hide_index=True)
    st.subheader('Bibliografía')
    for resource in db['resources']:
        st.markdown(f"**{resource['title']}** · {resource.get('author','')}  \n[{resource['url']}]({resource['url']})")
    st.stop()

if active=='Resumen':
    st.markdown('## Tu aula, organizada. Tu progreso, visible.')
    st.write('Gestiona evaluaciones, asistencia y contenidos desde un solo lugar.')
    a,b,c,d=st.columns(4); a.metric('Estudiantes',len(students)); b.metric('Promedio del grupo',f(course_avg)+'/10' if course_avg is not None else '—'); c.metric('Publicaciones',f'{published}/{len(students)}'); d.metric('Alertas de asistencia',len(at_risk))
    st.subheader('Próximas actividades')
    upcoming=sorted(db['sessions'],key=lambda x:x['date'])
    if upcoming: st.dataframe(pd.DataFrame(upcoming),use_container_width=True,hide_index=True)
    else: st.info('No hay actividades planificadas.')
    left,right=st.columns(2)
    with left:
        st.subheader('Accesos rápidos')
        for p in ['Libro de notas','Asistencia','Clases y temas','Tareas','Analítica']:
            if st.button('Abrir '+p,key='quick_'+p,use_container_width=True): st.session_state.active=p; st.rerun()
    with right:
        st.subheader('Distribución de notas sistemáticas')
        vals=[metrics(s)['Promedio sistemático'] for s in students if metrics(s)['Promedio sistemático'] is not None]
        if vals: st.bar_chart(pd.Series(vals,name='Promedio sistemático').value_counts().sort_index())

elif active=='Libro de notas':
    st.write('Edita las sistemáticas y parciales. Los cortes y la nota final se calculan automáticamente.')
    query=st.text_input('Buscar por estudiante, código o grupo')
    rows=[s for s in students if query.lower() in f"{s['name']} {s['code']} {s['group']}".lower()]
    for s in rows:
        m=metrics(s)
        with st.expander(f"{s['name']} · {s['code']} · Grupo {s['group']}",expanded=True):
            x1,x2,x3,x4=st.columns(4)
            labels=['Sistemática 1','Sistemática 2','Parcial 1','Parcial 2']
            for i,(col,label) in enumerate(zip([x1,x2,x3,x4],labels)):
                with col:
                    value=st.number_input(label,0.0,10.0,step=0.5,value=float(s['grades'][i] or 0),key=f"grade_{s['id']}_{i}")
                    s['grades'][i]=value
            m=metrics(s); a,b,c,d=st.columns(4)
            a.metric('Promedio S',f(m['Promedio sistemático'])+'/10'); b.metric('Corte 1',f(m['Corte 1'])); c.metric('Corte 2',f(m['Corte 2'])); d.metric('Final / 40',f(m['Final / 40']) if s['published'] else 'Oculta')
            s['published']=st.checkbox('Marcar resultado como publicado (solo estado de demostración)',value=s['published'],key=f"pub_{s['id']}")
    with st.expander('➕ Añadir estudiante'):
        with st.form('add_student'):
            name=st.text_input('Nombre completo'); code=st.text_input('Código'); group=st.text_input('Grupo','2A'); ok=st.form_submit_button('Guardar estudiante')
        if ok:
            if name.strip() and code.strip(): db['students'].append({'id':next_id(db['students']),'name':name.strip(),'code':code.strip(),'group':group or '2A','attendance':100,'grades':[None,None,None,None],'published':False}); st.success('Estudiante añadido.'); st.rerun()
            else: st.error('Nombre y código son obligatorios.')
    st.download_button('⬇️ Exportar libro de notas CSV',students_df(students).to_csv(index=False).encode('utf-8-sig'),'aulacontrol-libro-notas.csv','text/csv')

elif active=='Asistencia':
    st.write('Control de asistencia y planificación de clases. Las alertas se activan por debajo del 50%.')
    st.metric('Estudiantes bajo el 50%',len(at_risk))
    for s in students:
        with st.container(border=True):
            c1,c2,c3=st.columns([3,2,2]); c1.write(f"**{s['name']}** · {s['code']}");
            with c2: s['attendance']=st.slider('Asistencia %',0,100,int(s['attendance']),key=f"att_{s['id']}")
            with c3: st.write('⚠️ Seguimiento' if s['attendance']<50 else '✅ En rango')
    st.subheader('Clases y actividades')
    if db['sessions']: st.dataframe(pd.DataFrame(db['sessions']),use_container_width=True,hide_index=True)
    with st.expander('➕ Nueva clase o actividad'):
        with st.form('new_session'):
            topic=st.text_input('Tema / actividad'); dt=st.date_input('Fecha',value=date.today()); typ=st.selectbox('Tipo',['Clase','Práctica','Seminario','Evaluación']); ok=st.form_submit_button('Guardar actividad')
        if ok and topic.strip(): db['sessions'].append({'id':next_id(db['sessions']),'date':str(dt),'topic':topic.strip(),'type':typ,'status':'Planificada'}); st.success('Actividad añadida.'); st.rerun()

elif active=='Cursos y grupos':
    st.subheader('Configuración del curso')
    st.write(f"**Asignatura:** {st.session_state.subject}　|　**Período:** {st.session_state.term}")
    groups=sorted(set(s['group'] for s in students)); st.metric('Grupos registrados',len(groups)); st.metric('Estudiantes matriculados',len(students))
    for g in groups:
        with st.expander(f'Grupo {g} · {sum(s["group"]==g for s in students)} estudiantes'):
            st.dataframe(students_df([s for s in students if s['group']==g]),use_container_width=True,hide_index=True)
    with st.expander('Añadir estudiante al curso'):
        with st.form('course_student'):
            n=st.text_input('Nombre'); code=st.text_input('Código de matrícula'); group=st.text_input('Grupo','2A'); ok=st.form_submit_button('Añadir')
        if ok and n.strip() and code.strip(): db['students'].append({'id':next_id(students),'name':n.strip(),'code':code.strip(),'group':group,'attendance':100,'grades':[None,None,None,None],'published':False}); st.rerun()

elif active=='Clases y temas':
    st.write('Planifica contenidos, unidades temáticas y apuntes.')
    with st.expander('➕ Añadir tema o clase',expanded=not db['lessons']):
        with st.form('new_lesson'):
            title=st.text_input('Título del tema'); unit=st.text_input('Unidad temática','Unidad 1'); dt=st.date_input('Fecha',value=date.today()); notes=st.text_area('Apuntes de la clase'); ok=st.form_submit_button('Guardar tema')
        if ok and title.strip(): db['lessons'].append({'id':next_id(db['lessons']),'title':title.strip(),'unit':unit,'date':str(dt),'notes':notes}); st.success('Tema guardado.'); st.rerun()
    for lesson in db['lessons']:
        with st.expander(f"{lesson['title']} · {lesson['date']}"):
            st.caption(lesson.get('unit','')); st.write(lesson.get('notes','') or 'Sin apuntes.');
            if st.button('Eliminar tema',key=f"del_lesson_{lesson['id']}"): db['lessons']=[x for x in db['lessons'] if x['id']!=lesson['id']]; st.rerun()

elif active=='Bibliografía':
    st.write('Recursos de apoyo para la asignatura.')
    for r in db['resources']:
        st.markdown(f"**{r['title']}** · {r.get('author','')}  \n[{r['url']}]({r['url']})")
    with st.expander('➕ Añadir recurso'):
        with st.form('new_resource'):
            title=st.text_input('Título'); author=st.text_input('Autor o institución'); url=st.text_input('URL'); ok=st.form_submit_button('Guardar recurso')
        if ok and title.strip() and url.startswith(('http://','https://')): db['resources'].append({'title':title.strip(),'author':author,'url':url}); st.success('Recurso añadido.'); st.rerun()
        elif ok: st.error('Indica un título y una URL válida que empiece por http:// o https://.')

elif active=='Tareas':
    st.write('Gestiona actividades y fechas límite.')
    with st.expander('➕ Nueva tarea'):
        with st.form('new_task'):
            title=st.text_input('Título de la tarea'); due=st.date_input('Fecha límite',value=date.today()+timedelta(days=7)); ok=st.form_submit_button('Crear tarea')
        if ok and title.strip(): db['tasks'].append({'id':next_id(db['tasks']),'title':title.strip(),'due':str(due),'status':'Abierta'}); st.success('Tarea creada.'); st.rerun()
    for t in db['tasks']:
        with st.container(border=True):
            c1,c2,c3=st.columns([4,2,2]); c1.write(f"**{t['title']}**"); c2.write(f"Fecha límite: {t.get('due','—')}");
            with c3:
                if st.button('Cerrar' if t['status']=='Abierta' else 'Reabrir',key=f"toggle_task_{t['id']}"): t['status']='Cerrada' if t['status']=='Abierta' else 'Abierta'; st.rerun()
                if st.button('Eliminar',key=f"del_task_{t['id']}"): db['tasks']=[x for x in db['tasks'] if x['id']!=t['id']]; st.rerun()
            st.caption('Estado: '+t['status'])

elif active=='Analítica':
    vals=[metrics(s)['Promedio sistemático'] for s in students if metrics(s)['Promedio sistemático'] is not None]
    a,b,c,d=st.columns(4); a.metric('Promedio del grupo',f(avg(vals))); b.metric('Mejor sistemática',f(max(vals) if vals else None)); c.metric('Alertas de asistencia',len(at_risk)); d.metric('Estudiantes con notas',len(vals))
    st.subheader('Distribución del promedio sistemático')
    if vals: st.bar_chart(pd.Series(vals,name='Promedio').value_counts().sort_index())
    st.subheader('Seguimiento de asistencia')
    st.dataframe(pd.DataFrame([{'Estudiante':s['name'],'Asistencia %':s['attendance'],'Promedio S':f(metrics(s)['Promedio sistemático']),'Seguimiento':'Revisar causas' if s['attendance']<50 else 'Sin alerta'} for s in students]),use_container_width=True,hide_index=True)

elif active=='Informes':
    st.subheader('Exportaciones')
    st.download_button('⬇️ Descargar libro de notas CSV',students_df(students).to_csv(index=False).encode('utf-8-sig'),'aulacontrol-libro-notas.csv','text/csv')
    backup={'version':1,'subject':st.session_state.subject,'term':st.session_state.term,**db}
    st.download_button('⬇️ Descargar respaldo JSON',json.dumps(backup,ensure_ascii=False,indent=2).encode('utf-8'),'aulacontrol-respaldo.json','application/json')
    uploaded=st.file_uploader('Restaurar respaldo AulaControl (JSON)',type=['json'])
    if uploaded:
        if st.button('Importar y reemplazar datos'):
            try:
                data=json.load(uploaded)
                if not isinstance(data.get('students'),list): raise ValueError('No contiene una lista de estudiantes.')
                for k in ['students','sessions','lessons','tasks','resources']:
                    if isinstance(data.get(k),list): db[k]=data[k]
                st.success('Respaldo importado.'); st.rerun()
            except Exception as e: st.error(f'No se pudo importar: {e}')
    st.subheader('Resumen del informe'); a,b,c,d=st.columns(4); a.metric('Estudiantes',len(students)); b.metric('Notas capturadas',sum(sum(g is not None for g in s['grades']) for s in students)); c.metric('Publicaciones',published); d.metric('Alertas',len(at_risk))
    st.warning('El respaldo puede contener información académica. Esta versión no cifra el JSON.')

elif active=='Usuarios y roles' and role == 'admin':
    st.subheader('Cuentas y permisos')
    st.write('El administrador puede crear, activar o desactivar cuentas y asignar roles. Los profesores no pueden administrar usuarios.')
    con = auth_connect()
    with st.expander('➕ Crear cuenta', expanded=True):
        with st.form('create_user_form', clear_on_submit=True):
            uname = st.text_input('Nombre de usuario (sin espacios)').strip().lower()
            display = st.text_input('Nombre completo')
            new_role = st.selectbox('Rol', ['profesor','estudiante'], format_func=lambda x: ROLES[x])
            student_options = [x['code'] for x in db['students']]
            student_code = st.selectbox('Código de matrícula (solo estudiante)', ['']+student_options, disabled=(new_role!='estudiante'))
            pwd = st.text_input('Contraseña inicial (mínimo 12 caracteres)', type='password')
            pwd2 = st.text_input('Repetir contraseña', type='password')
            create = st.form_submit_button('Crear cuenta')
        if create:
            if not uname or any(ch.isspace() for ch in uname) or not display.strip(): st.error('Usuario válido y nombre completo son obligatorios.')
            elif len(pwd)<12: st.error('La contraseña debe tener al menos 12 caracteres.')
            elif pwd != pwd2: st.error('Las contraseñas no coinciden.')
            elif new_role=='estudiante' and not student_code: st.error('Vincula la cuenta con un código de matrícula.')
            else:
                salt, hashed = password_hash(pwd)
                try:
                    con.execute('INSERT INTO users(username,display_name,role,student_code,salt,password_hash) VALUES(?,?,?,?,?,?)', (uname,display.strip(),new_role,student_code or None,salt,hashed))
                    con.commit(); st.success('Cuenta creada. Entrega la contraseña inicial de forma segura y recomienda cambiarla en el primer acceso.'); st.rerun()
                except sqlite3.IntegrityError: st.error('Ese nombre de usuario ya existe.')
    users = con.execute('SELECT id,username,display_name,role,student_code,active,created_at FROM users ORDER BY id').fetchall()
    con.close()
    st.dataframe(pd.DataFrame([{'Usuario':u['username'],'Nombre':u['display_name'],'Rol':ROLES[u['role']],'Matrícula':u['student_code'] or '—','Estado':'Activo' if u['active'] else 'Desactivado','Creado':u['created_at']} for u in users]), use_container_width=True, hide_index=True)
    st.subheader('Activar o desactivar cuenta')
    choices = {f"{u['username']} · {ROLES[u['role']]}  · {'Activo' if u['active'] else 'Desactivado'}":u for u in users if u['username'] != st.session_state.auth_user['username']}
    if choices:
        selected_label = st.selectbox('Cuenta', list(choices.keys()))
        selected_user = choices[selected_label]
        desired = st.selectbox('Estado nuevo', ['Activo','Desactivado'], index=0 if not selected_user['active'] else 1)
        if st.button('Aplicar estado'):
            con=auth_connect(); con.execute('UPDATE users SET active=? WHERE id=?', (1 if desired=='Activo' else 0, selected_user['id'])); con.commit(); con.close(); st.success('Estado actualizado.'); st.rerun()
    st.warning('La base SQLite de cuentas debe almacenarse en un volumen persistente. Streamlit Community Cloud no garantiza persistencia de archivos locales entre reinicios; para uso real, migra usuarios y datos académicos a PostgreSQL gestionado.')

elif active=='Configuración':
    st.subheader('Preferencias de la aplicación')
    st.toggle('Preferir tema oscuro (visualización)',key='dark')
    st.write('**Asignatura activa:**',st.session_state.subject); st.write('**Período:**',st.session_state.term)
    st.subheader('Reglas académicas')
    a,b,c=st.columns(3); a.metric('Sistemática','Promedio simple'); b.metric('Cortes','(S + Pᵢ) / 2'); c.metric('Final','2 × (C₁ + C₂) · /40')
    st.info('La autenticación y los roles están habilitados en esta versión MVP. Los datos académicos siguen siendo demostrativos y viven en la sesión. Antes de usar información real, configura almacenamiento persistente compartido, recuperación de contraseña, auditoría de cambios y políticas institucionales de protección de datos.')

st.divider()
st.caption('© 2026 AulaControl · Acceso por roles habilitado. MVP: validar seguridad y persistencia antes de producción.')
