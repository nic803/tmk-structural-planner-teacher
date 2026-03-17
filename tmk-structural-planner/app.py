import math
import streamlit as st
from typing import Dict, List, Tuple

st.set_page_config(page_title="TMK Structural Planner", page_icon="✳️", layout="wide")

Route = Tuple[int, int]

STAGE_ORDER = ["0","A","B","C","D","E","F","G"]

STAGE_META = {
    "0":{"label":"Stage 0 · Foundation","products":[4,6,8,9,10],"color":"#4b5563"},
    "A":{"label":"Stage A · Identity","products":[1,2,3,4,5,6,7,8,9,10],"color":"#9ca3af"},
    "B":{"label":"Stage B · Scaling","products":[20,30,40,50,60,70,80,90,100],"color":"#1d4ed8"},
    "C":{"label":"Stage C · Midpoints","products":[15,25,35,45],"color":"#38bdf8"},
    "D":{"label":"Stage D · Nines","products":[18,27,36,54,63,72,81],"color":"#0ea5e9"},
    "E":{"label":"Stage E · Doubling Chain","products":[12,14,16,24,28,32,48,56,64],"color":"#14b8a6"},
    "F":{"label":"Stage F · Interleaving","products":[21,42],"color":"#7c3aed"},
    "G":{"label":"Stage G · Closure","products":[49],"color":"#d4a017"},
}

INTRO_ROUTES={
1:(1,1),2:(1,2),3:(1,3),4:(1,4),5:(1,5),
6:(1,6),7:(1,7),8:(1,8),9:(1,9),10:(1,10),
12:(2,6),14:(2,7),15:(3,5),16:(2,8),18:(2,9),
20:(2,10),21:(3,7),24:(4,6),25:(5,5),27:(3,9),
28:(4,7),30:(3,10),32:(4,8),35:(5,7),36:(4,9),
40:(4,10),42:(6,7),45:(5,9),48:(6,8),49:(7,7),
50:(5,10),54:(6,9),56:(7,8),60:(6,10),63:(7,9),
64:(8,8),70:(7,10),72:(8,9),80:(8,10),81:(9,9),
90:(9,10),100:(10,10)
}

PRODUCT_STAGE={}
for s,m in STAGE_META.items():
    for p in m["products"]:
        PRODUCT_STAGE[p]=s


def stage_rank(s):
    return STAGE_ORDER.index(s)


def visible_products(stage):
    v=set()
    for s in STAGE_ORDER:
        if stage_rank(s)<=stage_rank(stage):
            v.update(STAGE_META[s]["products"])
    return sorted(v)


def routes(product):
    r=[]
    for a in range(1,11):
        for b in range(1,11):
            if a*b==product:
                r.append((a,b))
    return r


def exits(product):
    e=[]
    for d in range(1,11):
        if product%d==0:
            q=product//d
            if 1<=q<=10:
                e.append((d,q))
    return e


def hub_radius(p,selected):
    rc=len(routes(p))
    if p==selected:
        return 42
    if rc>=5:
        return 34
    if rc>=3:
        return 31
    return 28


def curved_path(sx,sy,px,py):
    mx=(sx+px)/2
    my=(sy+py)/2
    dx=px-sx
    dy=py-sy
    cx=mx-dy*0.2
    cy=my+dx*0.1
    return f"M {sx} {sy} Q {cx} {cy} {px} {py}"


def build_world_map_svg(products,selected):

    width=1120
    height=780

    stage_y={
    "0":90,"A":170,"B":270,"C":360,
    "D":440,"E":540,"F":640,"G":720
    }

    pos={}

    for stage in STAGE_ORDER:

        sp=[p for p in STAGE_META[stage]["products"] if p in products]
        if not sp:
            continue

        y=stage_y[stage]

        # special layout for Stage E
        if stage=="E" and len(sp)==9:

            cols=[0,1,2]

            layout=[
            [12,24,48],
            [14,28,56],
            [16,32,64]
            ]

            startx=420
            step=140
            stepy=38

            for row_i,row in enumerate(layout):
                for col_i,p in enumerate(row):
                    if p in sp:
                        x=startx+col_i*step
                        yy=y+(row_i-1)*stepy
                        pos[p]=(x,yy)

        else:

            count=len(sp)

            if count==1:
                xs=[width/2]
            else:
                left=200
                right=width-80
                step=(right-left)/(count-1)
                xs=[left+i*step for i in range(count)]

            for p,x in zip(sp,xs):
                pos[p]=(x,y)

    svg=[
    f'<svg viewBox="0 0 {width} {height}" width="100%" height="780" xmlns="http://www.w3.org/2000/svg">',
    '<rect x="0" y="0" width="100%" height="100%" fill="white"/>'
    ]

    for p in products:

        if p not in INTRO_ROUTES:
            continue

        a,b=INTRO_ROUTES[p]

        if p not in pos:
            continue

        px,py=pos[p]

        for src in (a,b):

            if src in pos:

                sx,sy=pos[src]

                d=curved_path(sx,sy,px,py)

                svg.append(f'<path d="{d}" stroke="#94a3b8" stroke-width="2" fill="none" opacity="0.35"/>')

    for p in products:

        x,y=pos[p]
        r=hub_radius(p,selected)
        color=STAGE_META[PRODUCT_STAGE[p]]["color"]

        svg.append(f'''
        <a href="?product={p}">
        <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="white" stroke-width="4"/>
        <text x="{x}" y="{y+6}" text-anchor="middle" font-size="18" fill="white" font-weight="bold">{p}</text>
        </a>
        ''')

    svg.append("</svg>")

    return "".join(svg)


if "stage" not in st.session_state:
    st.session_state.stage="0"

if "product" not in st.session_state:
    st.session_state.product=4

with st.sidebar:
    st.header("Teacher Controls")
    st.session_state.stage=st.radio(
        "Unlock stage",
        STAGE_ORDER,
        index=STAGE_ORDER.index(st.session_state.stage),
        format_func=lambda s:STAGE_META[s]["label"]
    )

stage=st.session_state.stage
products=visible_products(stage)

st.title("TMK Structural Planner")
st.caption("Multiplication = entry routes • Division = exit routes")

st.subheader("Product World Map")

svg=build_world_map_svg(products,st.session_state.product)

st.components.v1.html(svg,height=780,scrolling=False)
