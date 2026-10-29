# AulaControl

Aplicación web de gestión académica. Este primer entregable es un **MVP funcional de demostración**:
- Frontend React + Vite + JavaScript (npm, sin TypeScript ni Bun).
- API Python + FastAPI con cálculos de notas y asistencia.
- Persistencia de demostración local en el navegador (localStorage).
- PWA básica con manifiesto y service worker.
- Docker Compose para frontend + API.
- Panel Streamlit opcional para probar cálculos.

> Importante: el MVP del navegador guarda datos en el dispositivo y no ofrece todavía autenticación multiusuario real, sincronización entre dispositivos, cifrado de copias de seguridad ni un despliegue público seguro. La API inicial usa datos en memoria. No introducir datos personales reales ni usar como libro oficial hasta completar la siguiente fase.

## Requisitos
- Node.js 20+ y npm
- Python 3.11+
- Docker Desktop (opcional)

## Ejecutar el frontend
```bash
cd frontend
npm install
npm run dev
```
Abrir la URL local que muestre Vite (normalmente http://localhost:5173).

## Ejecutar la API
En otra terminal:
```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Documentación interactiva de API: http://127.0.0.1:8000/docs

## Panel Streamlit opcional
```bash
cd streamlit_admin
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue con Docker
Desde la raíz del proyecto:
```bash
docker compose -f deployment/compose.yaml up --build
```
Frontend: http://localhost:8080 · API: http://localhost:8000/docs

## Criterios académicos configurados
- Notas sistemáticas y parciales: escala 0–10.
- Sistemática `S`: promedio simple de las evaluaciones sistemáticas válidas.
- Cortes: `C1=(S+P1)/2`, `C2=(S+P2)/2`.
- Final: `F=2*(C1+C2)`, escala 0–40.
- La nota final se calcula internamente, pero solo se muestra como publicada cuando el docente lo decide.
- Alerta de asistencia solo si el porcentaje es estrictamente menor al 50%.
- Ausencias justificadas no se confunden con injustificadas; la alerta no penaliza automáticamente la nota.

## Próximos hitos recomendados
1. Persistencia PostgreSQL + migraciones.
2. Autenticación, autorización por rol y aislamiento de datos por estudiante.
3. Sincronización offline con cola idempotente y resolución de conflictos.
4. Auditoría de cambios, publicación versionada de notas y copias cifradas con pruebas de restauración.
5. Pruebas automatizadas, accesibilidad y despliegue con HTTPS.
