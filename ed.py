import streamlit as st
import pandas as pd
import numpy as np
import io

# ------------------- Page Setup -------------------
st.set_page_config(page_title="Cleaner", layout="wide")
st.title("Cleaner - Your data cleaning assistant")

# ------------------- Utility Functions -------------------

# ------------------- Load Data -------------------

def load_data(file):
    """Load and cache uploaded file"""
    if "file_name" not in st.session_state or st.session_state.file_name != file.name:
        st.session_state.df = pd.read_csv(file)
        st.session_state.raw_data = st.session_state.df.copy()
        st.session_state.file_name = file.name
    return st.session_state.df, st.session_state.raw_data
# ------------------- Preview -------------------
def preview_data(df):
    """Display basic information about the data"""
    st.subheader('Dataset Preview')
    st.info(f'The dataset has {df.shape[0]} rows and {df.shape[1]} columns')
    st.dataframe(df.head())

    st.subheader('Data Info')
    buffer = io.StringIO()
    df.info(buf=buffer)
    st.text(buffer.getvalue())

    st.subheader('Statistical Summary')
    st.dataframe(df.describe(include='all').T)
# ------------------- Duplicate Handler -------------------
def remove_duplicates(df):
    """Remove duplicate rows"""
    st.subheader('Duplicate Checker')
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        st.warning(f'{dup_count} duplicate rows found')
        if st.button('Remove Duplicates'):
            df = df.drop_duplicates(ignore_index=True)
            st.success('Duplicates removed')
            st.session_state.df = df
    else:
        st.info('No Duplicates found')

def drop_columns(df):
    """Allow user to drop specific columns"""
    st.subheader('Drop Columns')
    columns = st.multiselect("**Select columns to drop**", df.columns)
    if columns:
        if st.button('Drop'):
            df = df.drop(columns=columns)
            st.session_state.df = df
            st.success(f"Columns dropped: {', '.join(columns)}")
    else:
        st.info("Please select at least one column to drop.")
# ------------------- Null Handling -------------------
def null_handling(df):
    """Handle nulls in dataset"""
    sub_option = st.sidebar.radio('Null Handling Options', (
        'Null percentage', 'Drop Rows(Null)', 'Drop Columns(Null)', 'Fill Numerical Null', 'Fill Categorical Null'))

    df.replace(['-', 'n/a', 'N/A', 'missing'], np.nan, inplace=True)
    null_per = (df.isnull().mean() * 100).reset_index()
    null_per.columns = ['Columns', 'null %']
    null_per = null_per[null_per['null %'] > 0]

    if sub_option == 'Null percentage':
        st.subheader('Null Percentages')
        if null_per.empty:
            st.info('Hurray No Null Columns')
        else:
            st.dataframe(null_per)

    elif sub_option == 'Drop Rows(Null)':
        st.subheader('Null Rows Drop')
        drop_row = df.dropna()
        rows_loss = df.shape[0] - df.dropna().shape[0]
        if rows_loss == 0:
            st.info('No Null Rows')
        else:
            st.warning('Drop only if loss percent is less than 2%, otherwise can lead to data lose')
            percent_loss = round((rows_loss / df.shape[0]) * 100, 1)
            st.info(f"Dropping rows will lose {rows_loss} rows and lose percent is ({percent_loss}%)")
            show_dropped = st.checkbox("Show rows that will be dropped")
            if show_dropped:
                dropped_rows = df.loc[~df.index.isin(drop_row.index)]
                st.dataframe(dropped_rows)
            if st.button('Drop Rows'):
                df = df.dropna()
                st.session_state.df = df
                st.success(f"{rows_loss} rows dropped")

    elif sub_option == 'Drop Columns(Null)':
        st.subheader('Null Columns Drop')
        st.warning(f'All columns with null percent greater than percent will be dropped, Default is 80')
        val = st.number_input(f'Enter the percent',min_value=0, max_value=100, value=80)
        high_null_cols = null_per[null_per['null %'] > val]
        if not high_null_cols.empty:
            st.warning(f"Columns dropped will be : {','.join(high_null_cols['Columns'].tolist())}")
        
        if st.button('Drop Columns'):
            if high_null_cols.empty:
                st.info('No high-null columns to drop')
            else:
                df = df.drop(columns=high_null_cols['Columns'])
                st.session_state.df = df
                st.success(f"{','.join(high_null_cols['Columns'].tolist())} columns dropped")

    elif sub_option == 'Fill Numerical Null':
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
                

    elif sub_option == 'Fill Categorical Null':
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
                
def outlier_detection(df):
    sub_option = st.sidebar.radio('Outlier Detection', (
        'Outlier Count', 'Outlier Drop'))

    numeric_cols = df.select_dtypes(include=['number'])
    outlier_summary = []

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]
        outlier_summary.append({
            "Column": col,
            "Outlier Count": outliers.shape[0]
        })

    outlier_df = pd.DataFrame(outlier_summary)

    if sub_option == 'Outlier Count':
        st.header('Outlier Detection (IQR Method)')
        st.dataframe(outlier_df)

    elif sub_option == 'Outlier Drop':
        st.header('Drop Outliers (Single Pass)')
        outlier_df = outlier_df[outlier_df['Outlier Count'] > 0]

        if outlier_df.empty:
            st.info("No outliers detected.")
        else:
            st.dataframe(outlier_df)

        columns_selected = st.multiselect("Select columns to remove outliers from", outlier_df["Column"])

        if columns_selected:
            
            temp_df = df.copy()
            original_rows = temp_df.shape[0]
            for col in columns_selected:
                Q1 = temp_df[col].quantile(0.25)
                Q3 = temp_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                temp_df = temp_df[(temp_df[col] >= lower) & (temp_df[col] <= upper)]
                
            new_rows = temp_df.shape[0]
            rows_dropped = original_rows - new_rows
            percent_lost = round((rows_dropped / original_rows) * 100, 2)
            
            if rows_dropped == 0:
                st.info("No rows will be dropped from this operation.")
            else:
                st.info(f"⚠️ This will drop **{rows_dropped} rows ({percent_lost}%)** from the dataset.")
                if percent_lost < 5:
                    st.success("✅ Safe to drop. Minimal loss.")
                elif percent_lost > 20:
                    st.warning("⚠️ High data loss! Consider using capping or transformation instead.")
                else:
                    st.info("ℹ️ Moderate data loss. Proceed based on data context.")
                    
            show_dropped = st.checkbox("Show rows that will be dropped")
            if show_dropped:
                dropped_rows = df.loc[~df.index.isin(temp_df.index)]
                st.dataframe(dropped_rows)
            
            if st.button("Remove Outlier Rows from Selected Columns"):
                df = temp_df
                st.session_state.df = df
                st.success(f"Outlier rows removed for: {', '.join(columns_selected)}")
                st.warning(
                "New outliers may appear even after this cleaning. "
                "Removing extreme values shifts IQR boundaries. Avoid repeated removal unless justified."
                )


def reset_data(raw_data):
    """Reset data to original uploaded version"""
    st.subheader('Reset Data')
    st.warning('All changes will be revoked')
    if st.button('Confirm for Data Reset'):
        st.info(f"The original data has {raw_data.shape[0]} rows and {raw_data.shape[1]} columns")
        st.session_state.df = raw_data.copy()
        st.success("Dataset has been reset to original")

def download_data(df):
    """Download the cleaned dataset"""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label='Download Cleaned CSV', data=csv, file_name='clean.csv')

# ------------------- Main Flow -------------------

file = st.file_uploader("Upload a CSV file", type=["csv"])

if file:
    df, raw_data = load_data(file)

    option = st.sidebar.radio("Choose an operation", 
                              ['Preview', 'Duplicate Removal', 'Null Handling', 'Outlier Detection', 'Reset Data'])

    if option == 'Preview':
        preview_data(df)

    elif option == 'Duplicate Removal':
        task = st.sidebar.radio('Choose', ['Duplicate Rows Removal', 'Drop Columns'])
        if task == 'Duplicate Rows Removal':
            remove_duplicates(df)
        else:
            drop_columns(df)

    elif option == 'Null Handling':
        null_handling(df)

    elif option == 'Reset Data':
        reset_data(raw_data)
        
    elif option == 'Outlier Detection':
        outlier_detection(df)

    st.markdown("---")
