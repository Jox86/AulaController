# AulaControl: inicio de sesión y roles

## Roles implementados
- **Administrador (`admin`)**: acceso a todas las pantallas y a `Usuarios y roles`; puede crear cuentas de profesor/estudiante, vincular estudiante a matrícula y activar/desactivar cuentas.
- **Profesor (`profesor`)**: gestiona la actividad académica (notas, asistencia, cursos, clases, bibliografía, tareas, informes y configuración). No ve ni administra cuentas.
- **Estudiante (`estudiante`)**: acceso de solo lectura a su propio espacio; ve exclusivamente sus datos asociados al código de matrícula y solo ve las notas cuando el profesor las marca como publicadas. No puede modificar notas, asistencia ni contenidos.

## Primer administrador
No existe una contraseña predeterminada ni registro público. Antes de iniciar la aplicación, configura en Streamlit Community Cloud → **Settings → Secrets**:

```toml
BOOTSTRAP_ADMIN_USERNAME = "admin"
BOOTSTRAP_ADMIN_PASSWORD = "CAMBIA-ESTA-POR-UNA-CONTRASENA-LARGA-Y-UNICA"
```

La contraseña inicial debe tener al menos 12 caracteres. En local puedes definir las mismas variables de entorno antes de ejecutar Streamlit. No subas secretos al repositorio GitHub ni compartas el archivo `secrets.toml`.

Cuando se abra la aplicación por primera vez, inicia sesión con esas credenciales y crea las cuentas de profesores y estudiantes desde **Usuarios y roles**. Para cada estudiante, selecciona su código de matrícula exacto.

## Controles de seguridad incluidos
- Contraseñas almacenadas como hashes PBKDF2-HMAC-SHA256 con salt aleatorio (no texto plano).
- Consultas SQL parametrizadas.
- Sin alta pública de usuarios.
- Rechazo de cuentas desactivadas.
- Bloqueo temporal tras cinco intentos fallidos en una sesión.
- Separación de vistas por rol; el estudiante no recibe la tabla de otros estudiantes en su pantalla.

## Limitaciones que hay que resolver antes de producción
Esta es una implementación de seguridad para MVP, **no una certificación de seguridad**. La base de usuarios se guarda en `aulacontrol_auth.sqlite3`; en Streamlit Community Cloud los archivos locales no son almacenamiento persistente garantizado. El bloqueo de intentos es por sesión, no global por usuario/IP. La sesión de Streamlit no equivale a un sistema de identidad institucional con MFA, revocación inmediata en sesiones ya abiertas o registro de auditoría.

Además, los datos académicos actuales siguen guardándose en `st.session_state` y son datos de demostración; no constituyen una base de datos compartida. Antes de usar datos reales, migrar usuarios y datos académicos a PostgreSQL gestionado con copias de seguridad, añadir recuperación/cambio obligatorio de contraseña, auditoría de cambios, controles de sesión y pruebas de seguridad. No usar todavía como sistema oficial de publicación de notas.
