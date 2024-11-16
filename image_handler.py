
import os
from werkzeug.utils import secure_filename

Uploaded_image = "/home/thando/Documents/Khula/static/uploads"
# valid_extentions = {'jpeg','jpg','png'}

"""
    Save the uploaded file to the user_uploads folder.
    :param file: File object from the request.
    :return: Path to the saved file.
    """

def save_image(file):
    # folder check for now
    if not os.path.exists(Uploaded_image):
        os.makedirs(Uploaded_image)
        print(f"Saving file to: {file_path}")

    if file and file.filename.lower().endswith('.jpeg'):  # Check if file is a JPEG
        filename = secure_filename(file.filename)  # Sanitize filename
        file_path = os.path.join(Uploaded_image, filename)
        file.save(file_path)  # Save the file
        return file_path
    return None