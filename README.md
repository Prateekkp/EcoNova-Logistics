# EcoNova Logistics  

EcoNova Logistics is a collection of Flask applications designed for various logistics optimizations, including inventory analysis, route optimization, sustainable packaging, and a recycle program.  

## Landing Page  

Visit our landing page for an overview of the project:  
[EcoNova Logistics - Landing Page](https://doc110010.wixsite.com/econova-logistics)  

> **Note:** Due to technical constraints, the landing page is currently not connected to the Flask applications.

## Features  

1. **Inventory Analysis**: Optimize inventory management using Flask-based analytics.  
2. **Route Optimization**: Enhance logistics efficiency with optimized delivery routes.  
3. **Sustainable Packaging**: Explore eco-friendly packaging solutions.  
4. **Recycle Program**: Join our effort for a sustainable future by filling out our quick and easy recycling form [here](https://forms.fillout.com/t/sQvANGX1drus).  

## Project Structure  

```plaintext  
EcoNova-Logistics/  
├── Flask_Inventory_Analysis_Improved/  
│   ├── templates/  
│   │   ├── index.html  
│   │   ├── result.html  
│   ├── app.py  
├── Flask_Route_optimization/  
│   ├── templates/  
│   │   ├── index.html  
│   │   ├── result.html  
│   ├── app.py  
├── Flask_Sustainable_Packaging/  
    ├── templates/  
    │   ├── index.html  
    ├── app.py  
```  

## Requirements  

Ensure Python 3.8+ is installed on your system.  

### Install Flask  

Run the following command to install Flask:  

```bash  
pip install flask  
```  

## How to Run  

1. **Navigate to the Desired Module**:  
   Use `cd` to enter the specific module's directory:  

   - For **Inventory Analysis**:  
     ```bash  
     cd Flask_Inventory_Analysis_Improved  
     ```  

   - For **Route Optimization**:  
     ```bash  
     cd Flask_Route_optimization  
     ```  

   - For **Sustainable Packaging**:  
     ```bash  
     cd Flask_Sustainable_Packaging  
     ```  

2. **Run the Application**:  
   Once inside the desired folder, execute the following command:  

   ```bash  
   python app.py  
   ```  

3. **Access the Application**:  
   Open your web browser and go to:  

   ```  
   http://127.0.0.1:5000  
   ```  

## Notes  

- Each folder contains its own `app.py` file and corresponding templates.  
- Modify the `app.py` files if required for customization or debugging.  

## Contributing  

Feel free to fork the repository or submit issues to enhance the project.  
