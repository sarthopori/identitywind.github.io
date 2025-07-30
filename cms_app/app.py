import os
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# --- Configuration ---
WEBSITE_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(WEBSITE_ROOT_PATH, 'src', 'data')
UPLOAD_FOLDER = os.path.join(WEBSITE_ROOT_PATH, 'src', 'content', 'images') # Base images folder

FOOTER_FILE = os.path.join(DATA_PATH, 'footer.json')
TESTIMONIALS_FILE = os.path.join(DATA_PATH, 'testimonials.json')
TEAM_FILE = os.path.join(DATA_PATH, 'team.json')
BANNERS_FILE = os.path.join(DATA_PATH, 'banners.json') # NEW: Path to banners data
BANNERS_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'banners') # NEW: Specific folder for banner images


# --- Flask App Initialization ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Keeping this as base if needed elsewhere


# --- Helper Functions ---
def get_json_data(filepath):
    # Ensure the file exists, if not, return empty list/dict based on common usage
    if not os.path.exists(filepath):
        # For banners, testimonials, team, offers, projects, videos, blog: it's a list
        # For footer, about, contact, services, portfolio: it's an object/dictionary
        if filepath in [BANNERS_FILE, TESTIMONIALS_FILE, TEAM_FILE, os.path.join(DATA_PATH, 'offers.json'), os.path.join(DATA_PATH, 'projects.json'), os.path.join(DATA_PATH, 'videos.json'), os.path.join(DATA_PATH, 'blog.json')]:
            return []
        else:
            return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_data(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def delete_image_file(image_filename, subfolder=""):
    """Deletes an image file from a specific subfolder within UPLOAD_FOLDER."""
    if not image_filename:
        return # Nothing to delete
    try:
        file_path = os.path.join(UPLOAD_FOLDER, subfolder, image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted image file: {file_path}")
        else:
            print(f"Image file not found for deletion: {file_path}")
    except OSError as e:
        print(f"Error deleting image file '{image_filename}': {e}") # Corrected variable name
        


# --- App Routes ---

# Serves images from the content/images directory (and its subdirectories)
@app.route('/content/images/<path:filename>')
def serve_content_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/', methods=['GET', 'POST'])
def edit_footer():
    if request.method == 'POST':
        data = get_json_data(FOOTER_FILE)
        data['email'] = request.form['email']
        data['copyright_text'] = request.form['copyright_text']
        save_json_data(FOOTER_FILE, data)
        return redirect(url_for('edit_footer'))
    return render_template('edit_footer.html', data=get_json_data(FOOTER_FILE), active_page='footer')

@app.route('/testimonials')
def manage_testimonials():
    # Sort testimonials by name for consistent display in CMS
    testimonials_data = get_json_data(TESTIMONIALS_FILE)
    # If you want newest first, you might need a 'timestamp' field in your JSON,
    # or you can just reverse the list here: testimonials_data.reverse()
    # For now, let's keep it in the order it was added or by name if needed.
    return render_template('manage_testimonials.html', testimonials=testimonials_data, active_page='testimonials')
@app.route('/testimonials/add', methods=['POST'])
def add_testimonial():
    data = get_json_data(TESTIMONIALS_FILE)
    data.append({"client_name": request.form['client_name'], "feedback": request.form['feedback']})
    save_json_data(TESTIMONIALS_FILE, data)
    return redirect(url_for('manage_testimonials'))
@app.route('/testimonials/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_testimonial(item_id):
    data = get_json_data(TESTIMONIALS_FILE)
    if request.method == 'POST':
        data[item_id]['client_name'] = request.form['client_name']
        data[item_id]['feedback'] = request.form['feedback'] # Corrected: Removed extra 'item'
        save_json_data(TESTIMONIALS_FILE, data)
        return redirect(url_for('manage_testimonials'))
    return render_template('edit_testimonial.html', testimonial=data[item_id], active_page='testimonials')
@app.route('/testimonials/delete/<int:item_id>', methods=['POST'])
def delete_testimonial(item_id):
    data = get_json_data(TESTIMONIALS_FILE)
    data.pop(item_id)
    save_json_data(TESTIMONIALS_FILE, data)
    return redirect(url_for('manage_testimonials'))

@app.route('/team')
def manage_team():
    return render_template('manage_team.html', team=get_json_data(TEAM_FILE), active_page='team')
@app.route('/team/add', methods=['POST'])
def add_team_member():
    data = get_json_data(TEAM_FILE)
    image_file = request.files.get('image')
    filename = ""
    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        # Ensure the 'team' subfolder exists before saving
        os.makedirs(os.path.join(UPLOAD_FOLDER, 'team'), exist_ok=True)
        image_file.save(os.path.join(UPLOAD_FOLDER, 'team', filename))
    new_member = {"name": request.form['name'],"title": request.form['title'],"bio": request.form.get('bio', ''),"image": filename,"is_ceo": 'is_ceo' in request.form}
    data.append(new_member)
    save_json_data(TEAM_FILE, data)
    return redirect(url_for('manage_team'))
@app.route('/team/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_team_member(item_id):
    data = get_json_data(TEAM_FILE)
    member_to_edit = data[item_id]
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            # Delete old image if it exists and a new one is uploaded
            if member_to_edit.get('image'):
                delete_image_file(member_to_edit['image'], subfolder='team')

            filename = secure_filename(image_file.filename)
            os.makedirs(os.path.join(UPLOAD_FOLDER, 'team'), exist_ok=True)
            image_file.save(os.path.join(UPLOAD_FOLDER, 'team', filename))
            member_to_edit['image'] = filename
        member_to_edit['name'] = request.form['name']
        member_to_edit['title'] = request.form['title']
        member_to_edit['bio'] = request.form.get('bio', '')
        member_to_edit['is_ceo'] = 'is_ceo' in request.form
        save_json_data(TEAM_FILE, data)
        return redirect(url_for('manage_team'))
    return render_template('edit_team_member.html', member=member_to_edit, active_page='team')
@app.route('/team/delete/<int:item_id>', methods=['POST'])
def delete_team_member(item_id):
    data = get_json_data(TEAM_FILE)
    image_to_delete = data[item_id].get('image')
    if image_to_delete:
        delete_image_file(image_to_delete, subfolder='team')
    data.pop(item_id)
    save_json_data(TEAM_FILE, data)
    return redirect(url_for('manage_team'))


# --- NEW: Banner Management Routes ---
@app.route('/banners')
def manage_banners():
    banners_data = get_json_data(BANNERS_FILE)
    return render_template('manage_banners.html', banners=banners_data, active_page='banners')

@app.route('/banners/add', methods=['GET', 'POST'])
def add_banner():
    if request.method == 'POST':
        data = get_json_data(BANNERS_FILE)
        image_file = request.files.get('image')
        filename = ""
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            # Ensure the 'banners' subfolder exists before saving
            os.makedirs(BANNERS_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(BANNERS_UPLOAD_FOLDER, filename))
        
        # Only saving the image filename as per your last clarification
        new_banner = {"image": filename}
        data.append(new_banner)
        save_json_data(BANNERS_FILE, data)
        return redirect(url_for('manage_banners'))
    return render_template('add_edit_banner.html', active_page='banners', title="Add New Banner")

@app.route('/banners/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_banner(item_id):
    data = get_json_data(BANNERS_FILE)
    banner_to_edit = data[item_id]
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            # Delete old banner image if it exists and a new one is uploaded
            if banner_to_edit.get('image'):
                delete_image_file(banner_to_edit['image'], subfolder='banners')

            filename = secure_filename(image_file.filename)
            os.makedirs(BANNERS_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(BANNERS_UPLOAD_FOLDER, filename))
            banner_to_edit['image'] = filename
        save_json_data(BANNERS_FILE, data)
        return redirect(url_for('manage_banners'))
    # --- THIS LINE WAS THE CRUCIAL CHANGE ---
    return render_template('add_edit_banner.html', active_page='banners', banner=banner_to_edit, banner_id=item_id, title="Edit Banner")

@app.route('/banners/delete/<int:item_id>', methods=['POST'])
def delete_banner(item_id):
    data = get_json_data(BANNERS_FILE)
    image_to_delete = data[item_id].get('image')
    if image_to_delete:
        delete_image_file(image_to_delete, subfolder='banners')
    data.pop(item_id)
    save_json_data(BANNERS_FILE, data)
    return redirect(url_for('manage_banners'))

# --- NEW DEPLOY ROUTE FOR PHASE 4 ---
@app.route('/deploy', methods=['GET', 'POST'])
def deploy():
    output = ""
    if request.method == 'POST':
        commit_message = request.form.get('commit_message', 'Updated website content via CMS')
        try:
            output += ">>> Running build.py...\n"
            build_process = subprocess.run(['python', 'build.py'], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += build_process.stdout + "\n"
            output += build_process.stderr + "\n"
            
            output += ">>> Running git add . ...\n"
            add_process = subprocess.run(['git', 'add', '.'], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += add_process.stdout + "\n"

            output += f">>> Running git commit -m \"{commit_message}\"...\n"
            commit_process = subprocess.run(['git', 'commit', '-m', commit_message], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += commit_process.stdout + "\n"

            output += ">>> Running git push...\n"
            push_process = subprocess.run(['git', 'push'], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += push_process.stdout + "\n"
            output += push_process.stderr + "\n"
            
            output += "\n✅ DEPLOYMENT SUCCESSFUL! ✅\nYour website is now live."
            
        except subprocess.CalledProcessError as e:
            output += f"\n\n❌ DEPLOYMENT FAILED! ❌\n"
            output += f"Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}.\n"
            output += "\n--- STDOUT ---\n" + e.stdout
            output += "\n--- STDERR ---\n" + e.stderr
            
    return render_template('deploy.html', output=output, active_page='deploy')

# --- Run the App ---
if __name__ == '__main__':
    print("===================================================")
    print("Starting your local Content Management Server...")
    print("Open your web browser and go to: http://127.0.0.1:5000")
    print("===================================================")
    app.run(port=5000, debug=True)