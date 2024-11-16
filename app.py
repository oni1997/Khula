from flask import Flask, render_template,redirect, request
from image_handler import save_image


app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('index.html')  #Ensure your landing page is named 'index.html'

@app.route('/upload', methods=['GET','POST']) #updated with image handling.
def upload():
    if request.method == 'POST':
        # Get form data
        image_type = request.form['imageType']
        image_file = request.files['imageUpload']
        saved_path = save_image(image_file) #save only jpeg img's for now

        #type error handler:
        if saved_path:
            print("Success, file is here: {saved_path}")
        else:
            print("Error, file not saved")

    return render_template('ImageAnalysis.html')

@app.route('/analysis') #link in js
def analysis():
    return render_template('FarmingAnalysis.html')

if __name__ == '__main__':
    app.run(debug=True)