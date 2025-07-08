import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import math

load_dotenv()

class ResourceCalculator:
    def __init__(self):
        """Initialize resource calculator with Gemini AI"""
        # Initialize Gemini AI
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.genai_model = None

        # Resource requirements per hectare for common crops
        self.crop_requirements = {
            'maize': {
                'seeds': {'amount': 25, 'unit': 'kg/ha', 'cost_per_unit': 45},
                'fertilizer': {
                    'nitrogen': {'amount': 120, 'unit': 'kg/ha', 'cost_per_kg': 12},
                    'phosphorus': {'amount': 60, 'unit': 'kg/ha', 'cost_per_kg': 15},
                    'potassium': {'amount': 40, 'unit': 'kg/ha', 'cost_per_kg': 18}
                },
                'water': {'amount': 600, 'unit': 'mm/season', 'cost_per_mm': 2.5},
                'labor': {'amount': 40, 'unit': 'hours/ha', 'cost_per_hour': 25}
            },
            'wheat': {
                'seeds': {'amount': 120, 'unit': 'kg/ha', 'cost_per_unit': 8},
                'fertilizer': {
                    'nitrogen': {'amount': 100, 'unit': 'kg/ha', 'cost_per_kg': 12},
                    'phosphorus': {'amount': 40, 'unit': 'kg/ha', 'cost_per_kg': 15},
                    'potassium': {'amount': 30, 'unit': 'kg/ha', 'cost_per_kg': 18}
                },
                'water': {'amount': 450, 'unit': 'mm/season', 'cost_per_mm': 2.5},
                'labor': {'amount': 35, 'unit': 'hours/ha', 'cost_per_hour': 25}
            },
            'soybeans': {
                'seeds': {'amount': 60, 'unit': 'kg/ha', 'cost_per_unit': 35},
                'fertilizer': {
                    'nitrogen': {'amount': 20, 'unit': 'kg/ha', 'cost_per_kg': 12},  # Lower due to nitrogen fixation
                    'phosphorus': {'amount': 80, 'unit': 'kg/ha', 'cost_per_kg': 15},
                    'potassium': {'amount': 60, 'unit': 'kg/ha', 'cost_per_kg': 18}
                },
                'water': {'amount': 500, 'unit': 'mm/season', 'cost_per_mm': 2.5},
                'labor': {'amount': 45, 'unit': 'hours/ha', 'cost_per_hour': 25}
            },
            'potatoes': {
                'seeds': {'amount': 2500, 'unit': 'kg/ha', 'cost_per_unit': 4},
                'fertilizer': {
                    'nitrogen': {'amount': 150, 'unit': 'kg/ha', 'cost_per_kg': 12},
                    'phosphorus': {'amount': 100, 'unit': 'kg/ha', 'cost_per_kg': 15},
                    'potassium': {'amount': 200, 'unit': 'kg/ha', 'cost_per_kg': 18}
                },
                'water': {'amount': 700, 'unit': 'mm/season', 'cost_per_mm': 2.5},
                'labor': {'amount': 80, 'unit': 'hours/ha', 'cost_per_hour': 25}
            },
            'tomatoes': {
                'seeds': {'amount': 0.3, 'unit': 'kg/ha', 'cost_per_unit': 2500},  # High-value seeds
                'fertilizer': {
                    'nitrogen': {'amount': 200, 'unit': 'kg/ha', 'cost_per_kg': 12},
                    'phosphorus': {'amount': 120, 'unit': 'kg/ha', 'cost_per_kg': 15},
                    'potassium': {'amount': 250, 'unit': 'kg/ha', 'cost_per_kg': 18}
                },
                'water': {'amount': 800, 'unit': 'mm/season', 'cost_per_mm': 2.5},
                'labor': {'amount': 120, 'unit': 'hours/ha', 'cost_per_hour': 25}
            }
        }

    def calculate_resources(self, crop_type, plot_size_ha, soil_type="medium", irrigation_type="drip"):
        """Calculate resource requirements for a specific crop and plot size"""
        if crop_type.lower() not in self.crop_requirements:
            return f"Resource data not available for {crop_type}"

        crop_data = self.crop_requirements[crop_type.lower()]

        # Calculate basic requirements
        calculations = {
            'crop_type': crop_type,
            'plot_size_ha': plot_size_ha,
            'soil_type': soil_type,
            'irrigation_type': irrigation_type,
            'resources': {},
            'total_cost': 0,
            'cost_breakdown': {}
        }

        # Seeds calculation
        seed_amount = crop_data['seeds']['amount'] * plot_size_ha
        seed_cost = seed_amount * crop_data['seeds']['cost_per_unit']
        calculations['resources']['seeds'] = {
            'amount': round(seed_amount, 2),
            'unit': crop_data['seeds']['unit'].replace('/ha', ''),
            'cost': round(seed_cost, 2)
        }
        calculations['cost_breakdown']['seeds'] = round(seed_cost, 2)

        # Fertilizer calculations
        fertilizer_total_cost = 0
        calculations['resources']['fertilizer'] = {}

        for nutrient, data in crop_data['fertilizer'].items():
            # Adjust for soil type
            soil_multiplier = {'poor': 1.3, 'medium': 1.0, 'rich': 0.8}.get(soil_type, 1.0)
            amount = data['amount'] * plot_size_ha * soil_multiplier
            cost = amount * data['cost_per_kg']

            calculations['resources']['fertilizer'][nutrient] = {
                'amount': round(amount, 2),
                'unit': 'kg',
                'cost': round(cost, 2)
            }
            fertilizer_total_cost += cost

        calculations['cost_breakdown']['fertilizer'] = round(fertilizer_total_cost, 2)

        # Water calculations
        irrigation_multiplier = {'drip': 0.8, 'sprinkler': 1.0, 'flood': 1.3}.get(irrigation_type, 1.0)
        water_amount = crop_data['water']['amount'] * plot_size_ha * irrigation_multiplier
        water_cost = water_amount * crop_data['water']['cost_per_mm']

        calculations['resources']['water'] = {
            'amount': round(water_amount, 2),
            'unit': 'mm total',
            'cost': round(water_cost, 2)
        }
        calculations['cost_breakdown']['water'] = round(water_cost, 2)

        # Labor calculations
        labor_amount = crop_data['labor']['amount'] * plot_size_ha
        labor_cost = labor_amount * crop_data['labor']['cost_per_hour']

        calculations['resources']['labor'] = {
            'amount': round(labor_amount, 2),
            'unit': 'hours',
            'cost': round(labor_cost, 2)
        }
        calculations['cost_breakdown']['labor'] = round(labor_cost, 2)

        # Total cost
        calculations['total_cost'] = round(sum(calculations['cost_breakdown'].values()), 2)

        return calculations

    def get_ai_resource_recommendations(self, crop_type, plot_size_ha, soil_type, location, budget=None):
        """Get AI-powered resource recommendations"""
        if not self.genai_model:
            return "AI recommendations unavailable"

        # Get basic calculations
        calculations = self.calculate_resources(crop_type, plot_size_ha, soil_type)

        prompt = f"""
        As an agricultural resource specialist, provide detailed recommendations for {crop_type} farming:

        Farm Details:
        - Crop: {crop_type}
        - Plot size: {plot_size_ha} hectares
        - Soil type: {soil_type}
        - Location: {location}
        """

        if budget:
            prompt += f"- Budget: R{budget}"

        prompt += f"""

        Calculated Resource Requirements:
        - Seeds: {calculations['resources']['seeds']['amount']} {calculations['resources']['seeds']['unit']} (R{calculations['resources']['seeds']['cost']})
        - Fertilizer total cost: R{calculations['cost_breakdown']['fertilizer']}
        - Water: {calculations['resources']['water']['amount']} {calculations['resources']['water']['unit']} (R{calculations['resources']['water']['cost']})
        - Labor: {calculations['resources']['labor']['amount']} {calculations['resources']['labor']['unit']} (R{calculations['resources']['labor']['cost']})
        - Total estimated cost: R{calculations['total_cost']}

        Please provide:
        1. Resource optimization strategies
        2. Cost-saving recommendations
        3. Quality vs cost trade-offs
        4. Timing recommendations for purchases
        5. Alternative resource options
        6. Risk mitigation strategies
        7. Expected ROI analysis

        """

        if budget and budget < calculations['total_cost']:
            prompt += f"\nIMPORTANT: The budget (R{budget}) is below estimated costs (R{calculations['total_cost']}). Provide budget-friendly alternatives."

        try:
            response = self.genai_model.generate_content(prompt)
            return {
                'calculations': calculations,
                'ai_recommendations': response.text,
                'budget_status': 'sufficient' if not budget or budget >= calculations['total_cost'] else 'insufficient'
            }
        except Exception as e:
            return {
                'calculations': calculations,
                'ai_recommendations': f"Unable to generate AI recommendations: {str(e)}",
                'budget_status': 'unknown'
            }

    def calculate_irrigation_schedule(self, crop_type, plot_size_ha, location, irrigation_type="drip"):
        """Calculate optimal irrigation schedule"""
        if not self.genai_model:
            return "Irrigation schedule unavailable"

        if crop_type.lower() not in self.crop_requirements:
            return f"Irrigation data not available for {crop_type}"

        water_needs = self.crop_requirements[crop_type.lower()]['water']['amount']

        prompt = f"""
        As an irrigation specialist, create an optimal irrigation schedule for {crop_type}:

        Farm Details:
        - Crop: {crop_type}
        - Plot size: {plot_size_ha} hectares
        - Location: {location}
        - Irrigation type: {irrigation_type}
        - Total water needs: {water_needs} mm/season

        Please provide:
        1. Daily/weekly irrigation schedule
        2. Water amounts per irrigation session
        3. Critical irrigation periods
        4. Water conservation strategies
        5. Monitoring recommendations
        6. Seasonal adjustments
        7. Equipment requirements

        Consider South African climate conditions and water scarcity.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate irrigation schedule: {str(e)}"

    def calculate_fertilizer_program(self, crop_type, plot_size_ha, soil_test_results=None):
        """Calculate detailed fertilizer application program"""
        if not self.genai_model:
            return "Fertilizer program unavailable"

        if crop_type.lower() not in self.crop_requirements:
            return f"Fertilizer data not available for {crop_type}"

        fertilizer_data = self.crop_requirements[crop_type.lower()]['fertilizer']

        prompt = f"""
        As a soil fertility expert, create a detailed fertilizer program for {crop_type}:

        Farm Details:
        - Crop: {crop_type}
        - Plot size: {plot_size_ha} hectares
        - Nitrogen needs: {fertilizer_data['nitrogen']['amount']} kg/ha
        - Phosphorus needs: {fertilizer_data['phosphorus']['amount']} kg/ha
        - Potassium needs: {fertilizer_data['potassium']['amount']} kg/ha
        """

        if soil_test_results:
            prompt += f"\nSoil test results: {soil_test_results}"

        prompt += """

        Please provide:
        1. Pre-planting fertilizer application
        2. Side-dressing schedule and amounts
        3. Foliar feeding recommendations
        4. Organic vs synthetic options
        5. Application timing and methods
        6. Soil pH management
        7. Micronutrient recommendations
        8. Cost optimization strategies

        Focus on South African farming conditions and available fertilizers.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate fertilizer program: {str(e)}"

# Initialize resource calculator
resource_calculator = ResourceCalculator()