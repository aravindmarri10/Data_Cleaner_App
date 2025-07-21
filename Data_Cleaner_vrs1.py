import streamlit as st
import pandas as pd
import numpy as np
import io

# ------------------- Page Setup -------------------
st.set_page_config(page_title="Cleaner", layout="wide")
st.title("Cleaner - Your data cleaning assistant")

# ------------------- Utility Functions -------------------

def load_data(file):
    """Load and cache uploaded file"""
    if "file_name" not in st.session_state or st.session_state.file_name != file.name:
        st.session_state.df = pd.read_csv(file)
        st.session_state.raw_data = st.session_state.df.copy()
        st.session_state.file_name = file.name
    return st.session_state.df, st.session_state.raw_data

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
    columns = st.multiselect("Select columns to drop", df.columns)
    if columns:
        if st.button('Drop'):
            df = df.drop(columns=columns)
            st.session_state.df = df
            st.success(f"Columns dropped: {', '.join(columns)}")

def null_handling(df):
    """Handle nulls in dataset"""
    sub_option = st.sidebar.radio('Null Handling Options', (
        'Null percentage', 'Drop Rows(Null)', 'Drop Null Columns', 'Fill Numerical Null', 'Fill Categorical Null'))

    df.replace(['-', 'n/a', 'N/A', 'missing'], np.nan, inplace=True)
    null_per = (df.isnull().mean() * 100).reset_index()
    null_per.columns = ['Columns', 'null %']
    null_per = null_per[null_per['null %'] > 0]

    if sub_option == 'Null percentage':
        st.subheader('Null Percentages')
        if null_per.empty:
            st.info('No Null Columns')
        else:
            st.dataframe(null_per)

    elif sub_option == 'Drop Rows(Null)':
        rows_loss = df.shape[0] - df.dropna().shape[0]
        percent_loss = round((rows_loss / df.shape[0]) * 100, 1)
        st.info(f"Dropping rows will lose {rows_loss} rows ({percent_loss}%)")
        if st.button('Drop Rows'):
            df = df.dropna()
            st.session_state.df = df
            st.success(f"{rows_loss} rows dropped")

    elif sub_option == 'Drop Null Columns':
        high_null_cols = null_per[null_per['null %'] > 80]
        if high_null_cols.empty:
            st.info('No high-null columns to drop')
        else:
            st.warning(f"Dropping: {high_null_cols['Columns'].tolist()}")
            df = df.drop(columns=high_null_cols['Columns'])
            st.session_state.df = df
            st.success(f"{len(high_null_cols)} columns dropped")

    elif sub_option == 'Fill Numerical Null':
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        numeric_nulls = null_per[null_per['Columns'].isin(numeric_cols)].set_index('Columns')['null %'].to_dict()
        if not numeric_nulls:
            st.info("No numerical nulls found.")

        for col in numeric_nulls:
            fill_option = st.radio(f"Fill {col}", ['Use constant', 'Use Median'], key=col)
            if fill_option == 'Use constant':
                val = st.number_input(f'Enter value for {col}', key=f'in_{col}')
                if st.button('Fill', key=f'but_{col}_const'):
                    df[col] = df[col].fillna(val)
                    st.success(f"{col} filled with {val}")
                    st.session_state.df = df
            else:
                if st.button('Fill', key=f'but_{col}_median'):
                    med = df[col].median()
                    df[col] = df[col].fillna(med)
                    st.success(f"{col} filled with median {med}")
                    st.session_state.df = df

    elif sub_option == 'Fill Categorical Null':
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        cat_nulls = null_per[null_per['Columns'].isin(cat_cols)].set_index('Columns')['null %'].to_dict()
        if not cat_nulls:
            st.info("No categorical nulls found.")

        for col in cat_nulls:
            method = st.radio(f"Fill {col}", ['Most Frequent', 'User Input'], key=f'cat_{col}')
            if method == 'Most Frequent':
                if st.button('Fill', key=f'but_{col}_freq'):
                    freq = df[col].value_counts().idxmax()
                    df[col] = df[col].fillna(freq)
                    st.success(f"{col} filled with most frequent: {freq}")
                    st.session_state.df = df
            else:
                val = st.text_input(f'Enter value for {col}', key=f'inp_{col}')
                if st.button('Fill', key=f'but_{col}_user'):
                    df[col] = df[col].fillna(val)
                    st.success(f"{col} filled with: {val}")
                    st.session_state.df = df

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
                              ['Preview', 'Duplicate Removal', 'Null Handling', 'Reset Data'])

    if option == 'Preview':
        preview_data(df)

    elif option == 'Duplicate Removal':
        task = st.sidebar.radio('Choose', ['Rows Duplicate Removal', 'Drop Columns'])
        if task == 'Rows Duplicate Removal':
            remove_duplicates(df)
        else:
            drop_columns(df)

    elif option == 'Null Handling':
        null_handling(df)

    elif option == 'Reset Data':
        reset_data(raw_data)

    st.markdown("---")
    download_data(st.session_state.df)
