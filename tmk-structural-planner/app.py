 import streamlit as st

st.set_page_config(page_title="TMK Structural Planner", layout="wide")

st.title("TMK Structural Planner")

st.write("### Product World")

st.write("Multiplication = entry routes to the product")
st.write("Division = exit routes from the product")

st.write("---")

products = {
    24: [(3, 8), (4, 6), (6, 4), (8, 3)],
    36: [(4, 9), (6, 6), (9, 4)],
    42: [(6, 7), (7, 6)],
    49: [(7, 7)]
}

product = st.selectbox("Choose a product", list(products.keys()))

st.header(f"Product {product}")

st.subheader("Entry routes")

for a, b in products[product]:
    st.write(f"{a} × {b} = {product}")

st.subheader("Exit routes")

for a, b in products[product]:
    st.write(f"{product} ÷ {a} = {b}")
