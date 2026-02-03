# =========================================================
# SMART ETL ANALYTICS DASHBOARD (FINAL DEPLOYMENT VERSION)
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Smart ETL Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Smart Professional ETL Analytics Dashboard")
st.caption("Clean • Interactive • Recruiter Ready • Auto Smart Visualizations")


# =========================================================
# HELPER FUNCTION (STYLE ALL CHARTS)
# =========================================================
def style_fig(fig, x_title, y_title, theme):
    fig.update_layout(
        template=theme,
        xaxis_title=x_title,
        yaxis_title=y_title,
        font=dict(size=14),
        xaxis_title_font=dict(size=18),
        yaxis_title_font=dict(size=18),
        margin=dict(l=80, r=40, t=60, b=90),
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )
    return fig


# =========================================================
# FILE UPLOADER
# =========================================================
file = st.file_uploader("📂 Upload CSV File", type=["csv"])


# =========================================================
# MAIN APP
# =========================================================
if file:

    # -------------------------
    # EXTRACT
    # -------------------------
    df = pd.read_csv(file)

    st.success("✅ File uploaded successfully")
    st.dataframe(df.head())

    # -------------------------
    # AUTO TYPE DETECTION
    # -------------------------
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    categorical_cols = df.select_dtypes(
        exclude=["number"]
    ).columns.tolist()

    all_cols = df.columns.tolist()

    # -------------------------
    # SIDEBAR CONTROLS
    # -------------------------
    st.sidebar.header("⚙️ Controls")

    date_col = st.sidebar.selectbox("📅 Date Column", all_cols)

    category_col = st.sidebar.selectbox(
        "📂 Category Column",
        ["None"] + categorical_cols
    )

    metric_cols = st.sidebar.multiselect(
        "📈 Metrics",
        numeric_cols,
        default=numeric_cols[:1]
    )

    theme = st.sidebar.selectbox(
        "🎨 Theme",
        ["plotly_dark", "plotly_white", "ggplot2"]
    )

    # -------------------------
    # TRANSFORM (ETL)
    # -------------------------
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])

    start, end = st.sidebar.date_input(
        "📆 Date Range",
        [df[date_col].min(), df[date_col].max()]
    )

    df = df[(df[date_col] >= pd.to_datetime(start)) &
            (df[date_col] <= pd.to_datetime(end))]

    df["Month"] = df[date_col].dt.strftime("%Y-%m")

    # -------------------------
    # KPI SECTION
    # -------------------------
    st.subheader("📌 Key Metrics")

    for metric in metric_cols:

        total = df[metric].sum()
        avg = df[metric].mean()
        mx = df[metric].max()
        mn = df[metric].min()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total", f"{total:,.0f}")
        c2.metric("Average", f"{avg:,.0f}")
        c3.metric("Max", f"{mx:,.0f}")
        c4.metric("Min", f"{mn:,.0f}")

    st.divider()

    # -------------------------
    # VISUALIZATIONS
    # -------------------------
    for metric in metric_cols:

        st.header(f"📊 Analysis → {metric}")

        # ===== Monthly Trend =====
        monthly = df.groupby("Month")[metric].sum().reset_index()

        fig1 = px.line(monthly, x="Month", y=metric, markers=True)
        fig1 = style_fig(fig1, "Month", f"Total {metric}", theme)

        # ===== Distribution =====
        fig2 = px.histogram(df, x=metric, nbins=30)
        fig2 = style_fig(fig2, metric, "Frequency", theme)

        col1, col2 = st.columns(2)
        col1.plotly_chart(fig1, use_container_width=True)
        col2.plotly_chart(fig2, use_container_width=True)

        # ===== Category Distribution =====
        if category_col != "None":

            st.subheader("📂 Top Category Distribution")

            cat_full = (
                df.groupby(category_col)[metric]
                .sum()
                .sort_values(ascending=False)
            )

            top10 = cat_full.head(10)
            others_sum = cat_full[10:].sum()

            if others_sum > 0:
                top10["Others"] = others_sum

            cat = top10.reset_index()
            cat.columns = [category_col, metric]

            fig3 = px.bar(cat, x=category_col, y=metric, text=metric)
            fig3.update_layout(xaxis_tickangle=-45)
            fig3 = style_fig(fig3, category_col, f"Total {metric}", theme)

            fig4 = px.pie(cat, names=category_col, values=metric, hole=0.4)
            fig4.update_layout(template=theme)

            col3, col4 = st.columns(2)
            col3.plotly_chart(fig3, use_container_width=True)
            col4.plotly_chart(fig4, use_container_width=True)

        st.divider()

    # -------------------------
    # CORRELATION HEATMAP
    # -------------------------
    if len(numeric_cols) > 1:

        st.header("🔥 Correlation Heatmap")

        corr = df[numeric_cols].corr()

        fig = ff.create_annotated_heatmap(
            z=corr.values,
            x=list(corr.columns),
            y=list(corr.index),
            showscale=True
        )

        fig.update_layout(template=theme)
        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # DOWNLOAD CLEANED DATA
    # -------------------------
    st.download_button(
        "⬇️ Download Cleaned Data",
        df.to_csv(index=False),
        "cleaned_data.csv"
    )

else:
    st.info("👆 Upload a CSV file to begin analysis")

