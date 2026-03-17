import math
from typing import Dict, List, Tuple

import streamlit as st

st.set_page_config(page_title="TMK Structural Planner", page_icon="✳️", layout="wide")

Route = Tuple[int, int]

STAGE_ORDER = ["0", "A", "B", "C", "D", "E", "F", "G"]

STAGE_META = {
    "0": {"label": "Stage 0 · Foundation", "products": [4, 6, 8, 9, 10], "color": "#475569"},
    "A": {"label": "Stage A · Identity", "products": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "color": "#9ca3af"},
    "B": {"label": "Stage B · Scaling", "products": [20, 30, 40, 50, 60, 70, 80, 90, 100], "color": "#1d4ed8"},
    "C": {"label": "Stage C · Midpoints", "products": [15, 25, 35, 45], "color": "#38bdf8"},
    "D": {"label": "Stage D · Nines", "products": [18, 27, 36, 54, 63, 72, 81], "color": "#0ea5e9"},
    "E": {"label": "Stage E · Doubling Chain", "products": [12, 14, 16, 24, 28, 32, 48, 56, 64], "color": "#14b8a6"},
    "F": {"label": "Stage F · Interleaving", "products": [21, 42], "color": "#7c3aed"},
    "G": {"label": "Stage G · Closure", "products": [49], "color": "#d4a017"},
}

INTRO_ROUTES = {
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
for s, meta in STAGE_META.items():
    for p in meta["products"]:
        PRODUCT_STAGE[p] = s


def stage_rank(s: str) -> int:
    return STAGE_ORDER.index(s)


def visible_products(stage: str) -> List[int]:
    visible = set()
    for s in STAGE_ORDER:
        if stage_rank(s) <= stage_rank(stage):
            visible.update(STAGE_META[s]["products"])
    return sorted(visible)


def routes(product: int) -> List[Route]:
    r = []
    for a in range(1, 11):
        for b in range(1, 11):
            if a * b == product:
                r.append((a, b))
    return r


def exits(product: int) -> List[Route]:
    e = []
    for d in range(1, 11):
        if product % d == 0:
            q = product // d
            if 1 <= q <= 10:
                e.append((d, q))
    return e


def distinct_factor_families(product: int) -> int:
    fam = set()
    for a, b in routes(product):
        fam.add(tuple(sorted((a, b))))
    return len(fam)


def structural_score(product: int) -> int:
    return len(routes(product)) + distinct_factor_families(product)


def is_compression_hub(product: int) -> bool:
    return len(routes(product)) >= 4 or product in {21, 24, 36, 40, 42, 48, 60, 72}


def read_query_product():
    try:
        raw = st.query_params.get("product", None)
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0]
        return int(raw)
    except Exception:
        return None


def read_query_stage():
    try:
        raw = st.query_params.get("stage", None)
        if raw is None:
            return None
        if isinstance(raw, list):
            raw = raw[0]
        if raw in STAGE_ORDER:
            return raw
        return None
    except Exception:
        return None


def write_query(product: int, stage: str) -> None:
    st.query_params.update({"product": str(product), "stage": stage})


def hub_radius(product: int, selected: int) -> int:
    if product == selected:
        return 46
    rc = len(routes(product))
    if rc >= 6:
        return 36
    if rc >= 4:
        return 33
    if rc >= 2:
        return 30
    return 27


def band_color(stage: str) -> str:
    colors = {
        "0": "#f8fafc",
        "A": "#f8fafc",
        "B": "#eff6ff",
        "C": "#ecfeff",
        "D": "#f0f9ff",
        "E": "#f0fdfa",
        "F": "#f5f3ff",
        "G": "#fffbeb",
    }
    return colors[stage]


def stage_y_map() -> Dict[str, int]:
    return {
        "0": 95,
        "A": 190,
        "B": 300,
        "C": 405,
        "D": 510,
        "E": 625,
        "F": 740,
        "G": 850,
    }


def stage_band_height(stage: str) -> int:
    heights = {
        "0": 72,
        "A": 82,
        "B": 92,
        "C": 78,
        "D": 88,
        "E": 118,
        "F": 86,
        "G": 72,
    }
    return heights[stage]


def distribute(xs_left: int, xs_right: int, count: int) -> List[float]:
    if count <= 0:
        return []
    if count == 1:
        return [(xs_left + xs_right) / 2]
    step = (xs_right - xs_left) / (count - 1)
    return [xs_left + i * step for i in range(count)]


def build_positions(products: List[int]) -> Dict[int, Tuple[float, float]]:
    pos: Dict[int, Tuple[float, float]] = {}
    ymap = stage_y_map()

    for s in STAGE_ORDER:
        sp = [p for p in STAGE_META[s]["products"] if p in products]
        if not sp:
            continue

        y = ymap[s]

        if s == "0":
            xs = distribute(220, 940, len(sp))
            for p, x in zip(sp, xs):
                pos[p] = (x, y)

        elif s == "A":
            xs = distribute(170, 990, len(sp))
            for p, x in zip(sp, xs):
                pos[p] = (x, y)

        elif s == "B":
            layout = [
                [20, 30, 40, 50],
                [60, 70, 80],
                [90, 100],
            ]
            startx = 290
            stepx = 155
            stepy = 34
            for r, row in enumerate(layout):
                row_width = (len(row) - 1) * stepx
                row_start = startx + (3 * stepx - row_width) / 2
                for c, p in enumerate(row):
                    if p in sp:
                        x = row_start + c * stepx
                        yy = y + (r - 1) * stepy
                        pos[p] = (x, yy)

        elif s == "C":
            xs = distribute(300, 860, len(sp))
            for p, x in zip(sp, xs):
                pos[p] = (x, y)

        elif s == "D":
            layout = [
                [18, 27],
                [36],
                [54, 63],
                [72],
                [81],
            ]
            stepx = 180
            stepy = 28
            center_x = 560
            for r, row in enumerate(layout):
                row_width = (len(row) - 1) * stepx
                row_start = center_x - row_width / 2
                for c, p in enumerate(row):
                    if p in sp:
                        x = row_start + c * stepx
                        yy = y + (r - 2) * stepy
                        pos[p] = (x, yy)

        elif s == "E":
            layout = [
                [12, 24, 48],
                [14, 28, 56],
                [16, 32, 64],
            ]
            startx = 420
            stepx = 150
            stepy = 42
            for r, row in enumerate(layout):
                for c, p in enumerate(row):
                    if p in sp:
                        x = startx + c * stepx
                        yy = y + (r - 1) * stepy
                        pos[p] = (x, yy)

        elif s == "F":
            custom = {21: (470, y - 18), 42: (650, y + 18)}
            for p in sp:
                pos[p] = custom[p]

        elif s == "G":
            pos[49] = (560, y)

    return pos


def curved_path(sx: float, sy: float, px: float, py: float) -> str:
    mx = (sx + px) / 2
    my = (sy + py) / 2
    dx = px - sx
    dy = py - sy
    cx = mx - dy * 0.16
    cy = my + dx * 0.08
    return f"M {sx:.1f} {sy:.1f} Q {cx:.1f} {cy:.1f} {px:.1f} {py:.1f}"


def escape_html(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_world_map_svg(products: List[int], selected: int, stage: str) -> str:
    width = 1120
    height = 910
    positions = build_positions(products)
    ymap = stage_y_map()

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        "<defs>",
        """
        <filter id="softShadow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.12"/>
        </filter>
        """,
        "</defs>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]

    for s in STAGE_ORDER:
        if stage_rank(s) > stage_rank(stage):
            continue
        y = ymap[s]
        h = stage_band_height(s)
        top = y - (h / 2)
        svg.append(
            f'<rect x="24" y="{top:.1f}" width="{width - 48}" height="{h}" rx="18" fill="{band_color(s)}" stroke="#e2e8f0" stroke-width="1.5"/>'
        )
        svg.append(
            f'<text x="42" y="{top + 24:.1f}" font-size="14" font-weight="700" fill="#334155">{escape_html(STAGE_META[s]["label"])}</text>'
        )

    for p in products:
        if p not in INTRO_ROUTES or p not in positions:
            continue

        a, b = INTRO_ROUTES[p]
        px, py = positions[p]

        for src in (a, b):
            if src not in positions:
                continue
            sx, sy = positions[src]
            path = curved_path(sx, sy, px, py)

            selected_touch = (p == selected) or (src == selected)
            if selected_touch:
                stroke = "#fb923c"
                sw = 3.8
                op = 0.92
            else:
                stroke = "#94a3b8"
                sw = 2
                op = 0.28

            svg.append(
                f'<path d="{path}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}" fill="none"/>'
            )

    if selected in positions:
        px, py = positions[selected]
        intro = INTRO_ROUTES.get(selected)
        for a, b in routes(selected):
            if (a, b) == intro:
                continue
            for src in (a, b):
                if src in positions and src != selected:
                    sx, sy = positions[src]
                    path = curved_path(sx, sy, px, py)
                    svg.append(
                        f'<path d="{path}" stroke="#8b5cf6" stroke-width="2.6" opacity="0.55" fill="none" stroke-dasharray="5 5"/>'
                    )

    for p in products:
        if p not in positions:
            continue

        x, y = positions[p]
        r = hub_radius(p, selected)
        color = STAGE_META[PRODUCT_STAGE[p]]["color"]
        selected_state = p == selected
        compression = is_compression_hub(p)

        if compression:
            halo_r = r + 9
            halo_fill = "#fde68a" if PRODUCT_STAGE[p] == "G" else "#c4b5fd"
            halo_opacity = 0.18 if not selected_state else 0.30
            svg.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{halo_r}" fill="{halo_fill}" opacity="{halo_opacity}"/>'
            )

        stroke = "#fb923c" if selected_state else "#ffffff"
        sw = 6 if selected_state else 4
        label_size = 22 if r >= 33 else 19

        title = f"Product {p} · {STAGE_META[PRODUCT_STAGE[p]]['label']} · {len(routes(p))} routes"
        svg.append(f'<a href="?product={p}&stage={stage}">')
        svg.append(f'<title>{escape_html(title)}</title>')
        svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="{stroke}" stroke-width="{sw}" filter="url(#softShadow)"/>'
        )
        svg.append(
            f'<text x="{x:.1f}" y="{y + 7:.1f}" text-anchor="middle" font-size="{label_size}" font-weight="800" fill="white">{p}</text>'
        )
        svg.append("</a>")

    legend_x = 806
    legend_y = 24
    svg.append(f'<rect x="{legend_x}" y="{legend_y}" width="288" height="92" rx="14" fill="#ffffff" stroke="#e2e8f0"/>')
    svg.append(f'<text x="{legend_x + 14}" y="{legend_y + 22}" font-size="13" font-weight="700" fill="#334155">How to read the world map</text>')
    svg.append(f'<line x1="{legend_x + 16}" y1="{legend_y + 42}" x2="{legend_x + 54}" y2="{legend_y + 42}" stroke="#94a3b8" stroke-width="2" opacity="0.55"/>')
    svg.append(f'<text x="{legend_x + 62}" y="{legend_y + 46}" font-size="12" fill="#475569">gray line = introduction route</text>')
    svg.append(f'<line x1="{legend_x + 16}" y1="{legend_y + 62}" x2="{legend_x + 54}" y2="{legend_y + 62}" stroke="#8b5cf6" stroke-width="2.2" opacity="0.75" stroke-dasharray="5 5"/>')
    svg.append(f'<text x="{legend_x + 62}" y="{legend_y + 66}" font-size="12" fill="#475569">purple dashed = extra routes for selected hub</text>')
    svg.append(f'<circle cx="{legend_x + 35}" cy="{legend_y + 82}" r="10" fill="#7c3aed" opacity="0.18"/>')
    svg.append(f'<circle cx="{legend_x + 35}" cy="{legend_y + 82}" r="7" fill="#7c3aed"/>')
    svg.append(f'<text x="{legend_x + 62}" y="{legend_y + 86}" font-size="12" fill="#475569">halo = compression hub</text>')

    svg.append("</svg>")
    return "".join(svg)


def anchor_for_angle(angle_deg: float) -> str:
    c = math.cos(math.radians(angle_deg))
    if c > 0.35:
        return "start"
    if c < -0.35:
        return "end"
    return "middle"


def text_offset_for_anchor(anchor: str) -> int:
    if anchor == "start":
        return 6
    if anchor == "end":
        return -6
    return 0


def radial_angles(count: int, start_deg: float, end_deg: float) -> List[float]:
    if count <= 0:
        return []
    if count == 1:
        return [(start_deg + end_deg) / 2]
    step = (end_deg - start_deg) / (count - 1)
    return [start_deg + i * step for i in range(count)]


def arrowhead_polygon(x: float, y: float, angle_deg: float, size: float = 9) -> str:
    left = math.radians(angle_deg + 145)
    right = math.radians(angle_deg - 145)
    x1 = x + size * math.cos(left)
    y1 = y + size * math.sin(left)
    x2 = x + size * math.cos(right)
    y2 = y + size * math.sin(right)
    return f"{x:.1f},{y:.1f} {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}"


def build_radial_svg(product: int, routes_list: List[Route], exits_list: List[Route], color: str) -> str:
    width = 760
    height = 560
    cx = width / 2
    cy = 275
    hub_r = 76

    entry_inner = hub_r + 8
    entry_outer = 198
    exit_inner = hub_r + 8
    exit_outer = 205
    label_push = 24

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#020617"/>',
        '<text x="28" y="34" font-size="18" font-weight="700" fill="#cbd5e1">Radial Hub View</text>',
        '<text x="28" y="56" font-size="12" fill="#94a3b8">Multiplication routes point inward · Division routes point outward</text>',
    ]

    entry_angles = radial_angles(len(routes_list), -155, -25)
    for angle_deg, r in zip(entry_angles, routes_list):
        angle = math.radians(angle_deg)

        ox = cx + entry_outer * math.cos(angle)
        oy = cy + entry_outer * math.sin(angle)
        ix = cx + entry_inner * math.cos(angle)
        iy = cy + entry_inner * math.sin(angle)

        svg.append(
            f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{ix:.1f}" y2="{iy:.1f}" stroke="#cbd5e1" stroke-width="3.2" opacity="0.95"/>'
        )
        svg.append(
            f'<polygon points="{arrowhead_polygon(ix, iy, angle_deg)}" fill="#cbd5e1" opacity="0.95"/>'
        )

        tx = cx + (entry_outer + label_push) * math.cos(angle)
        ty = cy + (entry_outer + label_push) * math.sin(angle)
        anchor = anchor_for_angle(angle_deg)
        dx = text_offset_for_anchor(anchor)

        svg.append(
            f'<text x="{tx + dx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" font-size="15" font-weight="600" fill="#e2e8f0">{r[0]}×{r[1]}</text>'
        )

    exit_angles = radial_angles(len(exits_list), 25, 155)
    for angle_deg, r in zip(exit_angles, exits_list):
        angle = math.radians(angle_deg)

        ix = cx + exit_inner * math.cos(angle)
        iy = cy + exit_inner * math.sin(angle)
        ox = cx + exit_outer * math.cos(angle)
        oy = cy + exit_outer * math.sin(angle)

        svg.append(
            f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{ox:.1f}" y2="{oy:.1f}" stroke="#a78bfa" stroke-width="3.2" opacity="0.95"/>'
        )
        svg.append(
            f'<polygon points="{arrowhead_polygon(ox, oy, angle_deg)}" fill="#a78bfa" opacity="0.95"/>'
        )

        tx = cx + (exit_outer + label_push) * math.cos(angle)
        ty = cy + (exit_outer + label_push) * math.sin(angle)
        anchor = anchor_for_angle(angle_deg)
        dx = text_offset_for_anchor(anchor)

        svg.append(
            f'<text x="{tx + dx:.1f}" y="{ty + 4:.1f}" text-anchor="{anchor}" font-size="15" font-weight="600" fill="#ddd6fe">{product}÷{r[0]}</text>'
        )

    if is_compression_hub(product):
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{hub_r + 14}" fill="#8b5cf6" opacity="0.18"/>')

    svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{hub_r}" fill="{color}" stroke="#ffffff" stroke-width="4"/>')
    svg.append(
        f'<text x="{cx:.1f}" y="{cy + 14:.1f}" text-anchor="middle" font-size="38" fill="white" font-weight="800">{product}</text>'
    )
    svg.append(f'<text x="{cx:.1f}" y="{cy - hub_r - 18:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="#cbd5e1">Entry routes</text>')
    svg.append(f'<text x="{cx:.1f}" y="{cy + hub_r + 34:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="#ddd6fe">Exit routes</text>')

    svg.append("</svg>")
    return "".join(svg)


def render_intro_panel() -> None:
    st.markdown(
        """
        <div style="
            background:#f8fafc;
            border:1px solid #e2e8f0;
            padding:16px 18px;
            border-radius:14px;
            margin-bottom:12px;
        ">
            <div style="font-size:16px;font-weight:800;color:#0f172a;margin-bottom:8px;">How to Read This Map</div>
            <div style="font-size:14px;color:#334155;line-height:1.65;">
                <b>Products are hubs.</b> Each circle is a product where multiplication routes meet.<br>
                <b>Multiplication enters the hub.</b> Example: <code>4 × 10 → 40</code><br>
                <b>Division exits the hub.</b> Example: <code>40 ÷ 5 → 8</code><br>
                Click any hub to explore its entry routes and exit routes.<br>
                Unlocking a stage adds new hubs and new connections while earlier hubs stay in place.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_selected_summary(product: int) -> None:
    color = STAGE_META[PRODUCT_STAGE[product]]["color"]
    intro = INTRO_ROUTES.get(product)
    intro_text = f"{intro[0]} × {intro[1]}" if intro else "—"
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(90deg,#ffffff 0%,#f8fafc 100%);
            border:1px solid #e2e8f0;
            border-radius:14px;
            padding:12px 16px;
            margin:6px 0 14px 0;
        ">
            <span style="font-size:13px;color:#64748b;font-weight:700;">Selected hub</span>
            <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-top:6px;">
                <div style="font-size:30px;font-weight:800;color:{color};">{product}</div>
                <div style="font-size:14px;color:#334155;">
                    {STAGE_META[PRODUCT_STAGE[product]]["label"]} ·
                    {len(routes(product))} entry routes ·
                    {len(exits(product))} exit routes ·
                    intro route: <b>{intro_text}</b>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if "stage" not in st.session_state:
    qp_stage = read_query_stage()
    st.session_state.stage = qp_stage if qp_stage else "0"

if "product" not in st.session_state:
    st.session_state.product = 4

if "show_help" not in st.session_state:
    st.session_state.show_help = True

with st.sidebar:
    st.header("Teacher Controls")

    stage_choice = st.radio(
        "Unlock stage",
        STAGE_ORDER,
        index=STAGE_ORDER.index(st.session_state.stage),
        format_func=lambda s: STAGE_META[s]["label"],
    )
    st.session_state.stage = stage_choice

    st.markdown("---")
    if st.session_state.show_help:
        st.info(
            "Start by clicking a hub. The upper spokes show multiplication entering the product. "
            "The lower spokes show division leaving it."
        )
        if st.button("Hide quick help", use_container_width=True):
            st.session_state.show_help = False
            st.rerun()
    else:
        if st.button("Show quick help", use_container_width=True):
            st.session_state.show_help = True
            st.rerun()

    st.markdown("---")
    st.markdown("**World rules**")
    st.caption("Products are hubs")
    st.caption("Multiplication = entry route")
    st.caption("Division = exit route")
    st.caption("Boundary = factors at or below 10")

stage = st.session_state.stage
products = visible_products(stage)

qp_product = read_query_product()
if qp_product in products:
    st.session_state.product = qp_product

if st.session_state.product not in products:
    st.session_state.product = products[0]

write_query(st.session_state.product, stage)

product = st.session_state.product
color = STAGE_META[PRODUCT_STAGE[product]]["color"]

st.title("TMK Structural Planner")
st.caption("A product world of hubs, routes, stage growth, and structural compression")

render_intro_panel()
render_selected_summary(product)

st.subheader("Product World Map")
world_svg = build_world_map_svg(products, product, stage)
st.components.v1.html(world_svg, height=920, scrolling=False)

st.subheader("Select Product")
cols = st.columns(8)
for i, p in enumerate(products):
    with cols[i % 8]:
        button_type = "primary" if p == product else "secondary"
        if st.button(str(p), key=f"p{p}", use_container_width=True, type=button_type):
            st.session_state.product = p
            write_query(p, stage)
            st.rerun()

left, right = st.columns([0.95, 1.25])

with left:
    st.subheader("Hub Detail")

    score = structural_score(product)
    family_count = distinct_factor_families(product)

    st.markdown(
        f"""
        <div style="
            background:#f8fafc;
            border:1px solid #e2e8f0;
            border-radius:16px;
            padding:18px 20px 16px 20px;
            margin-bottom:14px;
        ">
            <div style="font-size:14px;color:#64748b;font-weight:700;">Selected hub</div>
            <div style="font-size:44px;line-height:1.05;font-weight:800;color:{color};">{product}</div>
            <div style="margin-top:8px;color:#334155;font-size:14px;">
                {STAGE_META[PRODUCT_STAGE[product]]["label"]}<br>
                {len(routes(product))} entry routes · {len(exits(product))} exit routes · {family_count} factor families · score {score}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    intro = INTRO_ROUTES.get(product)
    if intro:
        st.markdown(f"**Introduction route:** `{intro[0]} × {intro[1]} = {product}`")

    if is_compression_hub(product):
        st.markdown("**Compression note:** this hub gathers multiple valid P10 routes.")

    st.markdown("**Entry routes**")
    for r in routes(product):
        marker = "← intro" if intro == r else ""
        st.write(f"{r[0]} × {r[1]} = {product} {marker}")

    st.markdown("**Exit routes**")
    for r in exits(product):
        st.write(f"{product} ÷ {r[0]} = {r[1]}")

with right:
    st.subheader("Selected Product Map")
    radial = build_radial_svg(product, routes(product), exits(product), color)
    st.components.v1.html(radial, height=580, scrolling=False)
