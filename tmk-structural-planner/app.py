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
"D":{"label":"Stage D · Nines","products":[18,27,36,54,63,72,81],"color":"#38bdf8"},
"E":{"label":"Stage E · Doubling Chain","products":[12,14,16,24,28,32,48,56,64],"color":"#14b8a6"},
"F":{"label":"Stage F · Interleaving","products":[21,42],"color":"#7c3aed"},
"G":{"label":"Stage G · Closure","products":[49],"color":"#d4a017"},
}

INTRO_ROUTES: Dict[int,Route] = {
1:(1,1),2:(1,2),3:(1,3),4:(1,4),5:(1,5),6:(1,6),7:(1,7),8:(1,8),9:(1,9),10:(1,10),
12:(2,6),14:(2,7),15:(3,5),16:(2,8),18:(2,9),20:(2,10),21:(3,7),24:(4,6),
25:(5,5),27:(3,9),28:(4,7),30:(3,10),32:(4,8),35:(5,7),36:(4,9),
40:(4,10),42:(6,7),45:(5,9),48:(6,8),49:(7,7),50:(5,10),54:(6,9),
56:(7,8),60:(6,10),63:(7,9),64:(8,8),70:(7,10),72:(8,9),80:(8,10),
81:(9,9),90:(9,10),100:(10,10)
}

PRODUCT_STAGE={}
for s in STAGE_META:
    for p in STAGE_META[s]["products"]:
        if p not in PRODUCT_STAGE:
            PRODUCT_STAGE[p]=s

def stage_rank(s):
    return STAGE_ORDER.index(s)

def visible_products(stage):
    vis=set()
    for s in STAGE_ORDER:
        if stage_rank(s)<=stage_rank(stage):
            vis.update(STAGE_META[s]["products"])
    return sorted(vis)

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

def route_text(r):
    return f"{r[0]} × {r[1]}"

def exit_text(p,r):
    return f"{p} ÷ {r[0]} = {r[1]}"

def intro_text(p):
    r=INTRO_ROUTES[p]
    return f"{r[0]} × {r[1]} = {p}"

def radial_svg(product,route_list,exit_list,color):

    cx=350
    cy=230
    radius=160

    angles=[-140,-100,-60,-20,20,60,100,140]

    svg=f'<svg width="700" height="520">'

    for i,r in enumerate(route_list[:8]):

        a=math.radians(angles[i])
        x=cx+radius*math.cos(a)
        y=cy+radius*math.sin(a)

        lx=cx+70*math.cos(a)
        ly=cy+70*math.sin(a)

        svg+=f'<line x1="{x}" y1="{y}" x2="{lx}" y2="{ly}" stroke="#94a3b8" stroke-width="3"/>'
        svg+=f'<rect x="{x-50}" y="{y-15}" width="100" height="30" rx="10" fill="#eef6ff" stroke="#bfdbfe"/>'
        svg+=f'<text x="{x}" y="{y+5}" font-size="14" text-anchor="middle">{route_text(r)}</text>'

    svg+=f'<circle cx="{cx}" cy="{cy}" r="60" fill="{color}"/>'
    svg+=f'<text x="{cx}" y="{cy+15}" font-size="40" text-anchor="middle" fill="white">{product}</text>'

    y2=420
    start=cx-(len(exit_list)-1)*70

    for i,r in enumerate(exit_list):
        x=start+i*140
        svg+=f'<line x1="{cx}" y1="{cy+60}" x2="{x}" y2="{y2-20}" stroke="#a78bfa" stroke-width="3"/>'
        svg+=f'<rect x="{x-50}" y="{y2-20}" width="100" height="35" rx="10" fill="#f5f3ff" stroke="#ddd6fe"/>'
        svg+=f'<text x="{x}" y="{y2+2}" font-size="14" text-anchor="middle">{product} ÷ {r[0]}</text>'

    svg+="</svg>"
    return svg

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
        format_func=lambda s: STAGE_META[s]["label"]
    )

stage=st.session_state.stage
products=visible_products(stage)

if st.session_state.product not in products:
    st.session_state.product=products[0]

st.title("TMK Structural Planner")
st.caption("Multiplication = entry routes • Division = exit routes")

cols=st.columns(8)

for i,p in enumerate(products):
    with cols[i%8]:
        if st.button(str(p)):
            st.session_state.product=p

product=st.session_state.product
color=STAGE_META[PRODUCT_STAGE[product]]["color"]

left,right=st.columns([1,1.2])

with left:

    st.subheader("Product Detail")

    st.markdown(
    f"""
    <div style="background:{color};
    width:120px;height:120px;border-radius:100px;
    display:flex;align-items:center;justify-content:center;
    font-size:40px;color:white;font-weight:700;margin:auto;">
    {product}
    </div>
    """,
    unsafe_allow_html=True)

    st.write("Introduction route")
    st.write(intro_text(product))

    st.write("Full route field")
    for r in routes(product):
        st.write(route_text(r),"=",product)

    st.write("Exit routes")
    for r in exits(product):
        st.write(exit_text(product,r))

with right:

    st.subheader("Radial Product Map")

    svg=radial_svg(product,routes(product),exits(product),color)

    st.components.v1.html(svg,height=520)
