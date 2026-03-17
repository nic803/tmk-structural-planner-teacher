import math
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


def read_query_product() -> int | None:
    try:
        qp = st.query_params
        raw = qp.get("product")
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0]
        return int(raw)
    except Exception:
        return None


def write_query_product(product: int) -> None:
    try:
        st.query_params["product"] = str(product)
    except Exception:
        pass


def read_query_stage() -> str | None:
    try:
        qp = st.query_params
        raw = qp.get("stage")
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0]
        if raw in STAGE_ORDER:
            return raw
        return None
    except Exception:
        return None


def write_query_stage(stage: str) -> None:
    try:
        st.query_params["stage"] = stage
    except Exception:
        pass


def build_world_map_svg(products: List[int], selected_product: int, selected_stage: str) -> str:
    width = 1100
    height = 760
    stage_y = {
        "0": 90,
        "A": 170,
        "B": 270,
        "C": 360,
        "D": 440,
        "E": 540,
        "F": 640,
        "G": 720,
    }

    positions: Dict[int, Tuple[float, float]] = {}

    for stage_key in STAGE_ORDER:
        stage_products = [p for p in STAGE_META[stage_key]["products"] if p in products]
        if not stage_products:
            continue

        y = stage_y[stage_key]
        count = len(stage_products)

        if count == 1:
            xs = [width / 2]
        else:
            left = 180
            right = width - 70
            step = (right - left) / (count - 1)
            xs = [left + i * step for i in range(count)]

        for p, x in zip(stage_products, xs):
            positions[p] = (x, y)

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="760" xmlns="http://www.w3.org/2000/svg">',
        """
        <style>
        .stage-label { font: 700 15px Arial, sans-serif; }
        .hub-text { font: 800 20px Georgia, serif; fill: white; pointer-events: none; }
        .line { stroke: #cbd5e1; stroke-width: 3; opacity: 0.9; }
        .line-selected { stroke: #fb923c; stroke-width: 5; opacity: 1; }
        .hub-link:hover circle { filter: brightness(1.08); }
        .hub-link { cursor: pointer; }
        </style>
        """,
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>',
    ]

    present_stages = {PRODUCT_STAGE[p] for p in products}
    for stage_key in STAGE_ORDER:
        if stage_key not in present_stages:
            continue
        y = stage_y[stage_key]
        color = STAGE_META[stage_key]["color"]
        label = STAGE_META[stage_key]["label"]
        svg.append(f'<text x="20" y="{y+5}" class="stage-label" fill="{color}">{label}</text>')
        svg.append(f'<line x1="160" y1="{y}" x2="{width-20}" y2="{y}" stroke="#eef2f7" stroke-width="1"/>')

    for p in products:
        if p not in INTRO_ROUTES or p not in positions:
            continue
        a, b = INTRO_ROUTES[p]
        px, py = positions[p]

        for source in (a, b):
            if source in positions:
                sx, sy = positions[source]
                cls = "line-selected" if p == selected_product else "line"
                svg.append(
                    f'<line x1="{sx}" y1="{sy+24}" x2="{px}" y2="{py-24}" class="{cls}"/>'
                )

    for p in products:
        x, y = positions[p]
        stage_key = PRODUCT_STAGE[p]
        color = STAGE_META[stage_key]["color"]

        r = 28
        stroke = "white"
        stroke_width = 4

        if p == selected_product:
            r = 34
            stroke = "#fb923c"
            stroke_width = 6

        svg.append(
            f'''
            <a href="?product={p}&stage={selected_stage}" target="_self" class="hub-link">
                <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="{stroke}" stroke-width="{stroke_width}"/>
                <text x="{x}" y="{y+7}" text-anchor="middle" class="hub-text">{p}</text>
            </a>
            '''
        )

    svg.append("</svg>")
    return "".join(svg)


def build_radial_svg(product: int, product_routes: List[Route], product_exits: List[Route], color: str) -> str:
    width = 760
    height = 540
    cx = width // 2
    cy = 220
    radius = 165
    angles = [-155, -125, -95, -65, -35, -5, 25, 55]

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="540" xmlns="http://www.w3.org/2000/svg">',
        """
        <style>
        .entry-label { font: 700 15px Arial, sans-serif; fill: #1f2937; }
        .exit-label { font: 700 14px Arial, sans-serif; fill: #3f3f46; }
        .hub-text { font: 800 42px Georgia, serif; fill: white; }
        .entry-box { fill: #eef6ff; stroke: #bfdbfe; stroke-width: 2; rx: 12; ry: 12; }
        .exit-box { fill: #f5f3ff; stroke: #ddd6fe; stroke-width: 2; rx: 12; ry: 12; }
        .line-entry { stroke: #94a3b8; stroke-width: 3; }
        .line-exit { stroke: #a78bfa; stroke-width: 3; }
        </style>
        """,
    ]

    for i, route in enumerate(product_routes[:8]):
        angle = math.radians(angles[i])
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        lx = cx + 72 * math.cos(angle)
        ly = cy + 72 * math.sin(angle)

        svg.append(f'<line x1="{x}" y1="{y}" x2="{lx}" y2="{ly}" class="line-entry"/>')
        svg.append(f'<rect x="{x-56}" y="{y-18}" width="112" height="36" class="entry-box"/>')
        svg.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" class="entry-label">{route_text(route)}</text>')

    svg.append(f'<circle cx="{cx}" cy="{cy}" r="66" fill="{color}"/>')
    svg.append(f'<text x="{cx}" y="{cy+14}" text-anchor="middle" class="hub-text">{product}</text>')

    exit_y = 430
    spacing = 130
    total = max(1, len(product_exits) - 1) * spacing
    start_x = cx - total / 2

    for i, route in enumerate(product_exits):
        x = start_x + i * spacing
        svg.append(f'<line x1="{cx}" y1="{cy+66}" x2="{x}" y2="{exit_y-26}" class="line-exit"/>')
        svg.append(f'<rect x="{x-54}" y="{exit_y-18}" width="108" height="38" class="exit-box"/>')
        svg.append(f'<text x="{x}" y="{exit_y+6}" text-anchor="middle" class="exit-label">{product} ÷ {route[0]}</text>')

    svg.append("</svg>")
    return "".join(svg)


st.markdown(
    """
    <style>
    .card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
    .hub {
        width: 132px;
        height: 132px;
        border-radius: 999px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 2.7rem;
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
        padding: 0.42rem 0.72rem;
        border-radius: 999px;
        border: 1px solid #dbe3ef;
        margin: 0.15rem 0.2rem 0.15rem 0;
        background: #f8fafc;
        font-size: 0.95rem;
    }
    .intro { background: #ecfeff; font-weight: 700; }
    .entry { background: #eef6ff; }
    .exit { background: #f5f3ff; }
    div[data-testid="stButton"] > button {
        width: 100%;
        border-radius: 12px;
        min-height: 2.8rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "stage" not in st.session_state:
    query_stage = read_query_stage()
    st.session_state.stage = query_stage if query_stage else "0"

if "product" not in st.session_state:
    st.session_state.product = 4

with st.sidebar:
    st.header("Teacher Controls")
    stage_choice = st.radio(
        "Unlock stage",
        STAGE_ORDER,
        index=STAGE_ORDER.index(st.session_state.stage),
        format_func=lambda s: STAGE_META[s]["label"],
    )
    st.session_state.stage = stage_choice
    write_query_stage(stage_choice)

stage = st.session_state.stage
products = visible_products(stage)

query_product = read_query_product()
if query_product in products:
    st.session_state.product = query_product

if st.session_state.product not in products:
    st.session_state.product = products[0]

write_query_product(st.session_state.product)
write_query_stage(stage)

st.title("TMK Structural Planner")
st.caption("Multiplication = entry routes • Division = exit routes")

st.subheader("Product World Map")
st.caption("Click any hub in the network.")

world_svg = build_world_map_svg(products, st.session_state.product, stage)
st.components.v1.html(world_svg, height=780, scrolling=False)

st.subheader("Select Product")
cols = st.columns(8)
for i, p in enumerate(products):
    with cols[i % 8]:
        if st.button(str(p), key=f"product_{p}"):
            st.session_state.product = p
            write_query_product(p)
            write_query_stage(stage)

product = st.session_state.product
color = STAGE_META[PRODUCT_STAGE[product]]["color"]

left, right = st.columns([1, 1.2])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Product Detail")

    st.markdown(
        f"""
        <div class="hub" style="background:{color};">{product}</div>
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
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Selected Product Map")
    radial = build_radial_svg(product, routes(product), exits(product), color)
    st.components.v1.html(radial, height=560, scrolling=False)
    st.markdown("</div>", unsafe_allow_html=True)

This version fixes the current bug by keeping both product and stage in the query params, so clicking a hub no longer drops the app back to Stage 0.

Send the next fix you want and I’ll return the full code again.

code not text
import math
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


def read_query_product() -> int | None:
    try:
        qp = st.query_params
        raw = qp.get("product")
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0]
        return int(raw)
    except Exception:
        return None


def write_query_product(product: int) -> None:
    try:
        st.query_params["product"] = str(product)
    except Exception:
        pass


def read_query_stage() -> str | None:
    try:
        qp = st.query_params
        raw = qp.get("stage")
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0]
        if raw in STAGE_ORDER:
            return raw
        return None
    except Exception:
        return None


def write_query_stage(stage: str) -> None:
    try:
        st.query_params["stage"] = stage
    except Exception:
        pass


def build_world_map_svg(products: List[int], selected_product: int, selected_stage: str) -> str:
    width = 1100
    height = 760
    stage_y = {
        "0": 90,
        "A": 170,
        "B": 270,
        "C": 360,
        "D": 440,
        "E": 540,
        "F": 640,
        "G": 720,
    }

    positions: Dict[int, Tuple[float, float]] = {}

    for stage_key in STAGE_ORDER:
        stage_products = [p for p in STAGE_META[stage_key]["products"] if p in products]
        if not stage_products:
            continue

        y = stage_y[stage_key]
        count = len(stage_products)

        if count == 1:
            xs = [width / 2]
        else:
            left = 180
            right = width - 70
            step = (right - left) / (count - 1)
            xs = [left + i * step for i in range(count)]

        for p, x in zip(stage_products, xs):
            positions[p] = (x, y)

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="760" xmlns="http://www.w3.org/2000/svg">',
        """
        <style>
        .stage-label { font: 700 15px Arial, sans-serif; }
        .hub-text { font: 800 20px Georgia, serif; fill: white; pointer-events: none; }
        .line { stroke: #cbd5e1; stroke-width: 3; opacity: 0.9; }
        .line-selected { stroke: #fb923c; stroke-width: 5; opacity: 1; }
        .hub-link:hover circle { filter: brightness(1.08); }
        .hub-link { cursor: pointer; }
        </style>
        """,
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>',
    ]

    present_stages = {PRODUCT_STAGE[p] for p in products}
    for stage_key in STAGE_ORDER:
        if stage_key not in present_stages:
            continue
        y = stage_y[stage_key]
        color = STAGE_META[stage_key]["color"]
        label = STAGE_META[stage_key]["label"]
        svg.append(f'<text x="20" y="{y+5}" class="stage-label" fill="{color}">{label}</text>')
        svg.append(f'<line x1="160" y1="{y}" x2="{width-20}" y2="{y}" stroke="#eef2f7" stroke-width="1"/>')

    for p in products:
        if p not in INTRO_ROUTES or p not in positions:
            continue
        a, b = INTRO_ROUTES[p]
        px, py = positions[p]

        for source in (a, b):
            if source in positions:
                sx, sy = positions[source]
                cls = "line-selected" if p == selected_product else "line"
                svg.append(
                    f'<line x1="{sx}" y1="{sy+24}" x2="{px}" y2="{py-24}" class="{cls}"/>'
                )

    for p in products:
        x, y = positions[p]
        stage_key = PRODUCT_STAGE[p]
        color = STAGE_META[stage_key]["color"]

        r = 28
        stroke = "white"
        stroke_width = 4

        if p == selected_product:
            r = 34
            stroke = "#fb923c"
            stroke_width = 6

        svg.append(
            f'''
            <a href="?product={p}&stage={selected_stage}" target="_self" class="hub-link">
                <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="{stroke}" stroke-width="{stroke_width}"/>
                <text x="{x}" y="{y+7}" text-anchor="middle" class="hub-text">{p}</text>
            </a>
            '''
        )

    svg.append("</svg>")
    return "".join(svg)


def build_radial_svg(product: int, product_routes: List[Route], product_exits: List[Route], color: str) -> str:
    width = 760
    height = 540
    cx = width // 2
    cy = 220
    radius = 165
    angles = [-155, -125, -95, -65, -35, -5, 25, 55]

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="540" xmlns="http://www.w3.org/2000/svg">',
        """
        <style>
        .entry-label { font: 700 15px Arial, sans-serif; fill: #1f2937; }
        .exit-label { font: 700 14px Arial, sans-serif; fill: #3f3f46; }
        .hub-text { font: 800 42px Georgia, serif; fill: white; }
        .entry-box { fill: #eef6ff; stroke: #bfdbfe; stroke-width: 2; rx: 12; ry: 12; }
        .exit-box { fill: #f5f3ff; stroke: #ddd6fe; stroke-width: 2; rx: 12; ry: 12; }
        .line-entry { stroke: #94a3b8; stroke-width: 3; }
        .line-exit { stroke: #a78bfa; stroke-width: 3; }
        </style>
        """,
    ]

    for i, route in enumerate(product_routes[:8]):
        angle = math.radians(angles[i])
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        lx = cx + 72 * math.cos(angle)
        ly = cy + 72 * math.sin(angle)

        svg.append(f'<line x1="{x}" y1="{y}" x2="{lx}" y2="{ly}" class="line-entry"/>')
        svg.append(f'<rect x="{x-56}" y="{y-18}" width="112" height="36" class="entry-box"/>')
        svg.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" class="entry-label">{route_text(route)}</text>')

    svg.append(f'<circle cx="{cx}" cy="{cy}" r="66" fill="{color}"/>')
    svg.append(f'<text x="{cx}" y="{cy+14}" text-anchor="middle" class="hub-text">{product}</text>')

    exit_y = 430
    spacing = 130
    total = max(1, len(product_exits) - 1) * spacing
    start_x = cx - total / 2

    for i, route in enumerate(product_exits):
        x = start_x + i * spacing
        svg.append(f'<line x1="{cx}" y1="{cy+66}" x2="{x}" y2="{exit_y-26}" class="line-exit"/>')
        svg.append(f'<rect x="{x-54}" y="{exit_y-18}" width="108" height="38" class="exit-box"/>')
        svg.append(f'<text x="{x}" y="{exit_y+6}" text-anchor="middle" class="exit-label">{product} ÷ {route[0]}</text>')

    svg.append("</svg>")
    return "".join(svg)


st.markdown(
    """
    <style>
    .card {
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: white;
    }
    .hub {
        width: 132px;
        height: 132px;
        border-radius: 999px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 2.7rem;
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
        padding: 0.42rem 0.72rem;
        border-radius: 999px;
        border: 1px solid #dbe3ef;
        margin: 0.15rem 0.2rem 0.15rem 0;
        background: #f8fafc;
        font-size: 0.95rem;
    }
    .intro { background: #ecfeff; font-weight: 700; }
    .entry { background: #eef6ff; }
    .exit { background: #f5f3ff; }
    div[data-testid="stButton"] > button {
        width: 100%;
        border-radius: 12px;
        min-height: 2.8rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "stage" not in st.session_state:
    query_stage = read_query_stage()
    st.session_state.stage = query_stage if query_stage else "0"

if "product" not in st.session_state:
    st.session_state.product = 4

with st.sidebar:
    st.header("Teacher Controls")
    stage_choice = st.radio(
        "Unlock stage",
        STAGE_ORDER,
        index=STAGE_ORDER.index(st.session_state.stage),
        format_func=lambda s: STAGE_META[s]["label"],
    )
    st.session_state.stage = stage_choice
    write_query_stage(stage_choice)

stage = st.session_state.stage
products = visible_products(stage)

query_product = read_query_product()
if query_product in products:
    st.session_state.product = query_product

if st.session_state.product not in products:
    st.session_state.product = products[0]

write_query_product(st.session_state.product)
write_query_stage(stage)

st.title("TMK Structural Planner")
st.caption("Multiplication = entry routes • Division = exit routes")

st.subheader("Product World Map")
st.caption("Click any hub in the network.")

world_svg = build_world_map_svg(products, st.session_state.product, stage)
st.components.v1.html(world_svg, height=780, scrolling=False)

st.subheader("Select Product")
cols = st.columns(8)
for i, p in enumerate(products):
    with cols[i % 8]:
        if st.button(str(p), key=f"product_{p}"):
            st.session_state.product = p
            write_query_product(p)
            write_query_stage(stage)

product = st.session_state.product
color = STAGE_META[PRODUCT_STAGE[product]]["color"]

left, right = st.columns([1, 1.2])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Product Detail")

    st.markdown(
        f"""
        <div class="hub" style="background:{color};">{product}</div>
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
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Selected Product Map")
    radial = build_radial_svg(product, routes(product), exits(product), color)
    st.components.v1.html(radial, height=560, scrolling=False)
    st.markdown("</div>", unsafe_allow_html=True)
