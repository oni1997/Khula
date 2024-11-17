import os
from flask import Flask, render_template, redirect, request, url_for
from FarmingAnalysis import FarmingAnalyzer
from imageAnalysis import process_image_with_gemini
from image_handler import save_image

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
        print(f"Error initializing model: {e}")
        print(f"Error loading model: {e}")
        print("Training new model...")
        analyzer.train_model('cape_town.csv')

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
        """Handle form submission and generate predictions with structured AI recommendations"""
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
            
            # Get structured AI recommendations
            recommendations = analyzer.get_ai_recommendations(input_data, prediction)

            # Check for errors in recommendations
            if "error" in recommendations:
                return render_template(
                    'prediction_result.html',
                    location=input_data['location'],
                    plant_type=input_data['plant_type'],
                    plot_size=input_data['plot_size'],
                    harvest_month=input_data['harvest_month'],
                    yield_prediction=prediction['yield_prediction'],
                    success_rating=prediction['success_rating'],
                    error=recommendations["error"]
                )

            # If no errors, render template with all recommendations
            return render_template(
                'prediction_result.html',
                # Input data
                location=input_data['location'],
                plant_type=input_data['plant_type'],
                plot_size=input_data['plot_size'],
                harvest_month=input_data['harvest_month'],
                
                # Predictions
                yield_prediction=prediction['yield_prediction'],
                success_rating=prediction['success_rating'],
                
                # Structured recommendations
                risks=recommendations.get('risks'),
                preparations=recommendations.get('preparations'),
                variety=recommendations.get('variety'),
                care=recommendations.get('care'),
                harvest=recommendations.get('harvest'),
                upgrade_message=recommendations.get('upgrade_message')
            )

        except Exception as e:
            app.logger.error(f"Error in submit_form: {str(e)}")
            return render_template(
                'prediction_result.html',
                error=f"Error processing request: {str(e)}",
                location=input_data.get('location'),
                plant_type=input_data.get('plant_type'),
                plot_size=input_data.get('plot_size'),
                harvest_month=input_data.get('harvest_month')
            ), 500

    @app.route('/view_image/<filename>')
    def view_image(filename):
        """View processed image results"""
        return render_template('imageResultsPage.html', filename=filename)

    return app

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)