import streamlit as st
from typing import Dict, List, Tuple

st.set_page_config(page_title="TMK Structural Planner", page_icon="✳️", layout="wide")

Route = Tuple[int, int]

STAGE_ORDER = ["0", "A", "B", "C", "D", "E", "F", "G"]

STAGE_META = {
    "0": {
        "label": "Stage 0 · Foundation",
        "products": [4, 6, 8, 9, 10],
        "color": "#4b5563",
        "description": "Foundation. Multiple routes can point to one product.",
    },
    "A": {
        "label": "Stage A · Identity",
        "products": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "color": "#9ca3af",
        "description": "Identity. Pattern: 1 × n = n.",
    },
    "B": {
        "label": "Stage B · Scaling",
        "products": [20, 30, 40, 50, 60, 70, 80, 90, 100],
        "color": "#1d4ed8",
        "description": "Scaling. Pattern: 10 × n.",
    },
    "C": {
        "label": "Stage C · Midpoints",
        "products": [15, 25, 35, 45],
        "color": "#38bdf8",
        "description": "Midpoints. Products 15, 25, 35, 45.",
    },
    "D": {
        "label": "Stage D · Nines",
        "products": [18, 27, 36, 54, 63, 72, 81],
        "color": "#38bdf8",
        "description": "Nines. Products derived through the nine-family.",
    },
    "E": {
        "label": "Stage E · Doubling Chain",
        "products": [12, 14, 16, 24, 28, 32, 48, 56, 64],
        "color": "#14b8a6",
        "description": "Doubling chain. 2 × n → 4 × n → 8 × n.",
    },
    "F": {
        "label": "Stage F · Interleaving",
        "products": [21, 42],
        "color": "#7c3aed",
        "description": "Interleaving. Compression onto existing product hubs.",
    },
    "G": {
        "label": "Stage G · Closure",
        "products": [49],
        "color": "#d4a017",
        "description": "Closure. Product 49 completes the P10 product world.",
    },
}

INTRO_ROUTES: Dict[int, Route] = {
    1: (1, 1), 2: (1, 2), 3: (1, 3), 4: (1, 4), 5: (1, 5),
    6: (1, 6), 7: (1, 7), 8: (1, 8), 9: (1, 9), 10: (1, 10),
    12: (2, 6), 14: (2, 7), 15: (3, 5), 16: (2, 8), 18: (2, 9),
    20: (2, 10), 21: (3, 7), 24: (4, 6), 25: (5, 5), 27: (3, 9),
    28: (4, 7), 30: (3, 10), 32: (4, 8), 35: (5, 7), 36: (4, 9),
    40: (4, 10), 42: (6, 7), 45: (5, 9), 48: (6, 8), 49: (7, 7),
    50: (5, 10), 54: (6, 9), 56: (7, 8), 60: (6, 10), 63: (7, 9),
    64: (8, 8), 70: (7, 10), 72: (8, 9), 80: (8, 10), 81: (9, 9),
    90: (9, 10), 100: (10, 10),
}

PRODUCT_STAGE: Dict[int, str] = {}
for stage_key, meta in STAGE_META.items():
    for p in meta["products"]:
        if p not in PRODUCT_STAGE:
            PRODUCT_STAGE[p] = stage_key


def stage_rank(stage_key: str) -> int:
    return STAGE_ORDER.index(stage_key)


def visible_products(selected_stage: str) -> List[int]:
    visible = set()
    for s in STAGE_ORDER:
        if stage_rank(s) <= stage_rank(selected_stage):
            visible.update(STAGE_META[s]["products"])
    return sorted(visible)


def routes(product: int) -> List[Route]:
    out: List[Route]
