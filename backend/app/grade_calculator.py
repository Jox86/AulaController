"""Funciones puras para calcular las calificaciones de AulaControl."""
from statistics import mean
from typing import Iterable, Optional

def validate_grade(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    value = float(value)
    if not 0 <= value <= 10:
        raise ValueError("Las notas deben estar en la escala de 0 a 10.")
    return value

def systematic_average(grades: Iterable[Optional[float]]) -> Optional[float]:
    valid = [validate_grade(g) for g in grades if g is not None]
    return mean(valid) if valid else None

def calculate_cut(systematic: Optional[float], partial: Optional[float]) -> Optional[float]:
    if systematic is None or partial is None:
        return None
    return (validate_grade(systematic) + validate_grade(partial)) / 2

def calculate_final(cut1: Optional[float], cut2: Optional[float]) -> Optional[float]:
    if cut1 is None or cut2 is None:
        return None
    result = 2 * (cut1 + cut2)
    if not 0 <= result <= 40:
        raise ValueError("El resultado final debe estar entre 0 y 40.")
    return result

def calculate_record(systematic_grades: Iterable[Optional[float]], partial1: Optional[float], partial2: Optional[float]) -> dict:
    s = systematic_average(systematic_grades)
    c1 = calculate_cut(s, partial1)
    c2 = calculate_cut(s, partial2)
    return {"systematic_average": s, "cut1": c1, "cut2": c2, "final_40": calculate_final(c1, c2)}
