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
    "D": {"label": "Stage D · Nines", "products": [18, 27, 36, 54, 63, 72, 81], "color": "#0ea5e9"},
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


def visible_stage_groups(selected_stage: str) -> Dict[str, List[int]]:
    groups: Dict[str, List[int]] = {}
    visible = set(visible_products(selected_stage))
    for s in STAGE_ORDER:
        if stage_rank(s) <= stage_rank(selected_stage):
            stage_products = [p for p in STAGE_META[s]["products"] if p in visible]
            if stage_products:
                groups[s] = stage_products
    return groups


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
        raw = st.query_params.get("product", None)
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0]
        return int(raw)
    except Exception:
        return None


def write_query_product(product: int) -> None:
    try:
        current_stage = st.query_params.get("stage", None)
        if isinstance(current_stage, list):
            current_stage = current_stage[0]

        if current_stage is not None:
            st.query_params.update({"product": str(product), "stage": str(current_stage)})
        else:
            st.query_params.update({"product": str(product)})
    except Exception:
        pass


def read_query_stage() -> str | None:
    try:
        raw = st.query_params.get("stage", None)
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0]
        raw = str(raw)
        return raw if raw in STAGE_ORDER else None
    except Exception:
        return None


def write_query_stage(stage: str) -> None:
    try:
        current_product = st.query_params.get("product", None)
        if isinstance(current_product, list):
            current_product = current_product[0]

        if current_product is not None:
            st.query_params.update({"product": str(current_product), "stage": str(stage)})
        else:
            st.query_params.update({"stage": str(stage)})
    except Exception:
        pass


def hub_radius(product: int, selected_product: int) -> int:
    route_count = len(routes(product))
    if product == selected_product:
        return 42
    if route_count >= 5:
        return 34
    if route_count >= 3:
        return 31
    return 28


def compression_count(product: int) -> int:
    return len(routes(product))


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgba(hex_color: str, alpha: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{alpha})"


def curved_path(sx: float, sy: float, px: float, py: float, bend: float = 0.22) -> str:
    mx = (sx + px) / 2
    my = (sy + py) / 2
    dx = px - sx
    dy = py - sy
    cx = mx - dy * bend
    cy = my + dx * bend * 0.18
    return f"M {sx:.1f} {sy:.1f} Q {cx:.1f} {cy:.1f} {px:.1f} {py:.1f}"


def build_world_map_svg(products: List[int], selected_product: int, selected_stage: str) -> str:
    width = 1120
    height = 780
    band_h = 78

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
            left = 200
            right = width - 80
            step = (right - left) / (count - 1)
            xs = [left + i * step for i in range(count)]

        for p, x in zip(stage_products, xs):
            positions[p] = (x, y)

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="780" xmlns="http://www.w3.org/2000/svg">',
        """
        <style>
        .stage-label { font: 700 15px Arial, sans-serif; }
        .band-label { font: 700 13px Arial, sans-serif; }
        .hub-text { font: 800 20px Georgia, serif; fill: white; pointer-events: none; }
        .hub-small { font: 700 11px Arial, sans-serif; fill: #0f172a; pointer-events: none; }
        .line { stroke: #94a3b8; stroke-width: 2.4; opacity: 0.33; fill: none; stroke-linecap: round; }
        .line-selected { stroke: #fb923c; stroke-width: 5; opacity: 0.96; fill: none; stroke-linecap: round; }
        .hub-link:hover circle.main-hub { filter: brightness(1.08); }
        .hub-link { cursor: pointer; }
        </style>
        """,
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="white"/>',
    ]

    present_stages = [s for s in STAGE_ORDER if any(PRODUCT_STAGE[p] == s for p in products)]

    for stage_key in present_stages:
        y = stage_y[stage_key]
        color = STAGE_META[stage_key]["color"]
        label = STAGE_META[stage_key]["label"]

        svg.append(
            f'<rect x="164" y="{y - band_h / 2}" width="{width - 190}" height="{band_h}" '
            f'rx="20" fill="{rgba(color, 0.07)}" stroke="{rgba(color, 0.12)}" stroke-width="1.2"/>'
        )
        svg.append(f'<text x="20" y="{y-6}" class="stage-label" fill="{color}">{label}</text>')
        svg.append(f'<text x="20" y="{y+14}" class="band-label" fill="#64748b">{len(STAGE_META[stage_key]["products"])} hubs</text>')
        svg.append(f'<line x1="178" y1="{y}" x2="{width-26}" y2="{y}" stroke="{rgba(color, 0.16)}" stroke-width="1.2"/>')

    for p in products:
        if p not in INTRO_ROUTES or p not in positions:
            continue
        a, b = INTRO_ROUTES[p]
        px, py = positions[p]
        target_r = hub_radius(p, selected_product)

        for source in (a, b):
            if source in positions:
                sx, sy = positions[source]
                source_r = hub_radius(source, selected_product)
                start_y = sy + source_r - 7
                end_y = py - target_r + 7
                d = curved_path(sx, start_y, px, end_y, 0.22)
                cls = "line-selected" if p == selected_product else "line"
                svg.append(f'<path d="{d}" class="{cls}"/>')

    for p in products:
        x, y = positions[p]
        stage_key = PRODUCT_STAGE[p]
        color = STAGE_META[stage_key]["color"]
        r = hub_radius(p, selected_product)
        route_count = compression_count(p)
        is_selected = p == selected_product
        is_compression = route_count >= 5

        outer_r = r + 8 if is_selected else (r + 6 if is_compression else r + 4)
        outer_fill = "#fed7aa" if is_selected else (rgba("#7c3aed", 0.14) if is_compression else rgba("#0f172a", 0.05))
        stroke = "#fb923c" if is_selected else "white"
        stroke_width = 6 if is_selected else 4

        svg.append(
            f'''
            <a href="?product={p}&stage={selected_stage}" target="_self" class="hub-link">
                <circle cx="{x}" cy="{y}" r="{outer_r}" fill="{outer_fill}"/>
                <circle class="main-hub" cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="{stroke}" stroke-width="{stroke_width}"/>
                <text x="{x}" y="{y+7}" text-anchor="middle" class="hub-text">{p}</text>
            '''
        )

        if is_compression:
            svg.append(
                f'''
                <rect x="{x-22}" y="{y-r-22}" width="44" height="18" rx="9" fill="white" stroke="{rgba("#7c3aed", 0.35)}" stroke-width="1.2"/>
                <text x="{x}" y="{y-r-9}" text-anchor="middle" class="hub-small">{route_count} routes</text>
                '''
            )

        svg.append("</a>")

    legend_x = width - 330
    legend_y = 24
    svg.append(
        f'''
        <g>
            <rect x="{legend_x}" y="{legend_y}" width="290" height="76" rx="16" fill="rgba(255,255,255,0.9)" stroke="#e2e8f0" stroke-width="1.2"/>
            <circle cx="{legend_x+24}" cy="{legend_y+24}" r="10" fill="#64748b"/>
            <text x="{legend_x+42}" y="{legend_y+29}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#0f172a">Product hub</text>

            <circle cx="{legend_x+24}" cy="{legend_y+52}" r="10" fill="#7c3aed" opacity="0.22"/>
            <circle cx="{legend_x+24}" cy="{legend_y+52}" r="7" fill="#7c3aed"/>
            <text x="{legend_x+42}" y="{legend_y+57}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#0f172a">Compression hub</text>

            <line x1="{legend_x+160}" y1="{legend_y+24}" x2="{legend_x+196}" y2="{legend_y+24}" stroke="#94a3b8" stroke-width="2.5" opacity="0.55" stroke-linecap="round"/>
            <text x="{legend_x+206}" y="{legend_y+29}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#0f172a">Route</text>

            <line x1="{legend_x+160}" y1="{legend_y+52}" x2="{legend_x+196}" y2="{legend_y+52}" stroke="#fb923c" stroke-width="4.5" stroke-linecap="round"/>
            <text x="{legend_x+206}" y="{legend_y+57}" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#0f172a">Selected</text>
        </g>
        '''
    )

    svg.append("</svg>")
    return "".join(svg)


def build_radial_svg(product: int, product_routes: List[Route], product_exits: List[Route], color: str) -> str:
    width = 760
    height = 560
    cx = width // 2
    cy = 270
    entry_radius = 168
    exit_radius = 170

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="560" xmlns="http://www.w3.org/2000/svg">',
        """
        <style>
        .entry-label { font: 700 15px Arial, sans-serif; fill: #111827; }
        .exit-label { font: 700 14px Arial, sans-serif; fill: #111827; }
        .hub-text { font: 800 42px Georgia, serif; fill: white; }
        .entry-box { fill: #dbeafe; stroke: #60a5fa; stroke-width: 2; rx: 12; ry: 12; }
        .exit-box { fill: #ede9fe; stroke: #8b5cf6; stroke-width: 2; rx: 12; ry: 12; }
        .line-entry { stroke: #94a3b8; stroke-width: 3; }
        .line-exit { stroke: #a78bfa; stroke-width: 3; }
        .mode-label { font: 800 13px Arial, sans-serif; fill: #475569; letter-spacing: 0.04em; }
        </style>
        """,
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="transparent"/>',
        f'<text x="{cx}" y="36" text-anchor="middle" class="mode-label">ENTRY ROUTES → INWARD</text>',
        f'<text x="{cx}" y="{height-22}" text-anchor="middle" class="mode-label">EXIT ROUTES → OUTWARD</text>',
    ]

    entry_count = min(8, len(product_routes))
    entry_start = -165
    entry_end = -15
    entry_angles = []
    if entry_count == 1:
        entry_angles = [-90]
    else:
        step = (entry_end - entry_start) / (entry_count - 1)
        entry_angles = [entry_start + i * step for i in range(entry_count)]

    for i, route in enumerate(product_routes[:8]):
        angle = math.radians(entry_angles[i])
        x = cx + entry_radius * math.cos(angle)
        y = cy + entry_radius * math.sin(angle)
        lx = cx + 76 * math.cos(angle)
        ly = cy + 76 * math.sin(angle)

        svg.append(f'<line x1="{x}" y1="{y}" x2="{lx}" y2="{ly}" class="line-entry"/>')
        svg.append(f'<rect x="{x-56}" y="{y-18}" width="112" height="36" class="entry-box"/>')
        svg.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" class="entry-label">{route_text(route)}</text>')

    exit_count = min(8, len(product_exits))
    exit_start = 15
    exit_end = 165
    exit_angles = []
    if exit_count == 1:
        exit_angles = [90]
    else:
        step = (exit_end - exit_start) / (exit_count - 1)
        exit_angles = [exit_start + i * step for i in range(exit_count)]

    for i, route in enumerate(product_exits[:8]):
        angle = math.radians(exit_angles[i])
        x = cx + exit_radius * math.cos(angle)
        y = cy + exit_radius * math.sin(angle)
        lx = cx + 78 * math.cos(angle)
        ly = cy + 78 * math.sin(angle)

        svg.append(f'<line x1="{cx + 66 * math.cos(angle)}" y1="{cy + 66 * math.sin(angle)}" x2="{x}" y2="{y}" class="line-exit"/>')
        svg.append(f'<rect x="{x-54}" y="{y-18}" width="108" height="38" class="exit-box"/>')
        svg.append(f'<text x="{x}" y="{y+6}" text-anchor="middle" class="exit-label">{product} ÷ {route[0]}</text>')

    svg.append(f'<circle cx="{cx}" cy="{cy}" r="76" fill="rgba(15,23,42,0.08)"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="66" fill="{color}"/>')
    svg.append(f'<text x="{cx}" y="{cy+14}" text-anchor="middle" class="hub-text">{product}</text>')
    svg.append("</svg>")
    return "".join(svg)


st.markdown(
    """
    <style>
    .card {
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 18px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.04);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.14);
    }
    .hub {
        width: 148px;
        height: 148px;
        border-radius: 999px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 3rem;
        font-weight: 800;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.22);
        border: 6px solid white;
    }
    .hub-label {
        text-align: center;
        margin-top: 0.7rem;
        color: rgba(226, 232, 240, 0.92);
        font-weight: 700;
    }
    .pill {
        display: inline-block;
        padding: 0.46rem 0.8rem;
        border-radius: 999px;
        border: 1px solid transparent;
        margin: 0.15rem 0.28rem 0.15rem 0;
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .intro {
        background: #ccfbf1;
        color: #134e4a;
        border-color: #5eead4;
    }
    .entry {
        background: #dbeafe;
        color: #1e3a8a;
        border-color: #93c5fd;
    }
    .exit {
        background: #ede9fe;
        color: #5b21b6;
        border-color: #c4b5fd;
    }

    .selector-stage {
        margin: 0 0 0.9rem 0;
        padding: 0.9rem 1rem;
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.03);
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }
    .selector-stage-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.65rem;
        font-weight: 800;
        color: inherit;
        font-size: 1rem;
    }
    .selector-stage-left {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }
    .selector-stage-count {
        font-size: 0.82rem;
        font-weight: 700;
        color: #94a3b8;
    }
    .selector-stage-dot {
        width: 12px;
        height: 12px;
        border-radius: 999px;
        display: inline-block;
        flex: 0 0 auto;
    }

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
st.caption("Stage bands show curriculum growth. Curved routes reduce overlap. Compression hubs display route counts.")

world_svg = build_world_map_svg(products, st.session_state.product, stage)
st.components.v1.html(world_svg, height=800, scrolling=False)

st.subheader("Select Product")
st.caption("Products are grouped by stage of introduction.")

stage_groups = visible_stage_groups(stage)
for stage_key in STAGE_ORDER:
    if stage_key not in stage_groups:
        continue

    meta = STAGE_META[stage_key]
    stage_products = stage_groups[stage_key]

    st.markdown(
        f"""
        <div class="selector-stage">
            <div class="selector-stage-header">
                <div class="selector-stage-left">
                    <span class="selector-stage-dot" style="background:{meta['color']};"></span>
                    <span>{meta['label']}</span>
                </div>
                <span class="selector-stage-count">{len(stage_products)} products</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(8)
    for i, p in enumerate(stage_products):
        with cols[i % 8]:
            if st.button(str(p), key=f"product_{stage_key}_{p}"):
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
    st.components.v1.html(radial, height=580, sc
