# Khula - Smart Farming Assistant

Khula is an AI-powered farming assistant that provides comprehensive tools for modern agriculture. Built with Flask, MongoDB, and Google Gemini AI, it offers real-time weather data, market analysis, planting schedules, resource calculations, and community features.

## 🌟 Features

### 1. **Weather Integration** 🌤️
- **Real-time weather data** from OpenWeatherMap API
- **7-day forecasts** with temperature, humidity, precipitation, and wind
- **Intelligent database caching** - fetches data once per day per location to stay within API limits
- **AI-powered farming weather analysis** using Gemini for crop-specific recommendations
- **Weather alerts and recommendations** for farming activities
- **Location-based weather insights** for South African farming regions
- **API optimization** - automatically caches weather data to minimize API calls (1000/day limit)

### 2. **Market Prices**
- Current crop prices and market trends
- AI market analysis and predictions
- Price alerts and notifications
- Seasonal trend analysis

### 3. **Planting Calendar**
- Optimal planting and harvesting schedules
- Location and crop-specific recommendations
- Weather-based timing suggestions
- Multi-crop farming calendars

### 4. **Resource Calculator**
- Fertilizer, water, and seed requirements
- Cost calculations and budget planning
- AI-powered optimization recommendations
- Irrigation scheduling

### 5. **Community Features**
- Farmer forums and knowledge sharing
- AI-moderated content and advice
- Expert insights and trending topics
- Q&A platform with AI assistance

### 6. **Image Analysis**
- Crop and soil image analysis using Gemini Vision
- Disease and pest identification
- Care recommendations

## 🚀 Installation

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- Google Gemini API key
- OpenWeatherMap API key (free tier: 1000 calls/day)

### Setup

1. **Clone the repository**
```bash
git clone git@github.com:oni1997/Khula.git
cd Khula
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and database configuration
```

4. **Start MongoDB**
```bash
# For local MongoDB
mongod

# Or use MongoDB Atlas cloud service
```

5. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
GOOGLE_API_KEY=your_google_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=khula_farming
OPEN_WEATHER_API=your_openweathermap_api_key_here

# Optional
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### MongoDB Collections

The application automatically creates the following collections:
- `weather_data` - Weather information and forecasts (with intelligent daily caching)
- `market_prices` - Crop prices and market data
- `planting_calendar` - Planting schedules and recommendations
- `forum_posts` - Community forum posts
- `forum_comments` - Forum post comments
- `user_profiles` - User information and preferences

### Intelligent Weather Caching

The weather service implements smart caching to optimize API usage:
- **Daily caching**: Weather data is fetched once per day per location
- **Automatic cache checking**: Before making API calls, checks if today's data exists
- **API limit protection**: Helps stay within OpenWeatherMap's 1000 calls/day limit
- **Database persistence**: Weather data is stored in MongoDB for future use
- **Cache indicators**: Logs show when using cached vs fresh data

## 📱 API Endpoints

### Weather API
- `GET /api/weather/<location>` - Get weather data for location
- `GET /api/weather/analysis/<location>/<crop_type>` - Get AI weather analysis

### Market API
- `GET /api/market/prices` - Get current market prices
- `GET /api/market/analysis/<crop_type>` - Get market analysis

### Planting Calendar API
- `POST /api/planting/schedule` - Create planting schedule

### Resource Calculator API
- `POST /api/calculate/resources` - Calculate resource requirements
- `POST /api/calculate/recommendations` - Get AI recommendations

### Community API
- `GET /api/forum/posts` - Get forum posts
- `POST /api/forum/post` - Create forum post
- `POST /api/ai/advice` - Get AI farming advice

## 🌍 Supported Crops

- Maize
- Wheat
- Soybeans
- Sunflower
- Potatoes
- Tomatoes
- Onions
- Carrots
- Cabbage
- Beans

## 📍 Supported Locations

Optimized for South African farming regions:
- Cape Town
- Johannesburg
- Durban
- Pretoria
- Bloemfontein
- Port Elizabeth
- Kimberley
- Polokwane
- Nelspruit
- Upington

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for intelligent analysis
- Open-Meteo for weather data
- MongoDB for data storage
- Flask for web framework

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the community forum within the app

---

**Khula** - Empowering farmers with smart, data-driven agriculture solutions.