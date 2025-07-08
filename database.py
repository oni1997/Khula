import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('DB_NAME', 'khula_farming')
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
            logging.info("Successfully connected to MongoDB")
        except Exception as e:
            logging.warning(f"Failed to connect to MongoDB: {e}")
            logging.warning("Running without database - data will not be persisted")
            self.client = None
            self.db = None

    def get_collection(self, collection_name):
        """Get a specific collection"""
        if self.db is None:
            return None
        return self.db[collection_name]

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

# Collections for different features
class WeatherData:
    def __init__(self, db_manager):
        self.collection = db_manager.get_collection('weather_data')

    def save_weather_data(self, location, weather_data):
        """Save weather data for a location"""
        if self.collection is None:
            return None
        try:
            document = {
                'location': location,
                'weather_data': weather_data,
                'timestamp': datetime.utcnow(),
                'created_at': datetime.utcnow()
            }
            return self.collection.insert_one(document)
        except Exception as e:
            logging.error(f"Error saving weather data: {e}")
            return None

    def get_latest_weather(self, location):
        """Get latest weather data for a location"""
        if self.collection is None:
            return None
        try:
            return self.collection.find_one(
                {'location': location},
                sort=[('timestamp', -1)]
            )
        except Exception as e:
            logging.error(f"Error getting latest weather: {e}")
            return None

    def get_weather_for_date(self, location, date):
        """Get weather data for a specific location and date"""
        if self.collection is None:
            return None
        try:
            return self.collection.find_one({
                'location': location,
                'weather_data.date': date
            })
        except Exception as e:
            logging.error(f"Error getting weather for date: {e}")
            return None

class MarketPrices:
    def __init__(self, db_manager):
        self.collection = db_manager.get_collection('market_prices')

    def save_market_data(self, crop_type, price_data):
        """Save market price data"""
        document = {
            'crop_type': crop_type,
            'price_data': price_data,
            'timestamp': datetime.utcnow(),
            'created_at': datetime.utcnow()
        }
        return self.collection.insert_one(document)

    def get_latest_prices(self, crop_type=None):
        """Get latest market prices"""
        query = {'crop_type': crop_type} if crop_type else {}
        return list(self.collection.find(query).sort('timestamp', -1).limit(10))

class PlantingCalendar:
    def __init__(self, db_manager):
        self.collection = db_manager.get_collection('planting_calendar')

    def save_planting_schedule(self, user_id, crop_type, location, schedule_data):
        """Save planting schedule"""
        document = {
            'user_id': user_id,
            'crop_type': crop_type,
            'location': location,
            'schedule_data': schedule_data,
            'created_at': datetime.utcnow()
        }
        return self.collection.insert_one(document)

    def get_user_schedules(self, user_id):
        """Get user's planting schedules"""
        return list(self.collection.find({'user_id': user_id}))

class CommunityForum:
    def __init__(self, db_manager):
        self.posts_collection = db_manager.get_collection('forum_posts')
        self.comments_collection = db_manager.get_collection('forum_comments')

    def create_post(self, user_id, title, content, category):
        """Create a new forum post"""
        document = {
            'user_id': user_id,
            'title': title,
            'content': content,
            'category': category,
            'likes': 0,
            'views': 0,
            'created_at': datetime.utcnow()
        }
        return self.posts_collection.insert_one(document)

    def get_posts(self, category=None, limit=20):
        """Get forum posts"""
        query = {'category': category} if category else {}
        return list(self.posts_collection.find(query).sort('created_at', -1).limit(limit))

    def add_comment(self, post_id, user_id, content):
        """Add comment to a post"""
        document = {
            'post_id': post_id,
            'user_id': user_id,
            'content': content,
            'created_at': datetime.utcnow()
        }
        return self.comments_collection.insert_one(document)

class UserProfiles:
    def __init__(self, db_manager):
        self.collection = db_manager.get_collection('user_profiles')

    def create_user(self, user_data):
        """Create a new user profile"""
        user_data['created_at'] = datetime.utcnow()
        return self.collection.insert_one(user_data)

    def get_user(self, user_id):
        """Get user profile"""
        return self.collection.find_one({'_id': user_id})

    def update_user(self, user_id, update_data):
        """Update user profile"""
        update_data['updated_at'] = datetime.utcnow()
        return self.collection.update_one(
            {'_id': user_id},
            {'$set': update_data}
        )

# Initialize database manager
db_manager = DatabaseManager()
weather_db = WeatherData(db_manager)
market_db = MarketPrices(db_manager)
calendar_db = PlantingCalendar(db_manager)
forum_db = CommunityForum(db_manager)
user_db = UserProfiles(db_manager)