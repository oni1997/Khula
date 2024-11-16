from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def landing():
    return render_template('index.html')  #Ensure your landing page is named 'index.html'

@app.route('/upload') #link in js
def upload():
    return render_template('ImageAnalysis.html')

@app.route('/analysis') #link in js
def analysis():
    return render_template('FarmingAnalysis.html')

if __name__ == '__main__':
    app.run(debug=True)