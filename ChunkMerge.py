import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import time
import os
from io import BytesIO

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Automation Tool by Faiz",
    layout="wide"
)

# -------------------------------
# SESSION STATE
# -------------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "user_count" not in st.session_state:
    st.session_state.user_count = 1

# -------------------------------
# HEADER
# -------------------------------
st.title("📊 CSV Automation Tool")
st.caption("Efficient filtering, combining, and splitting of large CSV files")

# -------------------------------
# TOP METRICS
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
    else:
        elapsed = 0
    st.metric("⏱ Waiting Time (sec)", elapsed)

with col2:
    st.metric("👤 User Count", st.session_state.user_count)

# -------------------------------
# NOTIFICATION BAR
# -------------------------------
st.info(
    "This tool, created by the Risk Team (SMPL), allows efficient filtering, "
    "combining, and splitting of large CSV files."
)

# -------------------------------
# FILE UPLOAD
# -------------------------------
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.start_time = time.time()
        encodings = ["utf-8", "latin1", "ISO-8859-1"]

        for enc in encodings:
            try:
                st.session_state.df = pd.read_csv(
                    uploaded_file,
                    encoding=enc,
                    on_bad_lines="skip"
                )
                break
            except Exception:
                continue

        if st.session_state.df is not None:
            st.success("CSV file loaded successfully ✅")

# -------------------------------
# DATA INFO
# -------------------------------
if st.session_state.df is not None:
    df = st.session_state.df
    st.write(f"### 📌 Row Count: **{df.shape[0]:,}**")

    # -------------------------------
    # COLUMN SELECTION
    # -------------------------------
    st.subheader("🔍 Select Columns")
    selected_columns = st.multiselect(
        "Choose columns to keep",
        df.columns.tolist()
    )

    if st.button("Generate Filtered File"):
        if selected_columns:
            filtered_df = df[selected_columns]
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ Download Filtered CSV",
                csv,
                file_name="filtered_file.csv",
                mime="text/csv"
            )
        else:
            st.warning("Please select at least one column")

    # -------------------------------
    # ADVANCED FILTER
    # -------------------------------
    st.subheader("🧠 Advanced Column Filter")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        filter_column = st.selectbox("Column", df.columns.tolist())

    with col_b:
        condition = st.selectbox(
            "Condition",
            [">", "<", ">=", "<=", "==", "!=", "contains", "startswith", "endswith", "in"]
        )

    with col_c:
        value = st.text_input("Value")

    if st.button("Apply Advanced Filter"):
        try:
            series = df[filter_column]

            if condition in [">", "<", ">=", "<="]:
                series = pd.to_numeric(series, errors="coerce")
                val = float(value)

                if condition == ">":
                    mask = series > val
                elif condition == "<":
                    mask = series < val
                elif condition == ">=":
                    mask = series >= val
                elif condition == "<=":
                    mask = series <= val

            elif condition == "==":
                mask = series.astype(str) == value
            elif condition == "!=":
                mask = series.astype(str) != value
            elif condition == "contains":
                mask = series.astype(str).str.contains(value, na=False)
            elif condition == "startswith":
                mask = series.astype(str).str.startswith(value, na=False)
            elif condition == "endswith":
                mask = series.astype(str).str.endswith(value, na=False)
            elif condition == "in":
                parts = [v.strip() for v in value.split(",")]
                mask = series.astype(str).isin(parts)

            result_df = df[mask]
            csv = result_df.to_csv(index=False).encode("utf-8")

            st.success(f"Filtered rows: {result_df.shape[0]:,}")
            st.download_button(
                "⬇ Download Filtered Result",
                csv,
                file_name="advanced_filtered.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"Filtering failed: {e}")

    # -------------------------------
    # SPLIT CSV
    # -------------------------------
    st.subheader("✂ Split CSV")
    rows_per_file = st.number_input(
        "Rows per split file",
        min_value=10000,
        value=500000,
        step=10000
    )

    if st.button("Split CSV"):
        chunks = []
        for i in range(0, len(df), rows_per_file):
            chunks.append(df.iloc[i:i + rows_per_file])

        zip_buffer = BytesIO()
        for idx, chunk in enumerate(chunks):
            chunk.to_csv(f"part_{idx+1}.csv", index=False)

        st.success(f"CSV split into {len(chunks)} files")

    # -------------------------------
    # COMBINE CSV
    # -------------------------------
    st.subheader("🧩 Combine CSV Files")
    csv_files = st.file_uploader(
        "Upload multiple CSV files",
        type=["csv"],
        accept_multiple_files=True
    )

    if st.button("Combine CSVs") and csv_files:
        combined = pd.concat(
            [pd.read_csv(f, on_bad_lines="skip", encoding="latin1") for f in csv_files],
            ignore_index=True
        )
        csv = combined.to_csv(index=False).encode("utf-8")

        st.success("CSV files combined successfully")
        st.download_button(
            "⬇ Download Combined CSV",
            csv,
            file_name="combined.csv",
            mime="text/csv"
        )

# -------------------------------
# RESET
# -------------------------------
st.divider()
if st.button("🔄 Reset Application"):
    st.session_state.clear()
    st.success("Application reset successfully")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown(
    "<div style='text-align:center;color:gray;'>Developed by Faiz Khan</div>",
    unsafe_allow_html=True
)
