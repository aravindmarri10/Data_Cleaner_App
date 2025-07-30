import streamlit as st
import pandas as pd
import numpy as np
import io
import seaborn as sns
import matplotlib.pyplot as plt

# ========== Page Config ==========
st.set_page_config(page_title="Cleaner", layout="wide")
st.title("Cleaner - Your data cleaning assistant")

# ========== Load Uploaded CSV ==========
def load_data(file):
    if "file_name" not in st.session_state or st.session_state.file_name != file.name:
        df = pd.read_csv(file)
        st.session_state.df = df
        st.session_state.raw_data = df.copy()
        st.session_state.file_name = file.name
    return st.session_state.df, st.session_state.raw_data

# ========== Preview Section ==========
def preview_data(df):
    st.subheader("Dataset Preview")
    st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
    st.dataframe(df.head())

    st.subheader("Column Types & Info")
    buf = io.StringIO()
    df.info(buf=buf)
    st.text(buf.getvalue())

    st.subheader("Descriptive Statistics")
    st.dataframe(df.describe(include='all').T)
    
# ========== EDA ==========
    
    
def eda(df):
    st.subheader("Exploratory Data Analysis")
    plot = st.sidebar.radio("Show Plots", ['Histogram', 'Box Plot', 'Heat Map'])
    if plot == 'Histogram':
        st.subheader("Histogram")
    

        if st.checkbox("Histogram Viewer"):
            num_cols = df.select_dtypes(include='number').columns.tolist()
            selected = st.multiselect("Select numeric columns", num_cols)
            for col in selected:
                fig, ax = plt.subplots()
                sns.histplot(df[col], kde=True, ax=ax)
                ax.set_title(f"Distribution of {col}")
                st.pyplot(fig)
                
    elif plot  == 'Box Plot':
        st.subheader("Box Plot")
        col = st.selectbox("Select a numeric column", df.select_dtypes(include='number').columns)
        fig, ax = plt.subplots()
        sns.boxplot(x=df[col], ax=ax)
        ax.set_title(f"Boxplot of {col}")
        st.pyplot(fig)
        
    elif plot  == 'Heat Map':
        st.subheader("Heat Map")
        num_df = df.select_dtypes(include='number')
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(num_df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        st.pyplot(fig)

# ========== Handle Duplicates ==========
def remove_duplicates(df):
    st.subheader("Check Duplicates")
    dup = df.duplicated().sum()
    if dup > 0:
        st.warning(f"{dup} duplicate rows found.")
        if st.button("Drop Duplicates"):
            df = df.drop_duplicates(ignore_index=True)
            st.success("Removed duplicate rows.")
            st.session_state.df = df
    else:
        st.info("No duplicates detected.")

def drop_columns(df):
    st.subheader("Drop Columns")
    cols = st.multiselect("Select columns to drop", df.columns.tolist())
    if cols:
        if st.button("Apply Drop"):
            df = df.drop(columns=cols)
            st.success(f"Dropped: {', '.join(cols)}")
            st.session_state.df = df

# ========== Null Handling ==========
def null_handling(df):
    st.subheader("Missing Value Handler")
    sub = st.sidebar.radio("Choose null handling method", 
                           ['Null Summary', 'Drop Rows with Nulls', 
                            'Drop Columns with Nulls', 
                            'Fill Numeric Nulls', 'Fill Categorical Nulls'])

    df.replace(['-', 'n/a', 'N/A', 'missing'], np.nan, inplace=True)
    null_per = (df.isnull().mean() * 100).reset_index()
    null_per.columns = ['Columns', 'null %']
    null_per = null_per[null_per['null %'] > 0]
    

    if sub == 'Null Summary':
        if null_per.empty:
            st.success("No nulls found.")
        else:
            st.dataframe(null_per)

    elif sub == 'Drop Rows with Nulls':
        dropped_df = df.dropna()
        loss = df.shape[0] - dropped_df.shape[0]
        loss_pct = round((loss / df.shape[0]) * 100, 2)
        if loss == 0:
            st.info("No null rows to drop.")
        else:
            st.warning(f"{loss} rows will be removed ({loss_pct}% of data).")
            if st.checkbox("Preview rows to be dropped"):
                st.dataframe(df[~df.index.isin(dropped_df.index)])
            if st.button("Drop Null Rows"):
                st.session_state.df = dropped_df
                st.success("Null rows removed.")
                

    elif sub == 'Drop Columns with Nulls':
            
        threshold = st.slider("Drop columns with nulls above (%)", 0, 100, 80)
        to_drop = null_per[null_per['null %'] > threshold]['Columns'].tolist()
        if to_drop:
            st.warning(f"Will drop columns: {', '.join(to_drop)}")
            if st.button("Drop Columns"):
                df = df.drop(columns=to_drop)
                st.session_state.df = df
                st.success("Columns dropped.")
        else:
            st.info("No columns meet threshold.")

    elif sub == 'Fill Numeric Nulls':
        
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        numeric_nulls = null_per[null_per['Columns'].isin(numeric_cols)].set_index('Columns')['null %'].to_dict()
        if not numeric_nulls:
            st.info("No numerical nulls found.")
            
        else:

            for col in numeric_nulls:
                
                method = st.radio(f"Fill {col}", ['Use constant', 'Use Median'], key=f'num_{col}')
                if method == 'Use Median':
                    if numeric_nulls[col] < 4:
                            st.info(f"{col} has low null %, a constant value may be better than median.")
                    st.session_state[f'{col}_value'] = 'Median'
                else:
                    if numeric_nulls[col] > 4:
                            st.info(f"{col} has higher null %, consider using median.")
                    val = st.number_input(f'Enter value for {col}', key=f'inp_{col}')
                    st.session_state[f'{col}_value'] = val
                    
            if st.button("Apply All Numerical Fills"):
                for col in numeric_nulls:
                    method = st.session_state.get(f'num_{col}')
                    value = st.session_state.get(f'{col}_value')
                    
                    if value == 'Median':
                        med = df[col].median()
                        df[col] = df[col].fillna(med)
                        st.success(f"{col} filled with median {med}")
                    else:
                        df[col] = df[col].fillna(value)
                        st.success(f"{col} filled with constant: {value}")
                        
                st.session_state.df = df

    elif sub == 'Fill Categorical Nulls':
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        cat_nulls = null_per[null_per['Columns'].isin(cat_cols)].set_index('Columns')['null %'].to_dict()
        if not cat_nulls:
            st.info("No categorical nulls found.")
            
        else:

            for col in cat_nulls:
     
                method = st.radio(f"Fill {col}", ['Most Frequent', 'User Input'], key=f'cat_{col}')
                if method == 'Most Frequent':
                    st.session_state[f'{col}_value'] = 'freq'
                else:
                    val = st.text_input(f'Enter value for {col}', key=f'inp_{col}')
                    st.session_state[f'{col}_value'] = val
            
            if st.button("Apply All Categorical Fills"):
                for col in cat_nulls:
                    method = st.session_state.get(f'cat_{col}')
                    value = st.session_state.get(f'{col}_value')

                    if value == 'freq':
                        freq = df[col].value_counts().idxmax()
                        df[col] = df[col].fillna(freq)
                        st.success(f"{col} filled with {freq}")
                    else:
                        df[col] = df[col].fillna(value)
                        st.success(f"{col} filled with constant: {value}")
                
                st.session_state.df = df

# ========== Type Convertor ==========
def type_convertor(df):
    st.subheader("Type Convertor")
    
    cols = df.columns.tolist()
    selected_col = st.selectbox("Select column to convert", cols)
    
    current_dtype = df[selected_col].dtype
    st.write(f"Current dtype of {selected_col}: **{current_dtype}**")
    
    new_type = st.selectbox("Convert to type", ["int", "float", "str", "datetime"])
    
    if st.button("Preview Conversion"):
        try:
            if new_type == "int":
                converted = pd.to_numeric(df[selected_col], errors='coerce').astype("Int64")
            elif new_type == "float":
                converted = pd.to_numeric(df[selected_col], errors='coerce').astype(float)
            elif new_type == "str":
                converted = df[selected_col].astype(str)
            elif new_type == "datetime":
                converted = pd.to_datetime(df[selected_col], errors='coerce')

            nulls_introduced = converted.isna().sum()
            total = df.shape[0]
            percent = round((nulls_introduced / total) * 100, 2)

            if percent > 0:
                st.warning(f"{nulls_introduced} rows ({percent}%) would become NaN after conversion.")
            else:
                st.success("Conversion is safe. No nulls introduced.")
            st.session_state.converted_col = converted
            st.session_state.converted_col_name = selected_col
            st.session_state.new_dtype = new_type
            st.dataframe(converted.head())

        except Exception as e:
            st.error(f"Error in conversion: {e}")
            
    if st.button("Apply Conversion"):
        if (
            "converted_col" in st.session_state and 
            st.session_state.get("converted_col_name") == selected_col
        ):
            df[selected_col] = st.session_state.converted_col
            st.session_state.df = df
            st.success(f"Column {selected_col} converted to {st.session_state.new_dtype}.")
        else:
            st.warning("Please preview conversion before applying.")
    

# ========== Outlier Detection ==========
def outlier_detection(df):
    st.subheader("Outlier Handler")
    mode = st.sidebar.radio("Outlier Option", ['Show Outliers', 'Drop Outliers', 'Capping'])

    num_cols = df.select_dtypes(include='number').columns.tolist()
    summary = []

    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        low = Q1 - 1.5 * IQR
        high = Q3 + 1.5 * IQR
        count = df[(df[col] < low) | (df[col] > high)].shape[0]
        summary.append({'Column': col, 'Outlier Count': count})

    outlier_df = pd.DataFrame(summary)

    if mode == 'Show Outliers':
        if outlier_df['Outlier Count'].sum() == 0:
            st.info("No outliers detected.")
        else:
            st.dataframe(outlier_df)

    elif mode == 'Drop Outliers':
        
        if outlier_df['Outlier Count'].sum() == 0:
            st.info("No outliers detected.")
        else:
            st.warning("""Note: Dropping outliers shifts IQR. Use wisely.
                          New outliers may appear even after this cleaning.""")

            cols = st.multiselect("Select columns for outlier removal", outlier_df[outlier_df['Outlier Count'] > 0]['Column'])
            if cols:
                temp = df.copy()
                rows_before = temp.shape[0]
                for col in cols:
                    Q1 = temp[col].quantile(0.25)
                    Q3 = temp[col].quantile(0.75)
                    IQR = Q3 - Q1
                    low = Q1 - 1.5 * IQR
                    high = Q3 + 1.5 * IQR
                    temp = temp[(temp[col] >= low) & (temp[col] <= high)]
                rows_after = temp.shape[0]
                loss = rows_before - rows_after
                percent_lost = round((loss / rows_before) * 100, 2)
                st.info(f"Will drop {loss} rows ({percent_lost}% of dataset)")
                
                if percent_lost < 5:
                    st.success("Safe to drop. Minimal loss.")
                elif percent_lost > 20:
                    st.warning("High data loss! Consider using capping")
                else:
                    st.info("Moderate data loss. Proceed based on data context.")
                    
                if st.checkbox("Preview rows to be dropped"):
                    dropped = df[~df.index.isin(temp.index)]
                    st.dataframe(dropped)
                if st.button("Confirm Outlier Removal"):
                    st.session_state.df = temp
                    st.success("Outliers removed.")
                    
    elif mode == 'Capping':
        
        if outlier_df['Outlier Count'].sum() == 0:
            st.info("No outliers detected.")
        else:
            cols = st.multiselect("Select columns for outlier removal", outlier_df[outlier_df['Outlier Count'] > 0]['Column'])
            temp = df.copy()
            for col in cols:
                Q1 = temp[col].quantile(0.25)
                Q3 = temp[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                
                temp[col] = np.where(temp[col] < lower, lower, temp[col])
                temp[col] = np.where(temp[col] > upper, upper, temp[col])
                
            if st.checkbox("Show capped rows"):
                changed_rows = df[cols] != temp[cols]
                affected = df[changed_rows.any(axis=1)]
                st.write(f"{affected.shape[0]} rows had outlier values capped.")
                st.dataframe(affected)

            
            if st.button("Confirm Outlier Capping"):
                st.session_state.df = temp
                st.success("Outliers Capped.")
        

# ========== Reset & Download ==========
def reset_data(original):
    st.subheader("Reset to Original")
    if st.button("Reset"):
        st.session_state.df = original.copy()
        st.success("Reset complete.")

def download_data(df):
    st.download_button("Download Cleaned CSV", df.to_csv(index=False), file_name="cleaned_data.csv")

# ========== Main App ==========
file = st.file_uploader("Upload your CSV file", type=['csv'])

if file:
    df, original = load_data(file)

    tab = st.sidebar.radio("What do you want to do?", 
                           ["Preview", "EDA", "Duplicate Handling", "Null Handling", "Outlier Detection", "Type Convertor", "Reset Data"])

    if tab == "Preview":
        preview_data(df)
    elif tab == "EDA":
        eda(df)
    elif tab == "Duplicate Handling":
        action = st.sidebar.radio("Pick Task", ["Remove Duplicates", "Drop Columns"])
        if action == "Remove Duplicates":
            remove_duplicates(df)
        else:
            drop_columns(df)
    elif tab == "Null Handling":
        null_handling(df)
    elif tab == "Outlier Detection":
        outlier_detection(df)
    elif tab == "Type Convertor":
        type_convertor(df)
    elif tab == "Reset Data":
        reset_data(original)

    st.markdown("---")
    download_data(st.session_state.df)
st.sidebar.markdown("**Developed by Aravind**")
