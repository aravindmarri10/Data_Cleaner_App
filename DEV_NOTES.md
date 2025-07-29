# Data_Cleaner_App

A Streamlit-based app for basic data cleaning.

This is a beginner-friendly Streamlit app I created while learning data cleaning as part of my AlmaBetter course.

I got curious after seeing some AI-based data cleaning tools, and thought why not try building something of my own. I had no idea where to start, but after learning about Streamlit, I realized I could build a UI easily without HTML or CSS.

I built this app using Python, Streamlit, Pandas, and NumPy, and I slowly kept adding new features to the app.

[Live App - Try it here](https://datacleanerapp-5yhhyr4tjrpffpuycj384b.streamlit.app/)

## App Screenshot

![App Screenshot](demo/Screenshot.png)

## Tech Stack

- Python
- Streamlit
- Pandas
- NumPy

## Features

### Preview
- View top 5 rows
- Column-wise info and data types
- Full statistical summary (numerical and categorical)

### Duplicate Removal
- Detect and remove exact duplicate rows
- Drop selected columns via multi-select

### Null Handling
- Show null percentage column-wise
- Drop rows with nulls (warning if >2% loss)
- Drop columns based on custom null percentage threshold
- Fill numerical columns:
  - Use constant (recommended if null % < 4%)
  - Use median (recommended if null % > 4%)
- Fill categorical columns:
  - Most frequent value
  - Custom user-defined value

### Outlier Detection (v1.2)
- Show outliers using IQR method
- Drop outliers with row-wise removal and loss summary
- Cap outliers to upper/lower bounds

### Type Converter (v1.3)
- Convert to int, float, string, or datetime
- Preview conversion before applying
- Warns if conversion introduces nulls

### Reset and Download
- Reset dataset to original uploaded state
- Download cleaned dataset as CSV

## Version History

### v1.1
- Added intelligent null handling with fill suggestions
- Separate fill strategy for each column
- Warnings based on null severity
- Improved UI and feedback messages

### v1.2
- Added outlier detection and cleaning module
- Options to drop or cap outliers
- Preview and warnings before changes

### v1.3
- Added type conversion feature
- Preview and validation for data loss during conversion

## What I Learned

- How to build dynamic UIs in Streamlit using session state
- Implementing real-time validation and data handling
- Designing safe operations with previews, warnings, and reset options
- Importance of user feedback and experience

## How to Run Locally

1. Install the required libraries:

```bash
pip install streamlit pandas numpy
```

2. **Run the app from your terminal**

```bash
streamlit run your_app_filename.py
```
