import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from database import calendar_db
from weather_service import weather_service
from market_service import market_service

load_dotenv()

class PlantingCalendarService:
    def __init__(self):
        """Initialize planting calendar service with Gemini AI"""
        # Initialize Gemini AI
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.genai_model = None

        # South African crop planting data
        self.crop_calendar = {
            'maize': {
                'planting_season': 'October - December',
                'harvest_season': 'April - July',
                'growing_days': 120,
                'optimal_temp': '18-30°C',
                'rainfall_needs': '500-800mm',
                'regions': ['Free State', 'North West', 'Mpumalanga', 'KwaZulu-Natal']
            },
            'wheat': {
                'planting_season': 'May - July',
                'harvest_season': 'November - January',
                'growing_days': 120,
                'optimal_temp': '15-25°C',
                'rainfall_needs': '400-600mm',
                'regions': ['Western Cape', 'Free State', 'Northern Cape']
            },
            'soybeans': {
                'planting_season': 'October - December',
                'harvest_season': 'March - May',
                'growing_days': 100,
                'optimal_temp': '20-30°C',
                'rainfall_needs': '450-700mm',
                'regions': ['Mpumalanga', 'KwaZulu-Natal', 'Limpopo']
            },
            'sunflower': {
                'planting_season': 'October - January',
                'harvest_season': 'March - June',
                'growing_days': 90,
                'optimal_temp': '18-25°C',
                'rainfall_needs': '400-600mm',
                'regions': ['Free State', 'North West', 'Northern Cape']
            },
            'potatoes': {
                'planting_season': 'August - October, February - April',
                'harvest_season': 'December - February, June - August',
                'growing_days': 90,
                'optimal_temp': '15-20°C',
                'rainfall_needs': '500-700mm',
                'regions': ['Western Cape', 'Free State', 'Limpopo']
            },
            'tomatoes': {
                'planting_season': 'August - October, February - April',
                'harvest_season': 'November - January, May - July',
                'growing_days': 80,
                'optimal_temp': '18-25°C',
                'rainfall_needs': '400-600mm',
                'regions': ['All provinces']
            }
        }

    def get_optimal_planting_dates(self, crop_type, location, plot_size=None):
        """Get optimal planting dates based on crop, location, and weather"""
        if crop_type.lower() not in self.crop_calendar:
            return f"Crop data not available for {crop_type}"

        crop_info = self.crop_calendar[crop_type.lower()]

        # Get weather data for location
        weather_data = weather_service.get_current_weather(location)

        # Get market analysis
        market_analysis = market_service.get_market_analysis(crop_type, location)

        if not self.genai_model:
            return {
                'crop_info': crop_info,
                'weather_data': weather_data,
                'recommendation': 'AI analysis unavailable'
            }

        prompt = f"""
        As an agricultural expert, provide optimal planting recommendations for {crop_type} in {location}:

        Crop Information:
        - Typical planting season: {crop_info['planting_season']}
        - Growing period: {crop_info['growing_days']} days
        - Optimal temperature: {crop_info['optimal_temp']}
        - Rainfall needs: {crop_info['rainfall_needs']}

        Current Weather Conditions:
        """

        if weather_data:
            prompt += f"""
        - Current temperature: {weather_data['current']['temperature']}°C
        - Current humidity: {weather_data['current']['humidity']}%
        - 7-day precipitation forecast: {sum([day['precipitation'] for day in weather_data['daily_forecast']])}mm
        """

        if plot_size:
            prompt += f"\nPlot size: {plot_size} hectares"

        prompt += f"""

        Market Context:
        {market_analysis[:500]}...

        Please provide:
        1. Best planting dates for the next 6 months
        2. Expected harvest dates
        3. Weather-based recommendations
        4. Market timing considerations
        5. Risk factors and mitigation strategies
        6. Specific variety recommendations for this location

        Format as a practical farming calendar with specific dates and actions.
        """

        try:
            response = self.genai_model.generate_content(prompt)

            # Create schedule data
            schedule_data = {
                'crop_type': crop_type,
                'location': location,
                'plot_size': plot_size,
                'crop_info': crop_info,
                'weather_summary': weather_data['current'] if weather_data else None,
                'ai_recommendations': response.text,
                'generated_date': datetime.now().isoformat()
            }

            return schedule_data

        except Exception as e:
            return {
                'crop_info': crop_info,
                'weather_data': weather_data,
                'recommendation': f"Unable to generate AI recommendations: {str(e)}"
            }

    def create_farming_calendar(self, user_id, crops_and_locations):
        """Create a comprehensive farming calendar for multiple crops"""
        calendar_data = {
            'user_id': user_id,
            'crops': [],
            'created_date': datetime.now().isoformat()
        }

        for crop_info in crops_and_locations:
            crop_type = crop_info['crop_type']
            location = crop_info['location']
            plot_size = crop_info.get('plot_size')

            schedule = self.get_optimal_planting_dates(crop_type, location, plot_size)
            calendar_data['crops'].append(schedule)

        # Save to database
        calendar_db.save_planting_schedule(
            user_id,
            'multiple_crops',
            'multiple_locations',
            calendar_data
        )

        return calendar_data

    def get_monthly_tasks(self, month, location, crops):
        """Get farming tasks for a specific month"""
        if not self.genai_model:
            return "Monthly task recommendations unavailable"

        prompt = f"""
        As a farming advisor, provide monthly farming tasks for {month} in {location}:

        Crops being grown: {', '.join(crops)}

        Please provide:
        1. Planting activities for this month
        2. Maintenance and care tasks
        3. Harvesting activities
        4. Soil preparation tasks
        5. Pest and disease monitoring
        6. Equipment maintenance
        7. Market preparation activities

        Organize by week within the month and prioritize by importance.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate monthly tasks: {str(e)}"

    def get_seasonal_recommendations(self, location, farming_type="mixed"):
        """Get seasonal farming recommendations"""
        if not self.genai_model:
            return "Seasonal recommendations unavailable"

        current_month = datetime.now().strftime("%B")
        current_season = self._get_season(datetime.now().month)

        prompt = f"""
        As an agricultural consultant, provide seasonal farming recommendations for {location}:

        Current month: {current_month}
        Current season: {current_season}
        Farming type: {farming_type}

        Please provide:
        1. Best crops to plant this season
        2. Crops to avoid this season
        3. Soil preparation recommendations
        4. Irrigation planning
        5. Pest and disease prevention
        6. Market opportunities for this season
        7. Equipment and resource planning

        Focus on South African farming conditions and practices.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate seasonal recommendations: {str(e)}"

    def _get_season(self, month):
        """Get season based on month (Southern Hemisphere)"""
        if month in [12, 1, 2]:
            return "Summer"
        elif month in [3, 4, 5]:
            return "Autumn"
        elif month in [6, 7, 8]:
            return "Winter"
        else:
            return "Spring"

# Initialize planting calendar service
planting_service = PlantingCalendarService()