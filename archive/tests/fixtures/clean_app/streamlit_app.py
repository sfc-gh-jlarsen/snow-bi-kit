import altair as alt
import streamlit as st

import bi_kit_runtime as bi
from snowflake.snowpark.context import get_active_session

bi.configure(get_active_session(), debug=True)

run = bi.run_visual("Net sales by region", "SELECT region, SUM(net_sales_usd) AS net_sales FROM SALES GROUP BY 1",
                    library_entry="bar", sources=["SALES"])
c1, c2 = st.columns(2)
bi.kpi(run, "NET_SALES", container=c1)
bi.chart(run, lambda df: alt.Chart(df).mark_bar().encode(x="REGION:N", y="NET_SALES:Q"))
