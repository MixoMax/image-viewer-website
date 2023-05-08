from flask import Flask, url_for
import requests
import PIL
import PIL.Image
import os
import json


db_path = r"C:\Users\Linus\Pictures"

def update_image_index(db_path, depth=0):
    image_dict = {}

    # If depth is 0, only process the files in the current directory
    if depth == 0:
        os.chdir(db_path)
        for file in os.listdir():
            if file.split(".")[-1] in ["jpg", "png", "jpeg", "ico"]:
                file_name, file_extension = os.path.splitext(file)
                img = PIL.Image.open(file)
                width, height = img.size

                image_dict[file_name] = {
                    "path": os.path.join(db_path, file),
                    "width": width,
                    "height": height,
                    "file_name": file_name,
                    "file_extension": file_extension
                }

    # If depth is greater than 0, process files in the current directory and all subdirectories up to the given depth
    elif depth > 0:
        for root, dirs, files in os.walk(db_path):
            current_depth = root[len(db_path) + len(os.sep):].count(os.sep)
            if current_depth > depth:
                continue

            for file in files:
                if file.split(".")[-1] in ["jpg", "png", "jpeg", "ico"]:
                    file_name, file_extension = os.path.splitext(file)
                    img = PIL.Image.open(os.path.join(root, file))
                    width, height = img.size

                    image_dict[file_name] = {
                        "path": os.path.join(root, file),
                        "width": width,
                        "height": height,
                        "file_name": file_name,
                        "file_extension": file_extension
                    }

    return image_dict

def save_image_index(image_dict):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("image_index.json", "w") as f:
        json.dump(image_dict, f)
    return "Image index saved", 200

def get_all_images():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    file_list = []
    with open("image_index.json", "r") as f:
        image_dict = json.load(f)
        for key, value in image_dict.items():
            file_list.append((value["path"], value["file_name"]))
    
    html_string = ""
    num_images_per_row = 4
    last_images = []
    len_file_list = len(file_list)
    i = -1
    for file in file_list:
        i += 1
        if os.path.isfile(os.path.dirname(os.path.abspath(__file__)) + "\\static\\" + file[1] + ".jpg") == False:
            copy_image_to_static(file[1])
            print("images saved", i, "/", len_file_list, "(", str(int((i/len_file_list)*100)), "%)")
        html_string += f"<img style = 'width: {str(int((1/num_images_per_row)*100))}%; height: auto;' src='" + url_for('static', filename=file[1] + ".jpg") + "'/>"
        last_images.append("/images/show/" + file[1])
        if len(last_images) == num_images_per_row:
            html_string += "<br>"
            for link in last_images:
                html_string += "<a href='" + link + f"' style = 'width: {str(int((1/num_images_per_row)*100))}%; height: auto; padding: {str((1/num_images_per_row)*50)}%;'>"+ "link" +  "</a>"
            html_string += "<br>"
            last_images = []
        
    return html_string
    

def get_image_by_id(image_id):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("image_index.json", "r") as f:
        image_dict = json.load(f)
        try:
            return image_dict[image_id], 200
        except KeyError:
            return "Image not found", 404

def copy_image_to_static(image_id):
    image_path = get_image_by_id(image_id)[0]["path"]
    
    img = PIL.Image.open(image_path)
    width, height = img.size
    mult = 512/width
    img = img.resize((int(width*mult), int(height*mult))).convert("RGB")
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "\\static")
    img.save(image_id + ".jpg")
    
    new_image_path = os.path.dirname(os.path.abspath(__file__)) + "\\static\\" + image_id + ".jpg"
    return new_image_path

def clear_static_images():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.remove("image_index.json")
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "\\static")
    for file in os.listdir():
        if file.endswith(".jpg"):
            os.remove(file)
    return "Images cleared", 200



app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/images/all")
def get_images():
    return get_all_images()

@app.route("/images/update")
def update_images():
    image_dict = update_image_index(db_path, depth=100)
    response = save_image_index(image_dict)
    return response

@app.route("/images/<image_id>")
def get_image(image_id):
    return json.dumps(get_image_by_id(image_id))

@app.route("/images/show/<image_id>")
def show_image(image_id):
    new_image_path = copy_image_to_static(image_id)
    image_url = url_for('static', filename=image_id + ".jpg")
    return "<img style = 'width: 100%; height: auto;' src='" + image_url + "'/>"

@app.route("/images/clear")
def clear_images():
    return clear_static_images()

@app.route("/ip")
def get_ip():
    return requests.get('https://api.ipify.org').text


if __name__ == "__main__":
    app.run(debug=True)