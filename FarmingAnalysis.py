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

    def get_ai_recommendations(self, input_data: Dict[str, Any], prediction: Dict[str, float]) -> str:
        """Get personalized recommendations from Gemini AI"""
        if not self.genai_model:
            return "AI recommendations not available - API key not configured."
            
        prompt = f"""
        As an agricultural expert, provide specific farming recommendations for:
        Location: {input_data['location']}
        Plant Type: {input_data['plant_type']}
        Plot Size: {input_data['plot_size']}
        Harvest Month: {input_data['harvest_month']}
        
        Based on our analysis:
        - Predicted Yield: {prediction['yield_prediction']} tons per hectare
        - Success Rating: {prediction['success_rating']}/10
        
        Please provide:
        1. Key risks and challenges for this specific combination
        2. Recommended preparations and best practices
        3. Optimal care instructions during growing season
        4. Harvesting tips
        Keep the response concise and practical.
        """
        
        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to get AI recommendations: {str(e)}"


    def predict(self, input_data: Dict[str, Any]) -> Dict[str, float]:
        input_df = pd.DataFrame([{
            'Season': 'Summer',
            'Rainfall_mm': 600,
            'Avg_Temp_C': 34,
            'Soil_Moisture_Percentage': 65,
            'Drought_Status': 'Low',
            'Pest_Pressure': 'Low',
            'Disease_Pressure': 'Low',
            'Growing_Days': 125,
            'Soil_pH': 6.2,
            'Fertilizer_Usage_kg_per_ha': 180
        }])
        
        if 'harvest_month' in input_data:
            input_df['Harvest_Month'] = input_data['harvest_month']
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
            harvest_idx = months.index(input_data['harvest_month'])
            planting_idx = (harvest_idx - 4) % 12
            input_df['Planting_Month'] = months[planting_idx]
        
        input_processed = self.preprocess_data(input_df)
        prediction_scaled = self.model.predict(input_processed[self.model.feature_names_in_])
        prediction = self.target_scaler.inverse_transform(prediction_scaled)
        
        return {
            'yield_prediction': round(prediction[0][0], 2),
            'success_rating': round(prediction[0][1], 1)
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
