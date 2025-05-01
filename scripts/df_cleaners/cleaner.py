import pandas as pd
import re
from datetime import datetime
import dateutil.parser



# Helper functions
def robust_parse_date(date_str):
    """
    Attempt to parse date_str using several candidate formats.
    If none of the formats work, fall back to dateutil.parser with dayfirst=True.
    Returns a datetime object or pd.NaT if parsing fails.
    """
    if pd.isna(date_str) or str(date_str).strip() == "":
        return pd.NaT

    # List of candidate formats to try explicitly.
    # Adjust or add formats as needed.
    formats = [
        '%a %b %d %Y %H:%M:%S GMT%z (%Z)',  # e.g., "Tue May 07 2024 00:00:00 GMT-0700 (Pacific Daylight Time)"
        '%d/%m/%Y',                         # e.g., "17/07/2024"
        '%Y-%m-%d'                          # e.g., "2024-07-17" (ISO)
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except Exception:
            continue

    # Fallback: try dateutil's parser (with dayfirst=True to handle dd/mm/yyyy cases)
    try:
        return dateutil.parser.parse(date_str, dayfirst=True)
    except Exception:
        return pd.NaT

def format_dates(df, date_cols):
    """Parses and standardizes date columns in YYYY-MM-DD format."""
    for col in date_cols:
        if col in df.columns:
            df[col] = df[col].apply(robust_parse_date).dt.strftime("%Y-%m-%d")
    return df

def standardize_column_names(df):
    """Standardizes column names by replacing spaces, slashes, dashes, and trailing dots."""
    df.columns = (
        df.columns.str.replace(" ", "_")
                  .str.replace("/", "_")
                  .str.replace("-", "_")
                  .str.replace(r'\.$', '', regex=True)
    )
    return df

def clean_dataframe(df, drop_last_row=False, drop_first_col=False, filter_col=None, filter_values=None):
    """Cleans dataframe by dropping empty/unnamed columns, removing unwanted rows, and optionally dropping first column or last row."""
    
    # ✅ Drop completely empty and unnamed columns
    df.dropna(axis=1, how="all", inplace=True)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    
    # ✅ Drop specific rows based on column values
    if filter_col and filter_values:
        df = df[~df[filter_col].isin(filter_values)]
    
    # ✅ Drop last row if requested
    if drop_last_row and len(df) > 1:
        df = df.iloc[:-1]

    # ✅ Drop first column if requested
    if drop_first_col:
        df = df.iloc[:, 1:]

    return df.reset_index(drop=True)

def clean_filename(file_name):
    file_name = re.sub(r"\s*\(\d+\)", "", file_name)  # Remove (2), (copy)
    file_name = re.sub(r"[^\w\s_.-]", "", file_name)  # Remove special characters
    return file_name.replace(" ", "_").lower()



# Item wise customer report
def modify_sales_report_dataframe(df):
    print("🛠 Modifying Sales Report...")
    
    # Drop columns where the first row has blanks
    df = df.dropna(axis=1, how='all')

    # Drop unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Drop rows where the 'Date' column has the value "Total"
    df = df[df["Date"] != "Total"]

    # Assign Item Code
    # When the first column is not null, assign the corresponding value in the second column as the Item Code
    df["Item Code"] = df.iloc[:, 1].where(df.iloc[:, 0].notna())

    # Forward fill Item Code
    df["Item Code"] = df["Item Code"].ffill()


    # Assign Item Color
    # When the first column is not null, assign the corresponding value in the third column as the Item Color
    df["Item Color"] = df.iloc[:, 2].where(df.iloc[:, 0].notna())

    # Forward fill Item Color only if it's not blank
    df["Item Color"] = df["Item Color"].ffill() 

    # Ensure relevant item codes and item colors are repeated for all associated records
    df = df.loc[df["Item Code"].notna()].copy()

    # Drop rows where 'Date' column has value 'Size' or 'Total' column is blank
    df = df[(df["Date"] != "Size") & df["Total"].notna()]

    # Drop 'Size Group' column
    if "Size Group" in df.columns:
        df.drop(columns=["Size Group"], inplace=True)

    # df["Date"] = pd.to_datetime(df["Date"], errors='coerce').dt.strftime('%Y-%m-%d')

    # Apply the robust parser function to your "Date" column
    df["Date"] = df["Date"].apply(robust_parse_date)

    # Convert to standardized string format YYYY-MM-DD
    df["Date"] = df["Date"].dt.strftime('%Y-%m-%d')

    # Drop rows where 'Date' column has value 'Total'
    df = df[df["Date"] != "Total"]

    # Drop rows where 'Order No' is blank
    df = df[df["Order No"].notna()]

    # Remove the first column
    df = df.iloc[:, 1:]

    # ✅ Replace spaces and "/" in column names with underscores
    df = standardize_column_names(df)

    # Reset index
    df.reset_index(drop=True, inplace=True)
    
    return df

def modify_order_dataframe(df):
    print("🛠 Modifying Sales Pending Order Dataframe...")

    df = standardize_column_names(df)

    # ✅ Define required columns after normalizing column names
    required_columns = [
        "Customer_Name", "Item_Code", "Item_Name", "Color_Name_Code", 
        "Total", "SO_No", "SO_Date", "Broker"
    ]

    # ✅ Check if all required columns exist
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"⚠️ Missing Columns: {missing_cols}")
        print(f"⚠️ All Columns: {df.columns.tolist()}")
        return None  # Prevent failure by returning None

    # ✅ Select only required columns
    df = df[required_columns]

    # ✅ Drop rows where 'so_no' is blank or NaN
    df = df[df["SO_No"].notna() & (df["SO_No"].astype(str).str.strip() != "")]

    # ✅ Convert 'SO Date' to proper datetime format
    df["SO_Date"] = pd.to_datetime(df["SO_Date"], format="%d/%m/%Y", errors='coerce')

    # ✅ Reset index
    df.reset_index(drop=True, inplace=True)

    # Convert all data to string
    df = df.astype(str)
    df.reset_index(drop=True, inplace=True)
    
    return df

def modify_stock_dataframe(df):
    print("🛠 Modifying Inventory Stock Report...")

    df = standardize_column_names(df)

    # ✅ Remove rows where "Item" contains "Grand Total"
    if "Item" in df.columns:
        df = df.loc[~df["Item"].str.contains("Grand Total", case=False, na=False)]
    
    # ✅ Convert all data to string
    df = df.astype(str)
    df.reset_index(drop=True, inplace=True)

    return df

def modify_sales_invoice_dataframe(df):
    print("🛠 Modifying Sales Invoice Data...")

    # ✅ Replace spaces and "/" in column names with underscores
    df = standardize_column_names(df)

    # ✅ Drop columns where the header is blank
    df = df.loc[:, df.columns.str.strip() != ""]

    # ✅ Drop the last row
    df = df.iloc[:-1]


    # ✅ Convert all data to string
    df = df.astype(str)
    df.reset_index(drop=True, inplace=True)

    return df

def modify_pending_po(df):
    print("🛠 Modifying Pending Purchase Order Report...")
    
    # Rename the first column to "Customer Name"
    df.rename(columns={df.columns[0]: "Vendor Name"}, inplace=True)
    
    # Function to fill down only non-numeric customer names
    def fill_down_non_numeric(df, column):
        last_value = None
        for index, row in df.iterrows():
            if pd.notna(row[column]) and not str(row[column]).isdigit():
                last_value = row[column]
            elif last_value is not None and (pd.isna(row[column]) or str(row[column]).isdigit()):
                df.at[index, column] = last_value
        return df
    
    # Apply fill down logic
    df = fill_down_non_numeric(df, "Vendor Name")
    
    # Drop rows where "Item Name" is blank
    df = df.dropna(subset=["Item Name"])

    df = standardize_column_names(df)

    # Convert all data to string
    df = df.astype(str)
    df.reset_index(drop=True, inplace=True)
    
    return df

def modify_valuation_dataframe(df):
    print("🛠 Modifying Stock Valuation Report...")

    # Replace spaces and "/" in column names with underscores.
    df = standardize_column_names(df)


    # Drop the last row
    df = df.iloc[:-1]

    # Convert all data to string.
    df = df.astype(str)
    df.reset_index(drop=True, inplace=True)
    return df

def modify_sales_order_dataframe(df):
    print("🛠 Modifying Sales Order Report...")

    # Replace spaces and "/" in column names with underscores.
    df.columns = df.columns.str.replace(" ", "_").str.replace("/", "_").str.replace("#", "column_n").str.replace("[", "").str.replace("]", "")


    # Drop the last row
    df = df.iloc[:-1]

    # Convert all data to string.
    df = df.astype(str)
    df.reset_index(drop=True, inplace=True)
    return df

def modify_broker_dataframe(df):
    print("🛠 Modifying Broker Data...")

    # Standardize column names.
    df.columns = (
    df.columns
      .str.replace(" ", "_")    # Replace spaces with underscores
      .str.replace("/", "_")    # Replace slashes
      .str.replace("-", "_")    # Replace dashes
      .str.replace(r'\.$', '', regex=True)  # Remove trailing periods (like 'Design_No.')
        )

    # Drop any completely empty columns.
    df.dropna(axis=1, how="all", inplace=True)

    # Remove rows where all values are NaN.
    df.dropna(axis=0, how="all", inplace=True)

    # Convert all data to string.
    df = df.astype(str)

    # Reset index.
    df.reset_index(drop=True, inplace=True)

    return df

def modify_customer_dataframe(df):
    print("🛠 Modifying Customer Data...")
    
    # Select required columns
    df_extracted = df[[
        "Company Name", "Cust/Ved Type", "Area", "City", "State", "Outstanding", "Broker", "Contact Name", "Number"
    ]].copy()
    
    # Replace "/" with "_" and " " with "_"
    df_extracted.columns = df_extracted.columns.str.replace("/", "_").str.replace(" ", "_")

    # Find the actual column name case-insensitively
    col_name = next((col for col in df.columns if col.lower() == "contact_name"), None)

    if col_name:
        df[col_name] = df[col_name].str.strip()

        # Replace variations of "NA NA", "na na", ". .", and "UNKNOWN JI" (case-insensitive) with blank
        df[col_name] = df[col_name].replace(r'(?i)^(NA NA|na na|\. \.|UNKNOWN JI|ACC JI)$', '', regex=True)

        # Remove trailing and leading dots, spaces, and multiple dot spaces
        df[col_name] = df[col_name].str.replace(r'^[\s.]+|[\s.]+$', '', regex=True)

        # Remove any standalone single dots or spaces
        df[col_name] = df[col_name].replace(r'^\.$', '', regex=True)

    # The DataFrame df is now cleaned


    
    # Extract numeric values from Outstanding and create a Type column
    df_extracted["Type"] = df_extracted["Outstanding"].str.extract(r"(Cr|Dr)$")  # Extract "Cr" or "Dr"
    df_extracted["Type"] = df_extracted["Type"].map({"Cr": "Credit", "Dr": "Debit"})  # Map to full words
    
    # Remove "Cr" or "Dr" from Outstanding and convert to float
    df_extracted["Outstanding"] = df_extracted["Outstanding"].str.replace(r"[^\d.]", "", regex=True).astype(float)
    
    # Ensure "Number" is stored as a string and remove ".0"
    df_extracted["Number"] = df_extracted["Number"].astype(str).str.replace(r"\.0$", "", regex=True)
    
    # Reorder columns to keep "Type" immediately after "Outstanding"
    df_extracted = df_extracted[[
        "Company_Name", "Cust_Ved_Type", "Area", "City", "State", "Outstanding", "Type", "Broker", "Contact_Name", "Number"
    ]]
    
    return df_extracted

def modify_gr_report(df):
    print("🛠 Modifying GR Report...")
    

    # Step 6: Trim all columns
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
     # Step 11: Convert all string values to uppercase
    df = df.map(lambda x: x.upper() if isinstance(x, str) else x)
    
    # Step 1: Remove completely empty rows
    df_cleaned = df.dropna(how='all')

    # Step 2: Remove rows where "CN Number" or "Customer Name" contains "Total"
    df_cleaned = df_cleaned[~df_cleaned['CN Number'].astype(str).str.contains('Total', na=False)]
    df_cleaned = df_cleaned[~df_cleaned['Customer Name'].astype(str).str.contains('Total', na=False)]

    # Step 3: Standardize Date Format in "CN Date"
    df_cleaned['CN Date'] = pd.to_datetime(df_cleaned['CN Date'], errors='coerce', dayfirst=True)

    # Step 4: Ensure "Qty" and "Amount" are numeric
    df_cleaned['Qty'] = pd.to_numeric(df_cleaned['Qty'], errors='coerce')
    df_cleaned['Amount'] = pd.to_numeric(df_cleaned['Amount'], errors='coerce')

    # Step 5: Keep only the part before the first comma in "Customer Name"
    df_cleaned['Customer Name'] = df_cleaned['Customer Name'].astype(str).str.split(',').str[0]

    df = df_cleaned
    # Step 8: Extract only the value after "CN/" in "CN Number" into a new column "Invoice No"
    # df["Invoice No"] = df["CN Number"].str.extract(r'CN/(.*)')
    
    df["Invoice No"] = df["CN Number"].str.extract(r'CN/([\d-]+/\d+)').fillna(df["CN Number"])
    # Step 9: Clean column names
    df.columns = df.columns.str.replace(r'\.$', '', regex=True)  # Remove trailing dots
    df.columns = df.columns.str.replace(r'[ .]', '_', regex=True)  # Replace spaces and non-trailing dots with underscores
    df.columns = df.columns.str.lower()  # Convert all column names to lowercase
    
    df.columns = df.columns.str.lower()
    
    # Step 13: Replace blank values in "reason" column with "NOT MENTIONED"
    df["reason"] = df["reason"].replace("", "NOT MENTIONED").fillna("NOT MENTIONED")
    

    # Step 6: Reset Index
    df.reset_index(drop=True, inplace=True)
    
    return df

def modify_purchase_invoice_dataframe(df):
    print("🛠 Modifying Purchase Invoice Report...")

    # ✅ Replace spaces and "/" in column names with underscores
    df.columns = df.columns.str.replace(" ", "_").str.replace("/", "_")

    # ✅ Drop columns where the header is blank
    df = df.loc[:, df.columns.str.strip() != ""]

    # Clean rows where 'Date' is NaN or empty string
    if "Date" in df.columns:
        # Drop rows where 'Date' is either NaN or empty string
        df = df[~(df['Date'].isna() | (df['Date'].astype(str).str.strip() == ''))]
    else:
        raise ValueError("The 'Date' column does not exist in the provided file.")

    # ✅ Convert all data to string
    df = df.astype(str)
    df.reset_index(drop=True, inplace=True)

    return df

def modify_account_payable_dataframe(df):
    print("🛠 Modifying Account Payable Report...")

    # ✅ Replace spaces and "/" in column names with underscores
    df = standardize_column_names(df)

    # ✅ Drop columns where the header is blank
    df = df.loc[:, df.columns.str.strip() != ""]

    # ✅ Drop columns whose header contains '--Select--Udyam'
    df = df.loc[:, ~df.columns.str.contains('__Select__Udyam')]

    # ✅ Drop the first column
    df = df.iloc[:, 1:]

    if "Vendor_Name" in df.columns:
        df = df[~(df['Vendor_Name'].isna() | (df['Vendor_Name'].astype(str).str.strip() == ''))]
    else:
        raise ValueError("The 'Vendor Name' column does not exist in the provided file.")

    # ✅ Convert all data to string
    df = df.astype(str)

    # ✅ Reset index
    df.reset_index(drop=True, inplace=True)

    return df

def modify_account_receivable_dataframe(df):
    print("🛠 Modifying Account Receivable Report...")

    # ✅ Standardize column names (replace spaces, / etc.)
    df = standardize_column_names(df)

    # Create an empty list to hold customer names
    customer_names = []
    current_customer = None

    # Loop through each row to detect and assign customer name
    for idx, row in df.iterrows():
        if pd.notna(row.iloc[0]) and row.iloc[1:].isnull().all():
            current_customer = row.iloc[0]
        customer_names.append(current_customer)

    # Add the new "customer_name" column
    df['customer_name'] = customer_names

    # Remove rows which are only customer titles or 'Total'
    df = df[~((df.iloc[:, 1:].isnull()).all(axis=1))]
    df = df[df.iloc[:, 0] != 'Total']

    # Drop unwanted columns
    if 'Unnamed:_1' in df.columns:
        df = df.drop(columns=['Unnamed:_1'])

    # Drop rows where Total_Amt is blank or null
    if 'Total_Amt' in df.columns:
        df = df[df['Total_Amt'].notna()]

    # Drop rows where Date == "Grand Total"
    if 'Date' in df.columns:
        df = df[df['Date'] != 'Grand Total']

    # Reorder columns (customer_name first)
    cols = ['customer_name'] + [col for col in df.columns if col != 'customer_name']
    df = df[cols]
    
    # Clean customer_name to remove anything starting from '['
    df['customer_name'] = df['customer_name'].apply(lambda x: re.split(r'\[', str(x))[0].strip())


    return df



def robust_date_parse(x, fallback_date=None):
    """
    Attempts to parse a date string using several common formats.
    If x is missing (NaN, empty, or a variant of 'nan'), returns fallback_date if provided,
    otherwise returns pd.NaT.
    """
    # Check for missing/empty values.
    if pd.isna(x) or str(x).strip() in ["", "nan", "NaN", "NAN"]:
        return fallback_date if fallback_date is not None else pd.NaT

    # List of possible date formats to try.
    possible_formats = [
        '%d-%m-%Y',
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%Y/%m/%d'
    ]
    
    for fmt in possible_formats:
        try:
            return pd.to_datetime(x, format=fmt)
        except Exception:
            continue

    # Fallback: try a generic parse with dayfirst=True.
    try:
        return pd.to_datetime(x, dayfirst=True, errors='coerce')
    except Exception:
        return fallback_date if fallback_date is not None else pd.NaT

def modify_jobcard_dataframe(df):
    print("🛠 Modifying Vastra Production Report...")

    # 1. Clean column names: replace spaces and "/" with underscores.
    # df.columns = df.columns.str.replace(" ", "_").str.replace("/", "_")
    
    df.columns = (
    df.columns
      .str.replace(" ", "_")
      .str.replace("/", "_")
      .str.replace(r'\.$', '', regex=True)  # Remove trailing period(s)
      )
    # df = df.astype(str)
    # 2. Process date columns:
    # Get today's date (as a datetime) using DD-MM-YYYY format.
    today_str = datetime.today().strftime('%d-%m-%Y')
    today = pd.to_datetime(today_str, format='%d-%m-%Y')

    # (a) Expected_Date: robustly parse and create a new column Expected_Date_mod.
    if "Expected_Date" in df.columns:
        def parse_expected_date(x):
            # Use today's date if x is missing, empty, or 'nan'
            return robust_date_parse(x, fallback_date=today)
        
        df["Expected_Date_mod"] = df["Expected_Date"].apply(parse_expected_date)
    
        # Also, update the original Expected_Date column using robust parsing.
        df["Expected_Date"] = df["Expected_Date"].apply(lambda x: robust_date_parse(x))
    
    # (b) Date: Convert to datetime using robust parsing.
    if "Date" in df.columns:
        df["Date"] = df["Date"].apply(lambda x: robust_date_parse(x))
    
    # (c) First_Received_Date: Convert to datetime using robust parsing.
    if "First_Received_Date" in df.columns:
        df["First_Received_Date"] = df["First_Received_Date"].apply(lambda x: robust_date_parse(x))
    
    # (d) Last_Received_Date: Convert to datetime using robust parsing.
    if "Last_Received_Date" in df.columns:
        df["Last_Received_Date"] = df["Last_Received_Date"].apply(lambda x: robust_date_parse(x))
    
    # 3. Process numeric columns:

    # 4. Create new columns using coalesce logic.
    # Helper function: returns the first non-null, non-empty value.
    def coalesce(col1, col2):
        # Replace empty strings with NA and then fill missing values.
        return col1.replace('', pd.NA).fillna(col2)
    
    # (a) Coalesce(Material_Name, Design_Name) -> new column: Material_Design
    if "Material_Name" in df.columns and "Design_Name" in df.columns:
        df["Material_Design"] = coalesce(df["Material_Name"], df["Design_Name"])
    elif "Material_Name" in df.columns:
        df["Material_Design"] = df["Material_Name"]
    elif "Design_Name" in df.columns:
        df["Material_Design"] = df["Design_Name"]
    
    # (b) Coalesce(Color, Color_Name) -> new column: Final_Color
    if "Color" in df.columns and "Color_Name" in df.columns:
        df["Final_Color"] = coalesce(df["Color"], df["Color_Name"])
    elif "Color" in df.columns:
        df["Final_Color"] = df["Color"]
    elif "Color_Name" in df.columns:
        df["Final_Color"] = df["Color_Name"]
    
    # (c) Coalesce(Qty, Color_qty) -> new column: Final_Qty
    if "Qty" in df.columns and "Color_qty" in df.columns:
        df["Final_Qty"] = coalesce(df["Qty"], df["Color_qty"])
    elif "Qty" in df.columns:
        df["Final_Qty"] = df["Qty"]
    elif "Color_qty" in df.columns:
        df["Final_Qty"] = df["Color_qty"]
    
    # (d) Coalesce(Unit, Color_Unit) -> new column: Final_Unit
    if "Unit" in df.columns and "Color_Unit" in df.columns:
        df["Final_Unit"] = coalesce(df["Unit"], df["Color_Unit"])
    elif "Unit" in df.columns:
        df["Final_Unit"] = df["Unit"]
    elif "Color_Unit" in df.columns:
        df["Final_Unit"] = df["Color_Unit"]
    
    # Convert both columns to numeric and replace missing values with 0.
    if "Remaining_Design_Qty" in df.columns:
        df["Remaining_Design_Qty"] = pd.to_numeric(df["Remaining_Design_Qty"].replace('', None), errors='coerce').fillna(0)
    if "Remaining_Material_Qty" in df.columns:
        df["Remaining_Material_Qty"] = pd.to_numeric(df["Remaining_Material_Qty"].replace('', None), errors='coerce').fillna(0)

    # Coalesce the two columns.
    if "Remaining_Material_Qty" in df.columns and "Remaining_Design_Qty" in df.columns:
        df["Final_Remain_Qty"] = df["Remaining_Material_Qty"].combine_first(df["Remaining_Design_Qty"]).fillna(0)
    elif "Remaining_Material_Qty" in df.columns:
        df["Final_Remain_Qty"] = df["Remaining_Material_Qty"]
    elif "Remaining_Design_Qty" in df.columns:
        df["Final_Remain_Qty"] = df["Remaining_Design_Qty"]
    
    df.reset_index(drop=True, inplace=True)
    return df

def modify_jobcard_sample_dataframe(df):
    print("🛠 Modifying Vastra Sample Report...")

    # 1. Clean column names: replace spaces and "/" with underscores.
    # df.columns = df.columns.str.replace(" ", "_").str.replace("/", "_")
    
    df.columns = (
    df.columns
      .str.replace(" ", "_")
      .str.replace("/", "_")
      .str.replace(r'\.$', '', regex=True)  # Remove trailing period(s)
      )
    # df = df.astype(str)
    # 2. Process date columns:
    # Get today's date (as a datetime) using DD-MM-YYYY format.
    today_str = datetime.today().strftime('%d-%m-%Y')
    today = pd.to_datetime(today_str, format='%d-%m-%Y')

    # (a) Expected_Date: robustly parse and create a new column Expected_Date_mod.
    if "Expected_Date" in df.columns:
        def parse_expected_date(x):
            # Use today's date if x is missing, empty, or 'nan'
            return robust_date_parse(x, fallback_date=today)
        
        df["Expected_Date_mod"] = df["Expected_Date"].apply(parse_expected_date)
    
        # Also, update the original Expected_Date column using robust parsing.
        df["Expected_Date"] = df["Expected_Date"].apply(lambda x: robust_date_parse(x))
    
    # (b) Date: Convert to datetime using robust parsing.
    if "Date" in df.columns:
        df["Date"] = df["Date"].apply(lambda x: robust_date_parse(x))
    
    # (c) First_Received_Date: Convert to datetime using robust parsing.
    if "First_Received_Date" in df.columns:
        df["First_Received_Date"] = df["First_Received_Date"].apply(lambda x: robust_date_parse(x))
    
    # (d) Last_Received_Date: Convert to datetime using robust parsing.
    if "Last_Received_Date" in df.columns:
        df["Last_Received_Date"] = df["Last_Received_Date"].apply(lambda x: robust_date_parse(x))
    
    # 3. Process numeric columns:

    # 4. Create new columns using coalesce logic.
    # Helper function: returns the first non-null, non-empty value.
    def coalesce(col1, col2):
        # Replace empty strings with NA and then fill missing values.
        return col1.replace('', pd.NA).fillna(col2)
    
    # (a) Coalesce(Material_Name, Design_Name) -> new column: Material_Design
    if "Material_Name" in df.columns and "Design_Name" in df.columns:
        df["Material_Design"] = coalesce(df["Material_Name"], df["Design_Name"])
    elif "Material_Name" in df.columns:
        df["Material_Design"] = df["Material_Name"]
    elif "Design_Name" in df.columns:
        df["Material_Design"] = df["Design_Name"]
    
    # (b) Coalesce(Color, Color_Name) -> new column: Final_Color
    if "Color" in df.columns and "Color_Name" in df.columns:
        df["Final_Color"] = coalesce(df["Color"], df["Color_Name"])
    elif "Color" in df.columns:
        df["Final_Color"] = df["Color"]
    elif "Color_Name" in df.columns:
        df["Final_Color"] = df["Color_Name"]
    
    # (c) Coalesce(Qty, Color_qty) -> new column: Final_Qty
    if "Qty" in df.columns and "Color_qty" in df.columns:
        df["Final_Qty"] = coalesce(df["Qty"], df["Color_qty"])
    elif "Qty" in df.columns:
        df["Final_Qty"] = df["Qty"]
    elif "Color_qty" in df.columns:
        df["Final_Qty"] = df["Color_qty"]
    
    # (d) Coalesce(Unit, Color_Unit) -> new column: Final_Unit
    if "Unit" in df.columns and "Color_Unit" in df.columns:
        df["Final_Unit"] = coalesce(df["Unit"], df["Color_Unit"])
    elif "Unit" in df.columns:
        df["Final_Unit"] = df["Unit"]
    elif "Color_Unit" in df.columns:
        df["Final_Unit"] = df["Color_Unit"]
    
    # Convert both columns to numeric and replace missing values with 0.
    if "Remaining_Design_Qty" in df.columns:
        df["Remaining_Design_Qty"] = pd.to_numeric(df["Remaining_Design_Qty"].replace('', None), errors='coerce').fillna(0)
    if "Remaining_Material_Qty" in df.columns:
        df["Remaining_Material_Qty"] = pd.to_numeric(df["Remaining_Material_Qty"].replace('', None), errors='coerce').fillna(0)

    # Coalesce the two columns.
    if "Remaining_Material_Qty" in df.columns and "Remaining_Design_Qty" in df.columns:
        df["Final_Remain_Qty"] = df["Remaining_Material_Qty"].combine_first(df["Remaining_Design_Qty"]).fillna(0)
    elif "Remaining_Material_Qty" in df.columns:
        df["Final_Remain_Qty"] = df["Remaining_Material_Qty"]
    elif "Remaining_Design_Qty" in df.columns:
        df["Final_Remain_Qty"] = df["Remaining_Design_Qty"]
    
    df.reset_index(drop=True, inplace=True)
    return df

def modify_sample_invoice_dataframe(df):
    # Load your raw data
    # Example: df = pd.read_excel('yourfile.xlsx')
    df = pd.read_clipboard()  # For quick testing if you copied the data

    # Create an empty list to hold customer names
    customer_names = []

    # Variable to track the current customer name
    current_customer = None

    # Loop through each row to detect and assign customer name
    for idx, row in df.iterrows():
        # If only the first column has value and others are empty
        if pd.notna(row.iloc[0]) and row.iloc[1:].isnull().all():
            current_customer = row.iloc[0]
        customer_names.append(current_customer)

    # Add the new "Customer Name" column
    df['Customer Name'] = customer_names

    # Optional: Remove the rows which are only customer titles (if you don't want them in final output)
    df = df[~((df.iloc[:, 1:].isnull()).all(axis=1))]
    df = df[df.iloc[:, 0] != 'Total']

    # Drop the unwanted 'Unnamed: 1' column if it exists
    if 'Unnamed: 1' in df.columns:
        df = df.drop(columns=['Unnamed: 1'])

    # Reorder columns if needed (put Customer Name first)
    cols = ['Customer Name'] + [col for col in df.columns if col != 'Customer Name']
    df = df[cols]

    # Save to Excel/CSV
    # df.to_excel('output.xlsx', index=False)

    print(df)