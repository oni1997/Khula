from flask import Flask, render_template,redirect, request, url_for
from image_handler import save_image


app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('index.html')  #Ensure your landing page is named 'index.html'

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


@app.route('/view_image/<filename>')
def view_image(filename):
    
    return render_template('imageResultsPage.html', filename=filename)

@app.route('/analysis') #link in js
def analysis():
    return render_template('FarmingAnalysis.html')

if __name__ == '__main__':
    app.run(debug=True)