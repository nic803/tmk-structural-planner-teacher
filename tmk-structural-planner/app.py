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

def build_world_map(products,selected):

    width=1000
    height=700

    stage_y={
    "0":80,
    "A":150,
    "B":250,
    "C":330,
    "D":410,
    "E":500,
    "F":600,
    "G":670
    }

    positions={}

    for stage in STAGE_ORDER:

        stage_products=[p for p in STAGE_META[stage]["products"] if p in products]

        if not stage_products:
            continue

        y=stage_y[stage]

        count=len(stage_products)

        if count==1:
            xs=[width/2]
        else:
            left=200
            right=width-50
            step=(right-left)/(count-1)
            xs=[left+i*step for i in range(count)]

        for p,x in zip(stage_products,xs):
            positions[p]=(x,y)

    svg=f'<svg width="{width}" height="{height}">'

    for p in positions:

        if p not in INTRO_ROUTES:
            continue

        a,b=INTRO_ROUTES[p]

        px,py=positions[p]

        for src in [a,b]:

            if src in positions:

                sx,sy=positions[src]

                color="#cbd5e1"

                if p==selected:
                    color="#fb923c"

                svg+=f'<line x1="{sx}" y1="{sy}" x2="{px}" y2="{py}" stroke="{color}" stroke-width="3"/>'

    for p,(x,y) in positions.items():

        color=STAGE_META[PRODUCT_STAGE[p]]["color"]

        r=28

        if p==selected:
            r=34

        svg+=f'<a href="?product={p}">'
        svg+=f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" stroke="white" stroke-width="4"/>'
        svg+=f'<text x="{x}" y="{y+6}" font-size="20" text-anchor="middle" fill="white">{p}</text>'
        svg+='</a>'

    svg+="</svg>"

    return svg

if "stage" not in st.session_state:
    st.session_state.stage="0"

if "product" not in st.session_state:
    st.session_state.product=4

qp=st.query_params
if "product" in qp:
    try:
        st.session_state.product=int(qp["product"])
    except:
        pass

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

st.subheader("Product World Map (click hubs)")

svg=build_world_map(products,st.session_state.product)

st.components.v1.html(svg,height=720)

st.subheader("Select Product")

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

    st.subheader("Product Hub Map")

    st.write("Multiplication routes enter the product. Division routes exit the product.")
