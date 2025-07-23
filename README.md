# Data_Cleaner_App
Streamlit-based app for basic data cleaning

# Cleaner - Data Cleaning Assistant

This is a beginner-friendly Streamlit app I created while learning data cleaning as part of my AlmaBetter course.

I got curious after seeing some AI-based data cleaning tools, and thought why not try building something of my own. I had no idea where to start, but after learning about Streamlit, I realized I could build a UI easily without HTML or CSS.

I built this app using Python, Streamlit, Pandas, and NumPy. ChatGPT helped me understand Streamlit components one by one, and I slowly kept adding new features to the app.


 **Live App:** [Click here to try it out](https://datacleanerapp-5yhhyr4tjrpffpuycj384b.streamlit.app/)


## Features

- **Preview**
  - View top 5 rows
  - Column-wise info and data types
  - Full statistical summary (numerical + categorical)

- **Duplicate Removal**
  - Detect and remove exact duplicate rows
  - Drop selected columns via multi-select

- **Null Handling**
  - Show null percentage column-wise
  - Drop rows with nulls (warning if >2% loss)
  - Drop columns based on custom null % threshold
  - Fill numerical columns
    - Use constant (recommended if null % < 4%)
    - Use median (recommended if null % > 4%)
  - Fill categorical columns
    - Most frequent value
    - Custom user value

- **Reset**
  - Restore dataset to original uploaded state

- **Download**
  - Download cleaned dataset as CSV

---

##  Version 1.1 Updates

- Added intelligent null handling with suggestions based on null percentage
- Each numeric and categorical null column now gets its own fill strategy
- Categorical columns can now be filled using most frequent or user-entered value
- Warnings and recommendations based on null severity (%)
- Option to drop high-null columns with custom threshold (default 80%)
- Consistent use of Streamlit feedback messages (info, warning, success)
- Download cleaned dataset at any time
- Better layout, section headers, and overall UI experience

##  Version 1.2 Updates
-Major Additions:
 Outlier Detection Module added under sidebar tab:
 - Show Outliers (IQR method)
 - Drop Outliers (row-wise removal with loss summary)
 - Capping Outliers (replace with lower/upper bounds)
 - Includes safety checks and preview options for data loss.


## How to Run

1. **Install required libraries**  
Make sure Python is installed, then install the required packages:

```bash
pip install streamlit pandas numpy
```

2. **Run the app from your terminal**

```bash
streamlit run your_app_filename.py
```

