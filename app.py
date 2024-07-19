from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFilter
import io
import torch
from facenet_pytorch import MTCNN
import numpy as np
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the MTCNN model for face detection
mtcnn = MTCNN(keep_all=True, device='cuda' if torch.cuda.is_available() else 'cpu')

def draw_boxes_and_blur_faces(image, boxes):
    for box in boxes:
        xmin, ymin, xmax, ymax = box
        face_img = image.crop((xmin, ymin, xmax, ymax))
        
        # Create a mask for the face
        mask = Image.new('L', (face_img.width, face_img.height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([(0, 0), (face_img.width, face_img.height)], fill=255)
        
        # Blur the face
        blurred_face = face_img.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Composite the blurred face with the mask
        blurred_face_with_mask = Image.composite(blurred_face, face_img, mask)
        
        # Paste the blurred face back onto the image
        image.paste(blurred_face_with_mask, (int(xmin), int(ymin)))
    
    return image

@app.route('/blur', methods=['POST'])
def blur_faces():
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    try:
        image_file = request.files['file']
        image_data = Image.open(image_file.stream)

        # Perform face detection
        boxes, _ = mtcnn.detect(image_data)

        if boxes is not None:
            image_with_boxes_and_blur = draw_boxes_and_blur_faces(image_data, boxes)

            # Save the blurred image to a BytesIO object
            output = io.BytesIO()
            image_with_boxes_and_blur.save(output, format='JPEG')
            output.seek(0)

            # Save the blurred image to disk for debugging purposes
            if not os.path.exists('images'):
                os.makedirs('images')
            blurred_image_path = os.path.join('images', 'blurred_image.jpg')
            image_with_boxes_and_blur.save(blurred_image_path)

            # Return the blurred image as a response
            return send_file(output, mimetype='image/jpeg')
        else:
            return {'error': 'No faces detected'}, 400
    except Exception as e:
        print(f"Error: {e}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
