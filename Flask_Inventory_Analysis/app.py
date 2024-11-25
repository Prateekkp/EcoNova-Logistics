from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from sklearn.linear_model import Ridge
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Load the CSV file
            df = pd.read_csv(file)

            # Ensure 'Date' is in datetime format
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # Drop rows with missing values in 'Date' or 'Sales'
            df = df.dropna(subset=['Date', 'Sales'])

            # Extract Month-Year as a period
            df['Month'] = df['Date'].dt.to_period('M')

            # Group by Month and Product to get total sales per product
            monthly_sales = df.groupby(['Month', 'Product_Name'])['Sales'].sum().reset_index()

            # Plot the top 3 products for each month and get their names
            trend_figures = []
            top_products_data = []
            for month in monthly_sales['Month'].unique():
                # Get top 3 products for the month
                monthly_data = monthly_sales[monthly_sales['Month'] == month]
                top_3 = monthly_data.nlargest(3, 'Sales')

                # Generate a list of colors for the bars
                colors = plt.cm.get_cmap('tab10', len(top_3))  # Use the 'tab10' colormap for distinct colors

                # Create a bar plot with different colors for each bar
                plt.figure(figsize=(8, 4))
                bars = plt.bar(top_3['Product_Name'], top_3['Sales'], color=colors(range(len(top_3))))
                plt.title(f'Top 3 Products in {month}')
                plt.xlabel('Product Name')
                plt.ylabel('Sales')
                plt.xticks(rotation=45, ha='right')

                # Save the plot as a base64-encoded string
                buffer = BytesIO()
                plt.tight_layout()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_data = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()
                plt.close()

                # Store product names and image for each month
                top_products_data.append({
                    'month': month,
                    'image': image_data,
                    'top_products': top_3['Product_Name'].tolist()
                })

            # Check if there are at least two months for forecasting
            if len(monthly_sales['Month'].unique()) >= 2:
                # Map months to numeric values
                month_mapping = {month: i + 1 for i, month in enumerate(monthly_sales['Month'].unique())}
                monthly_sales['Month_Num'] = monthly_sales['Month'].map(month_mapping)

                # Forecast using Ridge regression
                forecast_data = []
                for product in monthly_sales['Product_Name'].unique():
                    product_data = monthly_sales[monthly_sales['Product_Name'] == product]
                    if len(product_data) >= 2:  # Ensure sufficient data for forecasting
                        X = product_data[['Month_Num']]
                        y = product_data['Sales']
                        model = Ridge(alpha=1.0)
                        model.fit(X, y)
                        forecast_sales = model.predict([[len(month_mapping) + 1]])[0]
                        forecast_data.append({'Product_Name': product, 'Forecasted_Sales': forecast_sales})

                forecast_df = pd.DataFrame(forecast_data)
                top_forecasts = forecast_df.nlargest(3, 'Forecasted_Sales')

                # Generate a list of colors for the forecast bars
                forecast_colors = plt.cm.get_cmap('tab10', len(top_forecasts))  # Use the same colormap or choose another
                plt.figure(figsize=(8, 4))
                bars = plt.bar(top_forecasts['Product_Name'], top_forecasts['Forecasted_Sales'], color=forecast_colors(range(len(top_forecasts))))
                plt.title('Top 3 Forecasted Products for Next Month')
                plt.xlabel('Product Name')
                plt.ylabel('Forecasted Sales')
                plt.xticks(rotation=45, ha='right')

                # Save the forecast plot
                buffer = BytesIO()
                plt.tight_layout()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                forecast_image = base64.b64encode(buffer.getvalue()).decode()
                buffer.close()
                plt.close()
            else:
                forecast_image = None

            # Calculate the trend line for total sales across months
            total_monthly_sales = df.groupby('Month')['Sales'].sum().reset_index()

            # Map months to numeric values
            total_monthly_sales['Month_Num'] = total_monthly_sales['Month'].apply(lambda x: x.ordinal)

            # Fit the Ridge regression model for the trend line
            X = total_monthly_sales[['Month_Num']]
            y = total_monthly_sales['Sales']
            model = Ridge(alpha=1.0)
            model.fit(X, y)

            # Predict sales for the trend line
            trend_line_sales = model.predict(X)

            # Plot the total sales with the trend line
            plt.figure(figsize=(10, 6))
            plt.plot(total_monthly_sales['Month'].astype(str), total_monthly_sales['Sales'], label='Total Sales', color='blue', marker='o')
            plt.plot(total_monthly_sales['Month'].astype(str), trend_line_sales, label='Trend Line', color='red', linestyle='--')
            plt.title('Total Sales Trend with Regression Line')
            plt.xlabel('Month')
            plt.ylabel('Sales')
            plt.xticks(rotation=45, ha='right')
            plt.legend()

            # Save the trend line plot as a base64-encoded string
            buffer = BytesIO()
            plt.tight_layout()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            trend_line_image = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            plt.close()

            # Render the template with trend and forecast images, as well as product names
            return render_template('result.html', 
                                   top_products_data=top_products_data, 
                                   forecast_image=forecast_image,
                                   trend_line_image=trend_line_image)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
