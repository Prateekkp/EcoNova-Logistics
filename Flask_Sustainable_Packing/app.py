from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)

# Expanded Carbon Footprint Lookup Table (in kg CO2e)
carbon_footprint_data = {
    "T-shirt": 2.1,      # kg CO2e
    "Washing Machine": 100,  # kg CO2e for washing machine
    "Laptop": 150,       # kg CO2e
    "Smartphone": 70,    # kg CO2e
    "Plastic Box": 0.5,  # kg CO2e
    "Bubble Wrap": 1.2,  # kg CO2e
    "Jute Bag": 0.2,     # kg CO2e
    "Cardboard Box": 0.3, # kg CO2e
    "Refrigerator": 200,  # kg CO2e
    "Heavy Duty Machine": 300,  # kg CO2e
    "Cement Bags": 50,    # kg CO2e (for bulk)
    "Steel Rods": 200,    # kg CO2e (metal products)
    "Concrete Block": 250,  # kg CO2e (construction materials)
    "Truck": 400,         # kg CO2e (truck or large vehicle)
    "Solar Panel": 100,   # kg CO2e (solar panels, environmentally friendly)
    "Furniture": 75,      # kg CO2e (e.g., wood or metal furniture)
    "Bicycle": 20,        # kg CO2e
    "Air Conditioner": 350,  # kg CO2e
    "Steel Plate": 150     # kg CO2e
}

# Expanded Materials Data (with weights up to 100 kg)
materials_data = pd.DataFrame({
    "Material": ["Cardboard Box", "Bubble Wrap", "Jute Bag", "Plastic Box", 
                 "Wooden Pallet", "Steel Crate", "Foam", "Shrink Wrap", 
                 "Cargo Netting", "Metal Sheet", "Heavy Duty Cardboard", 
                 "Polyurethane Foam", "Cotton Packing", "Cloth Bag", 
                 "Wooden Box"],
    "Max_Weight": [10, 5, 3, 15, 100, 100, 50, 50, 200, 100, 50, 30, 40, 10, 100],  # Max weight in kg
    "Fragility": ["Low", "High", "Low", "Medium", "Low", "High", "Low", "Low", "High", "Medium", "Low", "Low", "Low", "Low", "Medium"],
    "Cost": [2.0, 1.5, 0.8, 3.0, 10.0, 20.0, 5.0, 4.5, 15.0, 25.0, 10.0, 8.0, 6.0, 2.5, 15.0],  # Cost in $
    "Carbon_Emission": [0.3, 1.2, 0.2, 0.5, 0.4, 2.0, 0.5, 0.6, 2.5, 1.5, 0.6, 0.7, 0.4, 0.3, 1.0]  # Carbon emission in kg CO2e
})

# Function to estimate carbon footprint based on product name and weight
def estimate_carbon_footprint(product_name, weight):
    if product_name in carbon_footprint_data:
        return carbon_footprint_data[product_name]
    else:
        return weight * 0.05  # Fallback for products without data

# Function to recommend packaging material
def recommend_packaging(weight, fragility, max_cost, max_carbon, product_name):
    carbon_footprint = estimate_carbon_footprint(product_name, weight)
    
    filtered_data = materials_data.copy()
    filtered_data = filtered_data[(
        filtered_data["Max_Weight"] >= weight) &
        (filtered_data["Fragility"].str.lower() == fragility.lower()) & 
        (filtered_data["Cost"] <= max_cost) & 
        (filtered_data["Carbon_Emission"] <= max_carbon)
    ]
    
    if filtered_data.empty:
        return pd.DataFrame({
            "Material": ["No suitable material found"],
            "Max_Weight": [0],
            "Fragility": ["N/A"],
            "Cost": [0],
            "Carbon_Emission": [0]
        })
    
    # Normalize the Carbon Emission and Cost
    max_carbon = filtered_data["Carbon_Emission"].max()
    max_cost = filtered_data["Cost"].max()
    filtered_data["Normalized_Carbon"] = filtered_data["Carbon_Emission"] / max_carbon
    filtered_data["Normalized_Cost"] = filtered_data["Cost"] / max_cost
    
    # Combine the scores with equal weight (50% for each factor)
    filtered_data["Score"] = 0.5 * filtered_data["Normalized_Carbon"] + 0.5 * filtered_data["Normalized_Cost"]
    
    # Sort by the best combined score (lowest carbon and cost are better, so score is lower)
    top_materials = filtered_data.sort_values(by="Score").head(3)  # Get top 3 materials
    
    return top_materials

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        product_name = request.form.get("product_name")
        weight = float(request.form.get("weight"))
        fragility = request.form.get("fragility")
        max_cost = float(request.form.get("max_cost"))
        max_carbon = float(request.form.get("max_carbon"))
        
        top_materials = recommend_packaging(weight, fragility, max_cost, max_carbon, product_name)
        
        # Create the carbon emission graph
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(top_materials["Material"], top_materials["Carbon_Emission"], color='green')
        ax.set_xlabel("Material")
        ax.set_ylabel("Carbon Emission (kg CO2e)")
        ax.set_title("Carbon Emission of Top 3 Recommended Packaging Materials")
        
        # Save the carbon emission graph to a base64 string
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url_carbon = base64.b64encode(img.getvalue()).decode()
        
        # Create the cost graph
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(top_materials["Material"], top_materials["Cost"], color='blue')
        ax.set_xlabel("Material")
        ax.set_ylabel("Cost ($)")
        ax.set_title("Cost of Top 3 Recommended Packaging Materials")
        
        # Save the cost graph to a base64 string
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url_cost = base64.b64encode(img.getvalue()).decode()

        # Display the best material based on carbon and cost score
        best_material = top_materials.iloc[0]
        best_material_text = f"The best material based on both carbon emission and cost-effectiveness is {best_material['Material']}."

        # Reset the index and hide it
        top_materials = top_materials.reset_index(drop=True)
        
        return render_template("index.html", 
                               graph_url_carbon=graph_url_carbon, 
                               graph_url_cost=graph_url_cost, 
                               result=top_materials.to_html(classes='table table-striped', index=False),
                               best_material_text=best_material_text)
    
    return render_template("index.html")


# Route to display the requirements page
@app.route("/requirements")
def requirements():
    return render_template("requirements.html")

if __name__ == "__main__":
    app.run(debug=True)
