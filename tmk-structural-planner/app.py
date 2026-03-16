import streamlit as st
from typing import Dict, List, Tuple

st.set_page_config(page_title="TMK Structural Planner", layout="wide")

Route = Tuple[int, int]

STAGE_ORDER = ["0", "A", "B", "C", "D", "E", "F", "G"]

STAGE_META = {
    "0": {
        "label": "Stage 0 · Foundation",
        "products": [4, 6, 8, 9, 10],
        "color": "#4b5563",
        "description": "Foundation products. Multiple routes can point to one product.",
    },
    "A": {
        "label": "Stage A · Identity",
        "products": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "color": "#9ca3af",
        "description": "Identity products. Pattern: 1 × n = n.",
    },
    "B": {
        "label": "Stage B · Scaling",
        "products": [20, 30, 40, 50, 60, 70, 80, 90, 100],
        "color": "#1d4ed8",
        "description": "Scaling products. Pattern: 10 × n.",
    },
    "C": {
        "label": "Stage C · Midpoints",
        "products": [15, 25, 35, 45],
        "color": "#38bdf8",
        "description": "Midpoint products.",
    },
    "D": {
        "label": "Stage D · Nines",
        "products": [18, 27, 36, 54, 63, 72, 81],
        "color": "#38bdf8",
        "description": "Nine-family products.",
    },
    "E": {
        "label": "Stage E · Doubling Chain",
        "products": [12, 14, 16, 24, 28, 32, 48, 56, 64],
        "color": "#14b8a6",
        "description": "Doubling chain products: 2 × n → 4 × n → 8 × n.",
    },
    "F": {
        "label": "Stage F · Interleaving",
        "products": [21, 42],
        "color": "#7c3aed",
        "description": "Interleaving products. Compression onto existing hubs.",
    },
    "G": {
        "label": "Stage G · Closure",
        "products": [49],
        "color": "#d4a017",
        "description": "Closure product: 49.",
    },
}

INTRO_ROUTES: Dict[int, Route] = {
    1: (1, 1),
    2: (1, 2),
    3: (1, 3),
    4: (1, 4),
    5: (1, 5),
    6: (1, 6),
    7: (1, 7),
    8: (1, 8),
    9: (1, 9),
    10: (1, 10),
    12: (2, 6),
    14: (2, 7),
    15: (3, 5),
    16: (2, 8),
    18: (2, 9),
    20: (2, 10),
    21: (3, 7),
    24: (4, 6),
    25: (5, 5),
    27: (3, 9),
    28: (4, 7),
    30: (3, 10),
    32: (4, 8),
    35: (5, 7),
    36: (4, 9),
    40: (4, 10),
    42: (6, 7),
    45: (5, 9),
    48: (6, 8),
    49: (7, 7),
    50: (5, 10),
    54: (6, 9),
    56: (7, 8),
    60: (6, 10),
    63: (7, 9),
    64: (8, 8),
    70: (7, 10),
    72: (8, 9),
    80: (8, 10),
    81: (9, 9),
    90: (9, 10),
    100: (10, 10),
}

PRODUCT_STAGE = {}
for stage_key, stage_info in STAGE_META.items():
    for product in stage_info["products"]:
        if product not in PRODUCT_STAGE:
            PRODUCT_STAGE[product] = stage_key


def stage_rank(stage_key: str) -> int:
    return STAGE_ORDER.index(stage_key)


def full_routes_for_product(product: int) -> List[Route]:
    routes = []
    for a in range(1, 11):
        for b in range(1, 11):
            if a * b == product:
                routes.append((a, b))
    return routes


def exits_for_product(product: int) -> List[Route]:
    exits = []
    for divisor in range(1, 11):
        if product % divisor == 0:
            quotient = product // divisor
            if 1 <= quotient <= 10:
                exits.append((divisor, quotient))
    return exits


def visible_products(selected_stage: str) -> List[int]:
    visible = set()
    for stage_key in STAGE_ORDER:
        if stage_rank(stage_key) <= stage_rank(selected_stage):
            visible.update(STAGE_META[stage_key]["products"])
    return sorted(visible)


def new_products_for_stage(selected_stage: str) -> List[int]:
    return STAGE_META[selected_stage]["products"]


def route_text(route: Route) -> str:
    return f"{route[0]} × {route[1]}"


def exit_text(product: int, route: Route) -> str:
    return f"{product} ÷ {route[0]} = {route[1]}"


def intro_text(product: int) -> str:
    route = INTRO_ROUTES[product]
    return f"{route[0]} × {route[1]} = {product}"


st.markdown(
    """
    <style>
    .title-main {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle-main {
        color: #5b6470;
        margin-bottom: 1rem;
    }
    .card {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
    .hub {
        width: 130px;
        height: 130px;
        border-radius: 999px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 2.6rem;
        font-weight: 800;
    }
    .hub-label {
        text-align: center;
        margin-top: 0.6rem;
        color: #5b6470;
        font-weight: 700;
    }
    .pill {
        display: inline-block;
        padding: 0.4rem 0.7rem;
        border-radius: 999px;
        border: 1px solid #dbe3ef;
        margin: 0.15rem 0.2rem 0.15rem 0;
        background: #f8fafc;
    }
    .intro {
        background: #ecfeff;
        font-weight: 700;
    }
    .entry {
        background: #eef6ff;
    }
    .exit {
        background: #f5f3ff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "selected_stage" not in st.session_state:
    st.session_state.selected_stage = "A"

if "selected_product" not in st.session_state:
    st.session_state.selected_product = 4

with st.sidebar:
    st.header("Stage Controls")

    st.session_state.selected_stage = st.radio(
        "Unlock up to stage",
        options=STAGE_ORDER,
        index=STAGE_ORDER.index(st.session_state.selected_stage),
        format_func=lambda s: STAGE_META[s]["label"],
    )

    st.markdown("---")
    st.subheader("Boundary")
    st.write("Only products inside the P10 boundary appear.")
    st.write("Both factors must be 10 or less.")

current_stage = st.session_state.selected_stage
current_visible = visible_products(current_stage)

if st.session_state.selected_product not in current_visible:
    st.session_state.selected_product = current_visible[0]

st.markdown('<div class="title-main">TMK Structural Planner</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-main">A product world where products appear only when their stage unlocks.</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader(STAGE_META[current_stage]["label"])
st.write(STAGE_META[current_stage]["description"])
st.write(f"New products in this stage: {', '.join(str(p) for p in new_products_for_stage(current_stage))}")
st.write(f"Visible products so far: {', '.join(str(p) for p in current_visible)}")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Product Selector")

cols = st.columns(8)
for i, product in enumerate(current_visible):
    with cols[i % 8]:
        if st.button(str(product), key=f"product_{product}"):
            st.session_state.selected_product = product
st.markdown("</div>", unsafe_allow_html=True)

product = st.session_state.selected_product
product_stage = PRODUCT_STAGE[product]
product_color = STAGE_META[product_stage]["color"]

left, right = st.columns([1, 1.2])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Product Detail View")

    st.markdown(
        f"""
        <div class="hub" style="background:{product_color};">{product}</div>
        <div class="hub-label">{STAGE_META[product_stage]['label']}</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Introduction Route**")
    st.markdown(f'<span class="pill intro">{intro_text(product)}</span>', unsafe_allow_html=True)

    st.markdown("**Full Route Field**")
    full_routes_html = ""
    for route in full_routes_for_product(product):
        full_routes_html += f'<span class="pill entry">{route_text(route)} = {product}</span>'
    st.markdown(full_routes_html, unsafe_allow_html=True)

    st.markdown("**Exits**")
    exits_html = ""
    for route in exits_for_product(product):
        exits_html += f'<span class="pill exit">{exit_text(product, route)}</span>'
    st.markdown(exits_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Hub-and-Spoke Product View")

    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        st.markdown("**Entry routes → product**")
        for route in full_routes_for_product(product):
            st.write(f"{route_text(route)} = {product}")

    with c2:
        st.markdown(
            f"""
            <div class="hub" style="background:{product_color}; width:110px; height:110px; font-size:2.2rem;">{product}</div>
            <div class="hub-label">Product Hub</div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown("**Product → exit routes**")
        for route in exits_for_product(product):
            st.write(exit_text(product, route))

    st.markdown("</div>", unsafe_allow_html=True)
