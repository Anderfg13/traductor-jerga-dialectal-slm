"""
tests/test_kappa.py

Verifica evaluation/kappa.py contra valores de referencia conocidos, para
no reportar un acuerdo entre evaluadores mal calculado en el paper.

    python -m pytest tests/test_kappa.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "evaluation"))

import pytest  # noqa: E402

from kappa import cohen_kappa_ponderado, fleiss_kappa  # noqa: E402


def test_fleiss_ejemplo_publicado():
    """Ejemplo de la literatura (Fleiss 1971, reproducido en Wikipedia):
    10 ítems, 14 evaluadores, 5 categorías -> kappa = 0.210."""
    tabla = [
        [0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1],
        [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7],
    ]
    assert fleiss_kappa(tabla) == pytest.approx(0.210, abs=0.001)


def test_fleiss_acuerdo_perfecto():
    tabla = [[3, 0, 0, 0, 0], [0, 0, 3, 0, 0], [0, 0, 0, 0, 3], [0, 3, 0, 0, 0]]
    assert fleiss_kappa(tabla) == pytest.approx(1.0)


def test_cohen_dos_categorias_coincide_con_kappa_clasico():
    """Con 2 categorías, el kappa ponderado es el kappa de Cohen normal.
    Tabla [[20,5],[10,15]] (50 ítems) -> kappa = 0.4."""
    a = [1] * 20 + [1] * 5 + [2] * 10 + [2] * 15
    b = [1] * 20 + [2] * 5 + [1] * 10 + [2] * 15
    assert cohen_kappa_ponderado(a, b, categorias=[1, 2]) == pytest.approx(0.4, abs=1e-9)


def test_cohen_acuerdo_perfecto_y_desacuerdo_total():
    a = [1, 2, 3, 4, 5, 1, 5]
    assert cohen_kappa_ponderado(a, a) == pytest.approx(1.0)
    assert cohen_kappa_ponderado([1, 1, 5, 5], [5, 5, 1, 1]) < 0


def test_cohen_ponderado_castiga_menos_un_desacuerdo_pequeno():
    base = [1, 2, 3, 4, 5, 3, 2, 4]
    cerca = [1, 2, 3, 4, 4, 3, 2, 4]  # un 5 -> 4
    lejos = [1, 2, 3, 4, 1, 3, 2, 4]  # un 5 -> 1
    assert cohen_kappa_ponderado(base, cerca) > cohen_kappa_ponderado(base, lejos)
