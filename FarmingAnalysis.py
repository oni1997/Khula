import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Any

class FarmingAnalyzer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.target_scaler = StandardScaler()
        
        # Load environment variables
        load_dotenv()
        google_api_key = os.getenv('GOOGLE_API_KEY')
        
        # Initialize Gemini AI if API key is set
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.genai_model = None

    def _load_training_data(self):
        """Simulate loading historical data from CSV"""
        np.random.seed(42)
        n_samples = 1000
        
        seasons = ['Summer', 'Winter', 'Spring', 'Fall']
        drought_status = ['Low', 'Medium', 'High']
        pest_pressure = ['Low', 'Medium', 'High']
        disease_pressure = ['Low', 'Medium', 'High']
        
        data = {
            'Season': np.random.choice(seasons, n_samples),
            'Rainfall_mm': np.random.normal(450, 100, n_samples),
            'Avg_Temp_C': np.random.normal(25, 5, n_samples),
            'Soil_Moisture_Percentage': np.random.normal(70, 5, n_samples),
            'Drought_Status': np.random.choice(drought_status, n_samples),
            'Pest_Pressure': np.random.choice(pest_pressure, n_samples),
            'Disease_Pressure': np.random.choice(disease_pressure, n_samples),
            'Growing_Days': np.random.normal(135, 15, n_samples),
            'Soil_pH': np.random.normal(6.5, 0.5, n_samples),
            'Fertilizer_Usage_kg_per_ha': np.random.normal(180, 20, n_samples),
            'Yield_per_hectare': np.random.normal(3500, 500, n_samples),  # Target variable
            'Success_Rating': np.random.normal(7, 1, n_samples)  # Target variable
        }
        
        data['Yield_per_hectare'] = np.where(
            data['Drought_Status'] == 'High',
            data['Yield_per_hectare'] * 0.7,
            data['Yield_per_hectare']
        )
        
        return pd.DataFrame(data)


    def preprocess_data(self, df):
        categorical_columns = ['Season', 'Drought_Status', 'Pest_Pressure', 
                               'Disease_Pressure', 'Season_Quality', 'Planting_Month', 
                               'Harvest_Month']
        
        for column in categorical_columns:
            if column in df.columns:
                self.label_encoders[column] = LabelEncoder()
                df[column] = self.label_encoders[column].fit_transform(df[column])
        
        numerical_columns = ['Rainfall_mm', 'Avg_Temp_C', 'Soil_Moisture_Percentage',
                             'Growing_Days', 'Soil_pH', 'Fertilizer_Usage_kg_per_ha']
        
        df[numerical_columns] = self.scaler.fit_transform(df[numerical_columns])
        
        return df

    def train_model(self, data_path: str) -> float:
        df = pd.read_csv(data_path)
        df_processed = self.preprocess_data(df)
        
        features = ['Rainfall_mm', 'Avg_Temp_C', 'Soil_Moisture_Percentage',
                    'Growing_Days', 'Soil_pH', 'Fertilizer_Usage_kg_per_ha',
                    'Season', 'Drought_Status', 'Pest_Pressure', 'Disease_Pressure']
        
        target = ['Yield_Tons_Per_Hectare', 'Success_Rating']
        
        X = df_processed[features]
        y = df[target]
        
        y_scaled = self.target_scaler.fit_transform(y)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_scaled, 
                                                            test_size=0.2, 
                                                            random_state=42)
        
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        self.save_model()
        
        return self.model.score(X_test, y_test)

    def get_ai_recommendations(self, input_data: Dict[str, Any], prediction: Dict[str, float]) -> Dict[str, str]:
        """Get personalized recommendations from Gemini AI, returned as structured data
        
        Returns:
            Dict with keys: risks, preparations, variety, care, harvest, upgrade_message
        """
        if not self.genai_model:
            return {
                "error": "AI recommendations not available - API key not configured."
            }

        base_context = f"""
        As an agricultural expert, analyze the following farming scenario:
        Location: {input_data['location']}
        Plant Type: {input_data['plant_type']}
        Plot Size: {input_data['plot_size']}
        Harvest Month: {input_data['harvest_month']}

        Analysis Results:
        - Predicted Yield: {prediction['yield_prediction']} tons per hectare
        - Success Rating: {prediction['success_rating']}/10
        """

        prompts = {
            "risks": f"{base_context}\nProvide key risks and challenges for this specific combination.",
            
            "preparations": f"{base_context}\nProvide recommended key preparations and best practices for these specifications.",
            
            "variety": f"""{base_context}
            Recommend the most appropriate maize variety for this season and plot size to maximize yield. Choose from:
            - ACTIVONEW (early double-purpose variety)
            - AKANTO (medium late dent corn for grain and silage)
            - AMBIENT (early variety with starch)
            - AROLDONEW (double-purpose maize with quick juvenile development)
            - BADIANE (profitable grain maize)
            - CRUSH (high-yielding grain maize)
            - DAVOS (early double-purpose maize)
            - FLYNT (flexible crop rotation)
            - FORTARIS (early dent silage maize)
            - FORTTUNO (balanced silage quality)
            - GALAKTION (late dual-purpose hybrid)
            - GLUTEXO (two grain rows ahead)
            - HONOREEN (high-yielding biomass type)
            - IONITINEW (grain maize for favorable conditions)
            - JOY (good tolerance to cold weather)
            - LIKEIT (rapid juvenile development, high starch yields)
            - LIROYAL (long growth habit, early vigor)
            - MOVANNA (high starch yields, cold tolerance)
            - PETROSCHKA (high starch yield)
            - PIATOV (dent genetics for yield stability)
            - PROPULSE (good health status, early flowering)
            - PURPLE (high-yielding silage and biogas maize)
            - SHINY (great yield and look)
            - VARIANTAL / INDEM 1355NEW (all-in-one for silage and grain)
            - WAKEFIELD (dent maize for high grain)""",
            
            "care": f"{base_context}\nProvide optimal care instructions during growing season for these specifications.",
            
            "harvest": f"{base_context}\nProvide harvesting tips for these specifications."
        }

        try:
            recommendations = {}
            for key, prompt in prompts.items():
                response = self.genai_model.generate_content(prompt)
                recommendations[key] = response.text.strip()
            
            # Add upgrade message
            recommendations["upgrade_message"] = "Upgrade your package to get more in-depth support and recommendations tailored to your specific soil type, weather conditions, and maize variety."
            
            return recommendations
        
        except Exception as e:
            return {
                "error": f"Unable to get AI recommendations: {str(e)}"
            }
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, float]:
        # Plot size definitions and modifiers
        plot_sizes = {
            'Small': {
                'min_size': 75,  # square feet
                'max_size': 100,
                'yield_modifier': 0.85,  # slightly lower yield due to less efficient use of space
                'success_modifier': 1.1   # higher success rate due to easier management
            },
            'Medium': {
                'min_size': 100,  # square meters
                'max_size': 320,
                'yield_modifier': 1.0,    # baseline yield
                'success_modifier': 1.0    # baseline success rate
            },
            'Large': {
                'min_size': 320,  # square meters
                'max_size': 800,
                'yield_modifier': 1.15,   # higher yield due to economies of scale
                'success_modifier': 0.9    # slightly lower success rate due to management complexity
            }
        }

        # Seasonal base values
        seasonal_data = {
            'Summer': {
                'Rainfall_mm': 600,
                'Avg_Temp_C': 34,
                'Soil_Moisture_Percentage': 65,
                'Growing_Days': 125,
                'base_yield_modifier': 1.0
            },
            'Winter': {
                'Rainfall_mm': 300,
                'Avg_Temp_C': 18,
                'Soil_Moisture_Percentage': 75,
                'Growing_Days': 150,
                'base_yield_modifier': 0.8
            },
            'Spring': {
                'Rainfall_mm': 450,
                'Avg_Temp_C': 25,
                'Soil_Moisture_Percentage': 70,
                'Growing_Days': 135,
                'base_yield_modifier': 1.2
            },
            'Fall': {
                'Rainfall_mm': 350,
                'Avg_Temp_C': 22,
                'Soil_Moisture_Percentage': 68,
                'Growing_Days': 140,
                'base_yield_modifier': 0.9
            }
        }

        # Monthly adjustments
        monthly_modifiers = {
            'January': {'temp': -2, 'moisture': +5, 'yield': 0.85},
            'February': {'temp': -1, 'moisture': +5, 'yield': 0.9},
            'March': {'temp': +1, 'moisture': +3, 'yield': 1.1},
            'April': {'temp': +2, 'moisture': +2, 'yield': 1.15},
            'May': {'temp': +3, 'moisture': 0, 'yield': 1.2},
            'June': {'temp': +4, 'moisture': -2, 'yield': 1.1},
            'July': {'temp': +5, 'moisture': -5, 'yield': 1.0},
            'August': {'temp': +5, 'moisture': -7, 'yield': 0.95},
            'September': {'temp': +3, 'moisture': -3, 'yield': 0.9},
            'October': {'temp': +1, 'moisture': 0, 'yield': 0.85},
            'November': {'temp': -1, 'moisture': +2, 'yield': 0.8},
            'December': {'temp': -2, 'moisture': +4, 'yield': 0.8}
        }

        # Get plot size and season from input or use default
        plot_size = input_data.get('plot_size', 'Medium')
        season = input_data.get('season', 'Summer')
        base_data = seasonal_data[season]
        size_data = plot_sizes[plot_size]

        # Calculate size-specific resource requirements
        plot_size_actual = input_data.get('plot_size_value', (size_data['min_size'] + size_data['max_size']) / 2)
        
        # Adjust fertilizer based on plot size (kg per ha converted to actual plot size)
        base_fertilizer = input_data.get('fertilizer_usage', 180)
        if plot_size == 'Small':
            # Convert square feet to hectares and adjust fertilizer
            actual_fertilizer = (base_fertilizer * (plot_size_actual * 0.092903) / 10000)
        else:
            # Convert square meters to hectares and adjust fertilizer
            actual_fertilizer = (base_fertilizer * plot_size_actual / 10000)

        # Initialize base values
        input_values = {
            'Season': season,
            'Rainfall_mm': base_data['Rainfall_mm'],
            'Avg_Temp_C': base_data['Avg_Temp_C'],
            'Soil_Moisture_Percentage': base_data['Soil_Moisture_Percentage'],
            'Drought_Status': input_data.get('drought_status', 'Low'),
            'Pest_Pressure': input_data.get('pest_pressure', 'Low'),
            'Disease_Pressure': input_data.get('disease_pressure', 'Low'),
            'Growing_Days': base_data['Growing_Days'],
            'Soil_pH': input_data.get('soil_ph', 6.2),
            'Fertilizer_Usage_kg_per_ha': actual_fertilizer
        }

        # Apply monthly adjustments if harvest month is provided
        if 'harvest_month' in input_data:
            harvest_month = input_data['harvest_month']
            monthly_mod = monthly_modifiers[harvest_month]
            
            # Adjust temperature and moisture based on month
            input_values['Avg_Temp_C'] += monthly_mod['temp']
            input_values['Soil_Moisture_Percentage'] += monthly_mod['moisture']
            
            # Calculate planting month
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December']
            harvest_idx = months.index(harvest_month)
            planting_idx = (harvest_idx - 4) % 12
            planting_month = months[planting_idx]
            
            input_values['Harvest_Month'] = harvest_month
            input_values['Planting_Month'] = planting_month
            
            # Adjust growing days based on season and month
            input_values['Growing_Days'] = int(base_data['Growing_Days'] * 
                                            (monthly_mod['yield'] * 0.9 + 0.1))

        # Create DataFrame
        input_df = pd.DataFrame([input_values])
        
        # Process input and make prediction
        input_processed = self.preprocess_data(input_df)
        prediction_scaled = self.model.predict(input_processed[self.model.feature_names_in_])
        base_prediction = self.target_scaler.inverse_transform(prediction_scaled)
        
        # Apply plot size, seasonal and monthly yield modifiers
        final_yield = (base_prediction[0][0] * 
                    base_data['base_yield_modifier'] * 
                    size_data['yield_modifier'])
        
        if 'harvest_month' in input_data:
            final_yield *= monthly_modifiers[harvest_month]['yield']
        
        # Calculate success rating based on conditions
        success_rating = base_prediction[0][1] * size_data['success_modifier']
        
        # Adjust success rating based on environmental factors
        if input_values['Drought_Status'] == 'High':
            success_rating *= 0.8
        if input_values['Pest_Pressure'] == 'High':
            success_rating *= 0.85
        if input_values['Disease_Pressure'] == 'High':
            success_rating *= 0.85
        
        # Calculate total yield based on area
        if plot_size == 'Small':
            # Convert square feet to hectares for yield calculation
            area_in_hectares = plot_size_actual * 0.092903 / 10000
        else:
            # Convert square meters to hectares for yield calculation
            area_in_hectares = plot_size_actual / 10000
        
        total_yield = final_yield * area_in_hectares
        
        return {
            'yield_prediction': round(total_yield, 2),  # Total yield for the entire plot
            'yield_per_hectare': round(final_yield, 2),  # Yield per hectare
            'success_rating': round(min(max(success_rating, 0), 10), 1)
        }

    def save_model(self):
        model_path = 'models/'
        if not os.path.exists(model_path):
            os.makedirs(model_path)
            
        joblib.dump(self.model, f'{model_path}farming_model.joblib')
        joblib.dump(self.scaler, f'{model_path}scaler.joblib')
        joblib.dump(self.label_encoders, f'{model_path}label_encoders.joblib')
        joblib.dump(self.target_scaler, f'{model_path}target_scaler.joblib')

    def load_model(self):
        model_path = 'models/'
        self.model = joblib.load(f'{model_path}farming_model.joblib')
        self.scaler = joblib.load(f'{model_path}scaler.joblib')
        self.label_encoders = joblib.load(f'{model_path}label_encoders.joblib')
        self.target_scaler = joblib.load(f'{model_path}target_scaler.joblib')
