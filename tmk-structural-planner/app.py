import math
from typing import Dict, List, Set, Tuple

import streamlit as st
import streamlit.components.v2 as components

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
for stage_key, meta in STAGE_META.items():
    for product in meta["products"]:
        PRODUCT_STAGE[product] = stage_key


WORLD_MAP_COMPONENT = components.component(
    "tmk_clickable_world_map",
    html="""
    <div id="tmk-root"></div>
    """,
    css="""
    :host {
      display: block;
      width: 100%;
    }

    #tmk-root {
      width: 100%;
    }

    #tmk-root svg {
      width: 100%;
      height: auto;
      display: block;
    }

    #tmk-root [data-product] {
      cursor: pointer;
    }
    """,
    js="""
    export default function(component) {
      const { data, parentElement, setTriggerValue } = component;
      const root = parentElement.querySelector("#tmk-root");
      if (!root) return;

      const svg = data?.svg ?? "";
      const minHeight = data?.height ?? 1200;

      root.innerHTML = svg;
      root.style.minHeight = `${minHeight}px`;

      const clickable = root.querySelectorAll("[data-product]");
      clickable.forEach((node) => {
        node.onclick = (e) => {
          e.preventDefault();
          e.stopPropagation();
          const product = node.getAttribute("data-product");
          setTriggerValue("clicked", product);
        };
      });
    }
    """,
)


def render_clickable_world_map(svg: str, height: int, key: str):
    result = WORLD_MAP_COMPONENT(
        data={"svg": svg, "height": height},
        key=key,
        on_clicked_change=lambda: None,
    )
    return getattr(result, "clicked", None)


def stage_rank(stage: str) -> int:
    return STAGE_ORDER.index(stage)


def visible_products(stage: str) -> List[int]:
    visible = set()
    for s in STAGE_ORDER:
        if stage_rank(s) <= stage_rank(stage):
            visible.update(STAGE_META[s]["products"])
    return sorted(visible)


def routes(product: int) -> List[Route]:
    out: List[Route] = []
    for a in range(1, 11):
        for b in range(1, 11):
            if a * b == product:
                out.append((a, b))
    return out


def exits(product: int) -> List[Route]:
    out: List[Route] = []
    for d in range(1, 11):
        if product % d == 0:
            q = product // d
            if 1 <= q <= 10:
                out.append((d, q))
    return out


def distinct_factor_families(product: int) -> int:
    families = set()
    for a, b in routes(product):
        families.add(tuple(sorted((a, b))))
    return len(families)


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
        return 48
    route_count = len(routes(product))
    if route_count >= 6:
        return 38
    if route_count >= 4:
        return 35
    if route_count >= 2:
        return 32
    return 29


def band_color(stage: str) -> str:
    return {
        "0": "#f8fafc",
        "A": "#f8fafc",
        "B": "#eff6ff",
        "C": "#ecfeff",
        "D": "#f0f9ff",
        "E": "#f0fdfa",
        "F": "#f5f3ff",
        "G": "#fffbeb",
    }[stage]


def stage_y_map() -> Dict[str, int]:
    return {
        "0": 110,
        "A": 230,
        "B": 380,
        "C": 530,
        "D": 700,
        "E": 910,
        "F": 1120,
        "G": 1290,
    }


def stage_band_height(stage: str) -> int:
    return {
        "0": 86,
        "A": 96,
        "B": 120,
        "C": 96,
        "D": 130,
        "E": 150,
        "F": 105,
        "G": 82,
    }[stage]


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

    for stage in STAGE_ORDER:
        stage_products = [p for p in STAGE_META[stage]["products"] if p in products]
        if not stage_products:
            continue

        y = ymap[stage]

        if stage == "0":
            xs = distribute(180, 940, len(stage_products))
            for p, x in zip(stage_products, xs):
                pos[p] = (x, y)

        elif stage == "A":
            xs = distribute(130, 990, len(stage_products))
            for p, x in zip(stage_products, xs):
                pos[p] = (x, y)

        elif stage == "B":
            custom = {
                20: (250, y - 34),
                30: (430, y - 34),
                40: (610, y - 34),
                50: (790, y - 34),
                60: (340, y + 10),
                70: (560, y + 10),
                80: (780, y + 10),
                90: (450, y + 52),
                100: (670, y + 52),
            }
            for p in stage_products:
                pos[p] = custom[p]

        elif stage == "C":
            xs = distribute(240, 880, len(stage_products))
            for p, x in zip(stage_products, xs):
                pos[p] = (x, y)

        elif stage == "D":
            custom = {
                18: (430, y - 54),
                27: (760, y - 54),
                36: (560, y - 10),
                54: (400, y + 38),
                63: (690, y + 38),
                72: (560, y + 82),
                81: (560, y + 126),
            }
            for p in stage_products:
                pos[p] = custom[p]

        elif stage == "E":
            custom = {
                12: (280, y - 46),
                24: (540, y - 6),
                48: (810, y - 46),
                14: (315, y + 14),
                28: (575, y + 54),
                56: (845, y + 14),
                16: (350, y + 74),
                32: (610, y + 114),
                64: (880, y + 74),
            }
            for p in stage_products:
                pos[p] = custom[p]

        elif stage == "F":
            custom = {
                21: (390, y - 6),
                42: (730, y + 18),
            }
            for p in stage_products:
                pos[p] = custom[p]

        elif stage == "G":
            pos[49] = (560, y)

    return pos


def curved_path(sx: float, sy: float, px: float, py: float) -> str:
    mx = (sx + px) / 2
    my = (sy + py) / 2
    dx = px - sx
    dy = py - sy
    cx = mx - dy * 0.14
    cy = my + dx * 0.07
    return f"M {sx:.1f} {sy:.1f} Q {cx:.1f} {cy:.1f} {px:.1f} {py:.1f}"


def escape_html(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def radial_angles(count: int, start_deg: float, end_deg: float) -> List[float]:
    if count <= 0:
        return []
    if count == 1:
        return [(start_deg + end_deg) / 2]
    step = (end_deg - start_deg) / (count - 1)
    return [start_deg + i * step for i in range(count)]


def selected_neighborhood(selected: int, visible: List[int]) -> Set[int]:
    visible_set = set(visible)
    neighbors = {selected}

    intro = INTRO_ROUTES.get(selected)
    if intro:
        a, b = intro
        if a in visible_set:
            neighbors.add(a)
        if b in visible_set:
            neighbors.add(b)

    for a, b in routes(selected):
        if a in visible_set:
            neighbors.add(a)
        if b in visible_set:
            neighbors.add(b)

    for p in visible:
        intro_p = INTRO_ROUTES.get(p)
        if intro_p and (intro_p[0] == selected or intro_p[1] == selected):
            neighbors.add(p)

    return neighbors


def build_world_map_svg(products: List[int], selected: int, stage: str) -> str:
    width = 1120
    height = 1380

    positions = build_positions(products)
    ymap = stage_y_map()
    spotlight = selected_neighborhood(selected, products)

    support_hubs: Dict[int, Tuple[float, float]] = {}
    selected_routes = routes(selected)
    selected_exits = exits(selected)

    candidate_nodes = set()
    for a, b in selected_routes:
        candidate_nodes.add(a)
        candidate_nodes.add(b)
    for d, q in selected_exits:
        candidate_nodes.add(d)
        candidate_nodes.add(q)

    candidate_nodes.discard(selected)

    if selected in positions:
        sx, sy = positions[selected]
        missing = [n for n in sorted(candidate_nodes) if n not in positions]
        if missing:
            angles = radial_angles(len(missing), -160, 160)
            support_radius = 155
            for n, angle_deg in zip(missing, angles):
                angle = math.radians(angle_deg)
                support_hubs[n] = (
                    sx + support_radius * math.cos(angle),
                    sy + support_radius * math.sin(angle),
                )

    all_positions = {**positions, **support_hubs}

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        "<defs>",
        """
        <filter id="softShadow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.14"/>
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
            f'<rect x="24" y="{top:.1f}" width="{width - 48}" height="{h}" rx="20" '
            f'fill="{band_color(s)}" stroke="#e2e8f0" stroke-width="1.5"/>'
        )
        svg.append(
            f'<text x="42" y="{top + 28:.1f}" font-size="16" font-weight="800" fill="#334155">'
            f'{escape_html(STAGE_META[s]["label"])}</text>'
        )

    for p in products:
        if p not in INTRO_ROUTES or p not in all_positions:
            continue

        a, b = INTRO_ROUTES[p]
        px, py = all_positions[p]

        for src in (a, b):
            if src not in all_positions:
                continue

            sx, sy = all_positions[src]
            path = curved_path(sx, sy, px, py)

            selected_touch = (p == selected) or (src == selected)
            spotlight_touch = (p in spotlight) and (src in spotlight)

            if selected_touch:
                stroke = "#fb923c"
                sw = 4.4
                op = 0.98
            elif spotlight_touch:
                stroke = "#94a3b8"
                sw = 2.6
                op = 0.34
            else:
                stroke = "#94a3b8"
                sw = 1.8
                op = 0.11

            svg.append(
                f'<path d="{path}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}" fill="none"/>'
            )

    if selected in all_positions:
        px, py = all_positions[selected]
        intro = INTRO_ROUTES.get(selected)
        for a, b in routes(selected):
            if (a, b) == intro:
                continue
            for src in (a, b):
                if src in all_positions and src != selected:
                    sx, sy = all_positions[src]
                    path = curved_path(sx, sy, px, py)
                    svg.append(
                        f'<path d="{path}" stroke="#8b5cf6" stroke-width="3" opacity="0.56" '
                        f'fill="none" stroke-dasharray="5 6"/>'
                    )

    for p in products:
        if p not in all_positions:
            continue

        x, y = all_positions[p]
        r = hub_radius(p, selected)
        color = STAGE_META[PRODUCT_STAGE[p]]["color"]
        selected_state = p == selected
        compression = is_compression_hub(p)
        in_spotlight = p in spotlight

        if compression:
            halo_r = r + 10
            halo_fill = "#fde68a" if PRODUCT_STAGE[p] == "G" else "#c4b5fd"
            halo_opacity = 0.16 if not selected_state else 0.28
            if not in_spotlight and not selected_state:
                halo_opacity = 0.07
            svg.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{halo_r}" fill="{halo_fill}" opacity="{halo_opacity}"/>'
            )

        stroke = "#fb923c" if selected_state else "#ffffff"
        sw = 6 if selected_state else 4
        label_size = 24 if r >= 35 else 21

        if selected_state:
            overall_opacity = 1.0
        elif in_spotlight:
            overall_opacity = 0.98
        else:
            overall_opacity = 0.34

        title = f"Product {p} · {STAGE_META[PRODUCT_STAGE[p]]['label']} · {len(routes(p))} routes"

        svg.append(f'<g data-product="{p}">')
        svg.append(f'<title>{escape_html(title)}</title>')
        svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" fill-opacity="{overall_opacity}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-opacity="{overall_opacity}" filter="url(#softShadow)"/>'
        )
        svg.append(
            f'<text x="{x:.1f}" y="{y + 8:.1f}" text-anchor="middle" font-size="{label_size}" '
            f'font-weight="800" fill="white" fill-opacity="{overall_opacity}">{p}</text>'
        )
        svg.append("</g>")

    # support hubs are visual only, not clickable
    for p, (x, y) in support_hubs.items():
        svg.append(f'<g>')
        svg.append(f'<title>{escape_html(f"Support hub {p}")}</title>')
        svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="#ffffff" stroke="#64748b" stroke-width="3" opacity="0.95"/>'
        )
        svg.append(
            f'<text x="{x:.1f}" y="{y + 6:.1f}" text-anchor="middle" font-size="16" font-weight="800" fill="#334155">{p}</text>'
        )
        svg.append("</g>")

    legend_x = 760
    legend_y = 26
    svg.append(f'<rect x="{legend_x}" y="{legend_y}" width="334" height="140" rx="14" fill="#ffffff" stroke="#e2e8f0"/>')
    svg.append(f'<text x="{legend_x + 14}" y="{legend_y + 24}" font-size="14" font-weight="800" fill="#334155">How to read the world map</text>')
    svg.append(f'<line x1="{legend_x + 16}" y1="{legend_y + 46}" x2="{legend_x + 54}" y2="{legend_y + 46}" stroke="#94a3b8" stroke-width="2.2" opacity="0.55"/>')
    svg.append(f'<text x="{legend_x + 62}" y="{legend_y + 50}" font-size="13" fill="#475569">gray line = introduction route</text>')
    svg.append(f'<line x1="{legend_x + 16}" y1="{legend_y + 68}" x2="{legend_x + 54}" y2="{legend_y + 68}" stroke="#8b5cf6" stroke-width="2.4" opacity="0.75" stroke-dasharray="5 6"/>')
    svg.append(f'<text x="{legend_x + 62}" y="{legend_y + 72}" font-size="13" fill="#475569">purple dashed = extra routes for selected hub</text>')
    svg.append(f'<circle cx="{legend_x + 35}" cy="{legend_y + 90}" r="11" fill="#7c3aed" opacity="0.18"/>')
    svg.append(f'<circle cx="{legend_x + 35}" cy="{legend_y + 90}" r="8" fill="#7c3aed"/>')
    svg.append(f'<text x="{legend_x + 62}" y="{legend_y + 94}" font-size="13" fill="#475569">halo = compression hub</text>')
    svg.append(f'<circle cx="{legend_x + 35}" cy="{legend_y + 114}" r="10" fill="#ffffff" stroke="#64748b" stroke-width="2"/>')
    svg.append(f'<text x="{legend_x + 62}" y="{legend_y + 118}" font-size="13" fill="#475569">outlined hub = route support hub</text>')
    svg.append("</svg>")

    return "".join(svg)


def anchor_for_angle(angle_deg: float) -> str:
    c = math.cos(math.radians(angle_deg))
    if c > 0.30:
        return "start"
    if c < -0.30:
        return "end"
    return "middle"


def text_offset_for_anchor(anchor: str) -> int:
    if anchor == "start":
        return 7
    if anchor == "end":
        return -7
    return 0


def arrowhead_polygon(x: float, y: float, angle_deg: float, size: float = 11) -> str:
    left = math.radians(angle_deg + 145)
    right = math.radians(angle_deg - 145)
    x1 = x + size * math.cos(left)
    y1 = y + size * math.sin(left)
    x2 = x + size * math.cos(right)
    y2 = y + size * math.sin(right)
    return f"{x:.1f},{y:.1f} {x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f}"


def build_radial_svg(product: int, routes_list: List[Route], exits_list: List[Route], color: str) -> str:
    width = 760
    height = 600
    cx = width / 2
    cy = 305
    hub_r = 92

    entry_count = len(routes_list)
    exit_count = len(exits_list)
    max_count = max(entry_count, exit_count)

    if max_count <= 3:
        entry_outer = 148
        exit_outer = 158
        label_push = 14
        entry_range = (-145, -35)
        exit_range = (35, 145)
    elif max_count <= 4:
        entry_outer = 160
        exit_outer = 170
        label_push = 15
        entry_range = (-150, -30)
        exit_range = (30, 150)
    else:
        entry_outer = 172
        exit_outer = 182
        label_push = 16
        entry_range = (-150, -30)
        exit_range = (30, 150)

    entry_inner = hub_r + 6
    exit_inner = hub_r + 10

    svg = [
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" xmlns="http://www.w3.org/2000/svg">',
        '<rect width="100%" height="100%" fill="#020617"/>',
        '<text x="22" y="34" font-size="28" font-weight="800" fill="#e2e8f0">Radial Hub View</text>',
        '<text x="22" y="64" font-size="16" fill="#cbd5e1">Multiplication routes point inward · Division routes point outward</text>',
    ]

    entry_angles = radial_angles(entry_count, entry_range[0], entry_range[1])
    for angle_deg, r in zip(entry_angles, routes_list):
        angle = math.radians(angle_deg)

        ox = cx + entry_outer * math.cos(angle)
        oy = cy + entry_outer * math.sin(angle)
        ix = cx + entry_inner * math.cos(angle)
        iy = cy + entry_inner * math.sin(angle)

        svg.append(
            f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{ix:.1f}" y2="{iy:.1f}" stroke="#e2e8f0" stroke-width="4" opacity="0.95"/>'
        )
        svg.append(
            f'<polygon points="{arrowhead_polygon(ix, iy, angle_deg)}" fill="#e2e8f0" opacity="0.95"/>'
        )

        tx = cx + (entry_outer + label_push) * math.cos(angle)
        ty = cy + (entry_outer + label_push) * math.sin(angle)
        anchor = anchor_for_angle(angle_deg)
        dx = text_offset_for_anchor(anchor)

        svg.append(
            f'<text x="{tx + dx:.1f}" y="{ty:.1f}" text-anchor="{anchor}" font-size="24" font-weight="700" fill="#ffffff">{r[0]}×{r[1]}</text>'
        )

    exit_angles = radial_angles(exit_count, exit_range[0], exit_range[1])
    for angle_deg, r in zip(exit_angles, exits_list):
        angle = math.radians(angle_deg)

        ix = cx + exit_inner * math.cos(angle)
        iy = cy + exit_inner * math.sin(angle)
        ox = cx + exit_outer * math.cos(angle)
        oy = cy + exit_outer * math.sin(angle)

        svg.append(
            f'<line x1="{ix:.1f}" y1="{iy:.1f}" x2="{ox:.1f}" y2="{oy:.1f}" stroke="#a78bfa" stroke-width="4" opacity="0.95"/>'
        )
        svg.append(
            f'<polygon points="{arrowhead_polygon(ox, oy, angle_deg)}" fill="#a78bfa" opacity="0.95"/>'
        )

        tx = cx + (exit_outer + label_push) * math.cos(angle)
        ty = cy + (exit_outer + label_push) * math.sin(angle)
        anchor = anchor_for_angle(angle_deg)
        dx = text_offset_for_anchor(anchor)

        svg.append(
            f'<text x="{tx + dx:.1f}" y="{ty + 6:.1f}" text-anchor="{anchor}" font-size="24" font-weight="700" fill="#ddd6fe">{product}÷{r[0]}</text>'
        )

    if is_compression_hub(product):
        svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{hub_r + 16}" fill="#8b5cf6" opacity="0.18"/>')

    svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{hub_r}" fill="{color}" stroke="#ffffff" stroke-width="5"/>')
    svg.append(
        f'<text x="{cx:.1f}" y="{cy + 18:.1f}" text-anchor="middle" font-size="52" fill="white" font-weight="800">{product}</text>'
    )
    svg.append(f'<text x="{cx:.1f}" y="{cy - hub_r - 18:.1f}" text-anchor="middle" font-size="18" font-weight="800" fill="#e2e8f0">Entry routes</text>')
    svg.append(f'<text x="{cx:.1f}" y="{cy + hub_r + 34:.1f}" text-anchor="middle" font-size="18" font-weight="800" fill="#ddd6fe">Exit routes</text>')
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
                Click a hub on the map or use the selector below to change focus.<br>
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
            "Click a hub or use the selector below. The upper spokes show multiplication entering the product. "
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

product = st.session_state.product
write_query(product, stage)

st.title("TMK Structural Planner")
st.caption("A product world of hubs, routes, stage growth, and structural compression")

render_intro_panel()
render_selected_summary(product)

st.subheader("Product World Map")
world_svg = build_world_map_svg(products, product, stage)

clicked_product = render_clickable_world_map(
    world_svg,
    height=1390,
    key=f"world-map-{stage}",
)

if clicked_product is not None:
    try:
        clicked_int = int(clicked_product)
        if clicked_int in products and clicked_int != st.session_state.product:
            st.session_state.product = clicked_int
            write_query(clicked_int, stage)
            st.rerun()
    except ValueError:
        pass

st.subheader("Select Product")
chosen = st.selectbox(
    "Choose a visible product",
    products,
    index=products.index(st.session_state.product) if st.session_state.product in products else 0,
    label_visibility="collapsed",
)

if chosen != st.session_state.product:
    st.session_state.product = chosen
    write_query(chosen, stage)
    st.rerun()

product = st.session_state.product
color = STAGE_META[PRODUCT_STAGE[product]]["color"]

left, right = st.columns([0.95, 1.25])

with left:
    st.subheader("Hub Detail")

    score = structural_score(product)
    family_count = distinct_factor_families(product)
    stage_label = STAGE_META[PRODUCT_STAGE[product]]["label"]

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
                {stage_label}<br>
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
    st.html(radial)
