from flask import Flask,render_template, request,redirect, url_for
from werkzeug.utils import secure_filename
import os
from prediction import predict
from flask_cors import CORS



UPLOAD_FOLDER = r'D:\app\images_uploded'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg'}

def image_prediction(image_path):
    result = predict(image_path)
    result_path = result.print_out()
    return result_path


app = Flask(__name__)
cors = CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
@cross_origin()

def index():
    return render_template('index.html')

@app.route('/uploader',methods=['GET','POST'])
def uploader():  
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        result_path = image_prediction(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print(path)
        result_path = os.path.basename(result_path)
        print(result_path)
        return render_template('result.html',path=result_path)
        
        

if __name__ == '__main__':
    PORT = os.environ.get("PORT",5000)
    app.run(host='0.0.0.0',port=PORT)