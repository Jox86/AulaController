import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.grade_calculator import calculate_record

st.set_page_config(page_title="AulaControl · Analítica", page_icon="🎓", layout="wide")
st.title("🎓 AulaControl · Panel de cálculo")
st.caption("Panel complementario de demostración. No es el portal principal de estudiantes ni almacena registros multiusuario.")
st.info("Las notas se calculan según las fórmulas configuradas. Este panel no publica notas a estudiantes.")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Evaluaciones sistemáticas")
    systematics = st.text_input("Notas separadas por comas", "8, 8")
    try:
        sys_grades = [float(x.strip()) for x in systematics.split(",") if x.strip()]
    except ValueError:
        st.error("Escribe números separados por comas.")
        sys_grades = []
with c2:
    st.subheader("Parciales")
    p1 = st.number_input("Parcial 1 (0–10)", min_value=0.0, max_value=10.0, value=7.0, step=0.5)
    p2 = st.number_input("Parcial 2 (0–10)", min_value=0.0, max_value=10.0, value=9.0, step=0.5)
if st.button("Calcular resultados", type="primary"):
    try:
        result = calculate_record(sys_grades, p1, p2)
        a, b, c, d = st.columns(4)
        a.metric("Promedio S", "—" if result["systematic_average"] is None else f'{result["systematic_average"]:.2f}/10')
        b.metric("Corte 1", "Pendiente" if result["cut1"] is None else f'{result["cut1"]:.2f}/10')
        c.metric("Corte 2", "Pendiente" if result["cut2"] is None else f'{result["cut2"]:.2f}/10')
        d.metric("Final", "Pendiente" if result["final_40"] is None else f'{result["final_40"]:.2f}/40')
        st.json(result)
    except ValueError as exc:
        st.error(str(exc))
