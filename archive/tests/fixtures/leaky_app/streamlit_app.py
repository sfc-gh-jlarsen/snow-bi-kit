# Seeded acceptance fixture (a): DO NOT COPY. Deliberately broken for kit tests.
# Values are fake test strings, not real credentials.
import streamlit as st
from snowflake.snowpark import Session

session = Session.builder.configs({
    "account": "xy12345",
    "user": "jdoe_analyst",
    "password": "Tr1ck-Pa55w0rd-for-tests",
    "role": "ACCOUNTADMIN",
}).create()

df = session.sql("SELECT region, SUM(net_sales_usd) AS net_sales FROM SALES GROUP BY 1").to_pandas()
st.metric("Net sales", f"{df['NET_SALES'].sum():,.0f}")
st.bar_chart(df, x="REGION", y="NET_SALES")
