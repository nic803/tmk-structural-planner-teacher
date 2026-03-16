import streamlit as st
from typing import Dict, List, Tuple

st.set_page_config(page_title="TMK Structural Planner", page_icon="✳️", layout="wide")

Route = Tuple[int, int]

STAGE_ORDER = ["0", "A", "B", "C", "D", "E", "F", "G"]

STAGE_META = {
    "0": {"label": "Stage 0 · Foundation", "products": [4, 6, 8, 9, 10], "color": "#4b5563"},
    "A": {"label": "Stage A · Identity", "products": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "color": "#9ca3af"},
    "B": {"label": "Stage B · Scaling", "products": [20, 30, 40, 50, 60, 70, 80, 90, 100], "color": "#1d4ed8"},
    "C": {"label": "Stage C · Midpoints", "products": [15, 25, 35, 45], "color": "#38bdf8"},
    "D": {"label": "Stage D · Nines", "products": [18, 27, 36, 54, 63, 72, 81], "color": "#38bdf8"},
    "E": {"label": "Stage E · Doubling Chain", "products": [12, 14, 16, 24, 28, 32, 48, 56, 64], "color": "#14b8a6"},
    "F": {"label": "Stage F · Interleaving", "products": [21, 42], "color": "#7c3aed"},
    "G": {"label": "Stage G · Closure", "products": [49], "color": "#d4a017"},
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
    out = []
    for a in range(1, 11):
        for b in range(1, 11):
            if a * b == product:
                out.append((a, b))
    return out


def exits(product: int) -> List[Route]:
    out = []
    for d in range(1, 11):
        if product % d == 0:
            q = product // d
            if 1 <= q <= 10:
                out.append((d, q))
    return out


def route_text(route: Route) -> str:
    return f"{route[0]} × {route[1]}"


def exit_text(product: int, route: Route) -> str:
    return f"{product} ÷ {route[0]} = {route[1]}"


def intro_text(product: int) -> str:
    a, b = INTRO_ROUTES[product]
    return f"{a} × {b} = {product}"


def stage_products_for_view(selected_stage: str) -> Dict[str, List[int]]:
    out: Dict[str, List[int]] = {}
    for s in STAGE_ORDER:
        if stage_rank(s) <= stage_rank(selected_stage):
            out[s] = STAGE_META[s]["products"]
    return out


st.markdown(
    """
    <style>
    .world-card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
    .hub-card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1rem;
        background: white;
    }
    .hub-circle {
        width: 120px;
        height: 120px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        color: white;
        font-size: 2.4rem;
        font-weight: 800;
    }
    .hub-label {
        text-align: center;
        margin-top: 0.5rem;
        color: #5b6470;
        font-weight: 700;
    }
    .pill {
        display: inline-block;
        padding: 0.42rem 0.72rem;
        border-radius: 999px;
        border: 1px solid #dbe3ef;
        margin: 0.15rem 0.2rem 0.15rem 0;
        background: #f8fafc;
        font-size: 0.95rem;
    }
    .intro { background: #ecfeff; font-weight: 700; }
    .entry { background: #eef6ff; }
    .exit  { background: #f5f3ff; }
    .stage-row {
        margin-bottom: 0.8rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #eef2f7;
    }
    .stage-name {
        font-weight: 800;
        margin-bottom: 0.45rem;
    }
    div[data-testid="stButton"] > button {
        width: 100%;
        border-radius: 999px;
        min-height: 3rem;
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "stage" not in st.session_state:
    st.session_state.stage = "0"

if "product" not in st.session_state:
    st.session_state.product = 4

with st.sidebar:
    st.header("Teacher Controls")
    st.session_state.stage = st.radio(
        "Unlock stage",
        STAGE_ORDER,
        index=STAGE_ORDER.index(st.session_state.stage),
        format_func=lambda s: STAGE_META[s]["label"],
    )

stage = st.session_state.stage
products = visible_products(stage)

if st.session_state.product not in products:
    st.session_state.product = products[0]

st.title("TMK Structural Planner")
st.caption("Multiplication = entry routes • Division = exit routes")

st.markdown('<div class="world-card">', unsafe_allow_html=True)
st.subheader("Product World Map")
st.caption("All visible hubs are shown together. Click any hub.")

world = stage_products_for_view(stage)

for stage_key, row_products in world.items():
    color = STAGE_META[stage_key]["color"]
    label = STAGE_META[stage_key]["label"]

    st.markdown(
        f'<div class="stage-row"><div class="stage-name" style="color:{color};">{label}</div></div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(len(row_products))
    for i, p in enumerate(row_products):
        with cols[i]:
            button_label = f"● {p}" if p == st.session_state.product else str(p)
            if st.button(button_label, key=f"world_{stage_key}_{p}"):
                st.session_state.product = p
                st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

product = st.session_state.product
color = STAGE_META[PRODUCT_STAGE[product]]["color"]

left, right = st.columns([1, 1.2])

with left:
    st.markdown('<div class="hub-card">', unsafe_allow_html=True)
    st.subheader("Product Detail")

    st.markdown(
        f"""
        <div class="hub-circle" style="background:{color};">{product}</div>
        <div class="hub-label">{STAGE_META[PRODUCT_STAGE[product]]['label']}</div>
        """,
        unsafe_allow_html=True,
    )

    st.write("Introduction route")
    st.markdown(f'<span class="pill intro">{intro_text(product)}</span>', unsafe_allow_html=True)

    st.write("Full route field")
    route_html = ""
    for r in routes(product):
        route_html += f'<span class="pill entry">{route_text(r)} = {product}</span>'
    st.markdown(route_html, unsafe_allow_html=True)

    st.write("Exit routes")
    exit_html = ""
    for r in exits(product):
        exit_html += f'<span class="pill exit">{exit_text(product, r)}</span>'
    st.markdown(exit_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="hub-card">', unsafe_allow_html=True)
    st.subheader("Selected Product Structure")
    st.write("Entry routes to the product")
    for r in routes(product):
        st.write(f"{route_text(r)} = {product}")

    st.write("Exit routes from the product")
    for r in exits(product):
        st.write(exit_text(product, r))

    st.markdown("</div>", unsafe_allow_html=True)
