import os
from flask import Flask, render_template, redirect, request, url_for, jsonify, session
from FarmingAnalysis import FarmingAnalyzer
from imageAnalysis import process_image_with_gemini
from image_handler import save_image

# Import new services
from weather_service import weather_service
from market_service import market_service
from planting_calendar import planting_service
from resource_calculator import resource_calculator
from community_service import community_service

# Load environment variables

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Initialize FarmingAnalyzer with Gemini API key
    analyzer = FarmingAnalyzer()

    # Initialize or train the model
    try:
        analyzer.load_model()
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Training new model with simulated data...")
        try:
            analyzer.train_model_with_simulated_data()
        except Exception as train_error:
            print(f"Error training model: {train_error}")
            print("Continuing without ML model - using basic predictions")

    @app.route('/')
    def landing():
        """Landing page route"""
        return render_template('index.html')

    @app.route('/form')
    def form():
        """Form page route"""
        return render_template('farmingAnalysis.html')

    @app.route('/analysis')
    def analysis():
        """Analysis page route"""
        return render_template('FarmingAnalysis.html')

    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        """Handle image upload and analysis"""
        if request.method == 'POST':
            try:
                # Get form data
                image_type = request.form['imageType']
                image_file = request.files['imageUpload']
                
                # Save the image
                saved_path = save_image(image_file)
                
                if not saved_path:
                    return render_template('ImageAnalysis.html', error="Failed to save image")
                
                try:
                    # Process the image with Gemini
                    analysis_result = process_image_with_gemini(saved_path)
                    
                    # Clean up - delete the image after processing
                    try:
                        os.remove(saved_path)
                        print(f"Successfully deleted {saved_path}")
                    except Exception as e:
                        print(f"Warning: Error deleting file: {e}")
                    
                    return render_template(
                        'analysis_result.html',
                        analysis=analysis_result,
                        image_type=image_type
                    )
                
                except Exception as e:
                    # Clean up on error
                    if os.path.exists(saved_path):
                        os.remove(saved_path)
                    raise e
                    
            except Exception as e:
                return render_template(
                    'ImageAnalysis.html',
                    error=f"Error processing image: {str(e)}"
                )
                
        return render_template('ImageAnalysis.html')

    @app.route('/submit_form', methods=['POST'])
    def submit_form():
        """Handle form submission and generate predictions"""
        try:
            # Get form data
            input_data = {
                'location': request.form.get('location'),
                'plant_type': request.form.get('plantType'),
                'plot_size': request.form.get('plotSize'),
                'harvest_month': request.form.get('harvestMonth')
            }

            # Validate required fields
            if not input_data['location'] or not input_data['plant_type']:
                return "Error: Location and Plant Type are required!", 400

            # Make prediction
            prediction = analyzer.predict(input_data)
            
            # Get AI recommendations
            ai_recommendations = analyzer.get_ai_recommendations(input_data, prediction)

            return render_template(
                'prediction_result.html',
                location=input_data['location'],
                plant_type=input_data['plant_type'],
                plot_size=input_data['plot_size'],
                harvest_month=input_data['harvest_month'],
                yield_prediction=prediction['yield_prediction'],
                success_rating=prediction['success_rating'],
                ai_recommendations=ai_recommendations
            )

        except Exception as e:
            return f"Error processing request: {str(e)}", 500

    @app.route('/view_image/<filename>')
    def view_image(filename):
        """View processed image results"""
        return render_template('imageResultsPage.html', filename=filename)

    # Weather Routes
    @app.route('/weather')
    def weather_dashboard():
        """Weather dashboard page"""
        return render_template('weather_dashboard.html')

    @app.route('/api/weather/<location>')
    def get_weather_api(location):
        """API endpoint for weather data"""
        weather_data = weather_service.get_current_weather(location)
        return jsonify(weather_data)

    @app.route('/api/weather/analysis/<location>/<crop_type>')
    def get_weather_analysis_api(location, crop_type):
        """API endpoint for weather analysis"""
        try:
            analysis = weather_service.get_farming_weather_analysis(location, crop_type)
            if analysis:
                return jsonify({'analysis': analysis})
            else:
                return jsonify({'error': 'Unable to generate weather analysis'}), 500
        except Exception as e:
            return jsonify({'error': f'Weather analysis error: {str(e)}'}), 500

    # Market Routes
    @app.route('/market')
    def market_dashboard():
        """Market prices dashboard"""
        return render_template('market_dashboard.html')

    @app.route('/api/market/prices')
    def get_market_prices_api():
        """API endpoint for market prices"""
        prices = market_service.get_simulated_market_prices()
        return jsonify(prices)

    @app.route('/api/market/analysis/<crop_type>')
    def get_market_analysis_api(crop_type):
        """API endpoint for market analysis"""
        analysis = market_service.get_market_analysis(crop_type)
        return jsonify({'analysis': analysis})

    # Planting Calendar Routes
    @app.route('/calendar')
    def planting_calendar():
        """Planting calendar page"""
        return render_template('planting_calendar.html')

    @app.route('/api/planting/schedule', methods=['POST'])
    def create_planting_schedule():
        """Create planting schedule"""
        data = request.get_json()
        schedule = planting_service.get_optimal_planting_dates(
            data['crop_type'],
            data['location'],
            data.get('plot_size')
        )
        return jsonify(schedule)

    # Resource Calculator Routes
    @app.route('/calculator')
    def resource_calculator_page():
        """Resource calculator page"""
        return render_template('resource_calculator.html')

    @app.route('/api/calculate/resources', methods=['POST'])
    def calculate_resources_api():
        """Calculate resource requirements"""
        data = request.get_json()
        calculations = resource_calculator.calculate_resources(
            data['crop_type'],
            data['plot_size_ha'],
            data.get('soil_type', 'medium'),
            data.get('irrigation_type', 'drip')
        )
        return jsonify(calculations)

    @app.route('/api/calculate/recommendations', methods=['POST'])
    def get_resource_recommendations():
        """Get AI resource recommendations"""
        data = request.get_json()
        recommendations = resource_calculator.get_ai_resource_recommendations(
            data['crop_type'],
            data['plot_size_ha'],
            data['soil_type'],
            data['location'],
            data.get('budget')
        )
        return jsonify(recommendations)

    # Community Routes
    @app.route('/community')
    def community_forum():
        """Community forum page"""
        return render_template('community_forum.html')

    @app.route('/api/forum/posts')
    def get_forum_posts():
        """Get forum posts"""
        category = request.args.get('category')
        posts = community_service.get_forum_posts(category)
        return jsonify(posts)

    @app.route('/api/forum/post', methods=['POST'])
    def create_forum_post():
        """Create a new forum post"""
        data = request.get_json()
        result = community_service.create_forum_post(
            data['user_id'],
            data['title'],
            data['content'],
            data['category']
        )
        return jsonify(result)

    @app.route('/api/ai/advice', methods=['POST'])
    def get_ai_advice():
        """Get AI farming advice"""
        data = request.get_json()
        advice = community_service.get_ai_farming_advice(
            data['question'],
            data.get('category', 'general')
        )
        return jsonify({'advice': advice})

    return app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)