import pandas as pd
df = pd.read_csv("data/raw_data.csv", header=3)

# Drop the last three columns (empty)
df = df.iloc[:, :-3]

# Extract every set of 4 columns and prepare for concatenation
common_columns = ["date", "spy_close", "1_y_return", "return_by_05-05-2022"]
dfs = [df.iloc[:, i:i+4].set_axis(common_columns, axis=1) 
       for i in range(0, df.shape[1], 4)]

df = pd.concat(dfs, ignore_index=True)

# Strip "|", "[", and "(" from dates & replace missing data with none
df["date"] = df["date"].astype(str).str.replace(r'[|\[(]', '', regex=True).str.strip()
df.replace(["nu", "?", "Th", "a%", "S4A%", "4a%", "4A%"], None, inplace=True)

# Fix data on index 73
df.loc[73, "date"] = df.loc[73, "spy_close"] 
df.loc[73, "spy_close"] = df.loc[73, "1_y_return"]
df.loc[73, "1_y_return"] = None

# Remove row with missing data
df = df[df["date"] != "4147"].reset_index(drop=True)

# Conver date to datetime
df['date'] = pd.to_datetime(df["date"])
df = df.sort_values(by="date", ascending=True, ignore_index=True)

# Convert list to DataFrame, skipping redundant header rows
print(df.head())
print(df.shape)
print(df.describe())

# Save
df.to_csv('data/clean_data.csv')