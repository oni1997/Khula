from flask import Flask, render_template,redirect, request, url_for
from image_handler import save_image


app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('index.html')  

# ------
@app.route('/upload', methods=['GET','POST']) #updated with image handling.
def upload():
    if request.method == 'POST':
        # Get form data
        # image_type = request.form['imageType']
        image_file = request.files['imageUpload']
        saved_path = save_image(image_file) #save only jpeg img's for now


        #re routing image to new page:
        if saved_path:
            filename = saved_path.split('/')[-1]
            return redirect(url_for('view_image', filename=filename))
            
        else:
            print("Error, file not saved")

    return render_template('ImageAnalysis.html')

# ------  
@app.route('/form', methods=['GET'])
def form():
    return render_template('farmingAnalysis.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    # data for user input set
    location = request.form.get('location')
    plant_type = request.form.get('plantType')
    plot_size = request.form.get('plotSize')
    harvest_month = request.form.get('harvestMonth')

    # Check for compulsory fields
    if not location or not plant_type:
        return "Error: Location and Plant Type are required!", 400

    # Process form data (print for now)
    print(f"Location: {location}")
    print(f"Plant Type: {plant_type}")
    print(f"Plot Size: {plot_size}")
    print(f"Harvest Month: {harvest_month}")

    # Redirect or display a confirmation (for now)
    return f"Form submitted successfully! Location: {location}, Plant Type: {plant_type}, Plot Size: {plot_size}, Harvest Month: {harvest_month}"


# ------
@app.route('/view_image/<filename>')
def view_image(filename):
    
    return render_template('imageResultsPage.html', filename=filename)

@app.route('/analysis') #link in js
def analysis():
    return render_template('FarmingAnalysis.html')

if __name__ == '__main__':
    app.run(debug=True)