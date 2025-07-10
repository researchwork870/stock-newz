import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

def convert_percentage(value):
    if value == 'NaN' or pd.isna(value):
        return np.nan
    elif isinstance(value, str) and value.endswith('%'):
        # Remove % and convert to float
        return float(value.rstrip('%'))
    else:
        return float(value)

def plot(df, title):
    
    # Create the time series plot
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date'], df['Value'], marker='o', linewidth=2, markersize=6)
    plt.title(f'{title}', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Value (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)

    # Format y-axis to show percentage
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}%'))

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Show the plot
    plt.show()

def stock_growth_rate(df, stock):
    df = df[df.stock == stock].drop(columns=["stock", "cap_group"]).T.reset_index()
    df.columns = ["Date", "Value"]
    df["Date"] = pd.to_datetime(df["Date"], format="%b %Y")
    df = df.sort_values("Date").reset_index(drop=True)
    df["Value"] = df["Value"].apply(convert_percentage)
    df = df.dropna()

    df['Date_numeric'] = range(1, len(df) + 1)

     # Fit linear regression
    X = df['Date_numeric'].values.reshape(-1, 1)
    y = df['Value'].values

    # Create and fit the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    return model.coef_[0], df