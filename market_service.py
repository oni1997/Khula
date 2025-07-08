import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import json
from database import market_db

load_dotenv()

class MarketService:
    def __init__(self):
        """Initialize market service with Gemini AI for analysis"""
        # Initialize Gemini AI
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.genai_model = None

    def get_simulated_market_prices(self):
        """Get simulated market prices for South African crops"""
        # Simulated market data - in production, you'd connect to real market APIs
        base_prices = {
            'maize': {'price': 4500, 'unit': 'R/ton', 'change': 0},
            'wheat': {'price': 6200, 'unit': 'R/ton', 'change': 0},
            'soybeans': {'price': 8500, 'unit': 'R/ton', 'change': 0},
            'sunflower': {'price': 7800, 'unit': 'R/ton', 'change': 0},
            'potatoes': {'price': 3200, 'unit': 'R/ton', 'change': 0},
            'tomatoes': {'price': 8500, 'unit': 'R/ton', 'change': 0},
            'onions': {'price': 4800, 'unit': 'R/ton', 'change': 0},
            'carrots': {'price': 5200, 'unit': 'R/ton', 'change': 0},
            'cabbage': {'price': 2800, 'unit': 'R/ton', 'change': 0},
            'beans': {'price': 12000, 'unit': 'R/ton', 'change': 0}
        }

        # Add random price fluctuations
        for crop in base_prices:
            change_percent = random.uniform(-5, 5)  # ±5% change
            base_prices[crop]['change'] = round(change_percent, 2)
            new_price = base_prices[crop]['price'] * (1 + change_percent/100)
            base_prices[crop]['price'] = round(new_price, 0)
            base_prices[crop]['last_updated'] = datetime.now().isoformat()

        return base_prices

    def get_market_trends(self, crop_type=None):
        """Get market trends for specific crop or all crops"""
        try:
            # Get current prices
            current_prices = self.get_simulated_market_prices()

            # Generate historical data for trends (simulated)
            historical_data = {}
            for crop, data in current_prices.items():
                if crop_type and crop != crop_type.lower():
                    continue

                # Generate 30 days of historical data
                history = []
                base_price = data['price']
                for i in range(30, 0, -1):
                    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                    # Simulate price variation
                    variation = random.uniform(-10, 10)
                    price = base_price * (1 + variation/100)
                    history.append({
                        'date': date,
                        'price': round(price, 0),
                        'volume': random.randint(100, 1000)  # Simulated volume
                    })

                historical_data[crop] = {
                    'current_price': data['price'],
                    'unit': data['unit'],
                    'change_percent': data['change'],
                    'history': history,
                    'last_updated': data['last_updated']
                }

            # Save to database
            if crop_type:
                market_db.save_market_data(crop_type.lower(), historical_data)
            else:
                for crop, data in historical_data.items():
                    market_db.save_market_data(crop, data)

            return historical_data

        except Exception as e:
            print(f"Error fetching market trends: {e}")
            return {}

    def get_market_analysis(self, crop_type, location="South Africa"):
        """Get AI-powered market analysis for a specific crop"""
        if not self.genai_model:
            return "Market analysis unavailable - AI service not configured"

        # Get market data
        market_data = self.get_market_trends(crop_type)

        if not market_data or crop_type.lower() not in market_data:
            return f"Market data not available for {crop_type}"

        crop_data = market_data[crop_type.lower()]
        current_price = crop_data['current_price']
        change_percent = crop_data['change_percent']

        # Calculate average price from history
        history = crop_data['history']
        avg_price = sum([day['price'] for day in history]) / len(history)

        prompt = f"""
        As an agricultural market analyst, provide analysis for {crop_type} in {location}:

        Current Market Data:
        - Current Price: R{current_price}/ton
        - Price Change: {change_percent}%
        - 30-day Average: R{avg_price:.0f}/ton
        - Price vs Average: {((current_price - avg_price) / avg_price * 100):.1f}%

        Please provide:
        1. Market outlook for {crop_type} (bullish/bearish/neutral)
        2. Key factors affecting current prices
        3. Price predictions for next 30 days
        4. Best selling strategies for farmers
        5. Optimal timing for market entry
        6. Risk factors to consider

        Keep the analysis practical and actionable for South African farmers.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate market analysis: {str(e)}"

    def get_price_alerts(self, crop_type, target_price=None):
        """Get price alerts for specific crops"""
        market_data = self.get_market_trends(crop_type)

        if not market_data or crop_type.lower() not in market_data:
            return []

        crop_data = market_data[crop_type.lower()]
        current_price = crop_data['current_price']
        change_percent = crop_data['change_percent']

        alerts = []

        # Price movement alerts
        if abs(change_percent) > 3:
            direction = "increased" if change_percent > 0 else "decreased"
            severity = "high" if abs(change_percent) > 5 else "medium"
            alerts.append({
                "type": "price_movement",
                "message": f"{crop_type.title()} price has {direction} by {abs(change_percent):.1f}% to R{current_price}/ton",
                "severity": severity,
                "current_price": current_price,
                "change_percent": change_percent
            })

        # Target price alerts
        if target_price and current_price >= target_price:
            alerts.append({
                "type": "target_reached",
                "message": f"{crop_type.title()} has reached your target price of R{target_price}/ton (Current: R{current_price}/ton)",
                "severity": "high",
                "current_price": current_price,
                "target_price": target_price
            })

        return alerts

    def get_seasonal_trends(self, crop_type):
        """Get seasonal price trends for crop planning"""
        if not self.genai_model:
            return "Seasonal analysis unavailable"

        prompt = f"""
        As an agricultural economist, provide seasonal price trends for {crop_type} in South Africa:

        Please analyze:
        1. Typical price patterns throughout the year
        2. Peak and low price seasons
        3. Factors driving seasonal variations
        4. Best planting times for optimal market prices
        5. Storage vs immediate sale recommendations
        6. Regional price differences within South Africa

        Provide specific months and expected price ranges where possible.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate seasonal analysis: {str(e)}"

# Initialize market service
market_service = MarketService()