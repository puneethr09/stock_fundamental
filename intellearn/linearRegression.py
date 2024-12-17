
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from src.basic_analysis import get_financial_ratios

# Assume ratios_df is your DataFrame with financial ratios
ratios_df = get_financial_ratios('RELIANCE.NS')

# Prepare features and target variable
X = ratios_df[['ROE', 'ROA', 'Debt to Equity']]  # Example features
y = ratios_df['P/E Ratio']  # Example target variable

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
