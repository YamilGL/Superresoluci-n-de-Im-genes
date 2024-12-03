import os
import shutil
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/process_image', methods=['POST'])
def process_image_endpoint():
    scale = request.form['scale']
    file = request.files['image']

    images_folder = 'images'
    os.makedirs(images_folder, exist_ok=True)

    clear_folder(images_folder)

    # Save the image in the 'images' folder with the name '001.png'
    image_path = os.path.join(images_folder, '001.png')
    file.save(image_path)

    # Process the image
    process_image(images_folder, '001.png', scale)

    # Call the command to process the image
    command_output = run_python_command(scale)

    # Build the paths of the images
    input_image_path = f"datasets/benchmark/custom/LR/{scale}/001.png"
    result_image_path = f"results/{scale}/001_CRAFT_x{scale[-1]}.png"

    return jsonify({
        "message": "Image processed successfully",
        "inputImage": input_image_path,
        "resultImage": result_image_path,
        "commandOutput": command_output
    })

@app.route('/images/<path:filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory('images', filename)

@app.route('/input/<scale>/<filename>', methods=['GET'])
def serve_input_image(scale, filename):
    folder_path = os.path.join('datasets', 'benchmark', 'custom', 'LR', scale)
    return send_from_directory(folder_path, filename)

@app.route('/results/<scale>/<filename>', methods=['GET'])
def serve_result_image(scale, filename):
    folder_path = os.path.join('results', 'CRAFT', 'custom', scale)
    return send_from_directory(folder_path, filename)

def clear_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder)

def process_image(input_folder, filename, scale):
    # Prepare the input folder
    lr_folder = os.path.join('datasets', 'benchmark', 'custom', 'LR', scale)
    clear_folder(lr_folder)

    # Save the input image in the LR folder
    input_path = os.path.join(input_folder, filename)
    output_path = os.path.join(lr_folder, filename)
    shutil.copy(input_path, output_path)

def run_python_command(scale):
    command = f'python inference/inference_CRAFT.py --input datasets/benchmark/custom/LR/{scale} --output results/CRAFT/custom/{scale} --scale {scale[-1]} --model_path experiments/pretrained_models/CRAFT_MODEL_{scale}.pth'
    
    print("START")

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        output = str(e)
    
    print("END")

    return output

if __name__ == '__main__':
    app.run(debug=True, port=5000)