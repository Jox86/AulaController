# Estado y alcance del MVP

## Funciona en esta versión
- Navegación por secciones, modo claro/oscuro y diseño adaptable.
- Libro de notas editable para sistemáticas y parciales (0–10).
- Cálculo automático de promedio sistemático, cortes y nota final /40.
- Estado de publicación por estudiante y ocultación visual de final no publicada.
- Gestión local de estudiantes, clases, temas, recursos y tareas.
- Registro de asistencia de demostración y alerta bajo 50%.
- Exportación CSV, exportación/importación JSON, gráficos básicos.
- API FastAPI para cálculo de notas y resumen de asistencia.
- Panel Streamlit de cálculo y Docker Compose inicial.

## Limitaciones importantes
- Datos de muestra precargados. No se ha implementado autenticación real ni roles en el servidor.
- El almacenamiento de la app principal es localStorage: solo en el navegador/dispositivo actual; no es multiusuario ni cifrado.
- La asistencia en la UI es una demostración simplificada y ajusta un porcentaje manualmente. La versión oficial debe calcularla desde sesiones y marcas persistidas, diferenciando ausencias justificadas e injustificadas.
- El botón de publicación es una maqueta de estado local, no un sistema seguro de publicación por alumno/actividad.
- El service worker cachea el shell; no implementa todavía una cola de operaciones offline sincronizable.
- Los respaldos JSON no están cifrados.
- El PDF/acta oficial, importación masiva robusta, auditoría inmutable, PostgreSQL, migraciones, notificaciones y portal real del estudiante están pendientes.
- El manifiesto PWA es inicial; para instalar sin conexión real deben completarse pruebas y estrategia de actualización de caché.
- No se ha ejecutado una prueba de extremo a extremo en un navegador en este entorno.

## Fórmulas
- `S = promedio de las sistemáticas válidas`.
- `C1 = (S + P1) / 2`.
- `C2 = (S + P2) / 2`.
- `F = 2 * (C1 + C2)`, escala 0–40.
- Si faltan datos necesarios, el resultado queda pendiente (no se fuerza a cero).
