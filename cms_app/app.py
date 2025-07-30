import os
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# --- Configuration ---
WEBSITE_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(WEBSITE_ROOT_PATH, 'src', 'data')
UPLOAD_FOLDER = os.path.join(WEBSITE_ROOT_PATH, 'src', 'content', 'images')

FOOTER_FILE = os.path.join(DATA_PATH, 'footer.json')
TESTIMONIALS_FILE = os.path.join(DATA_PATH, 'testimonials.json')
TEAM_FILE = os.path.join(DATA_PATH, 'team.json')


# --- Flask App Initialization ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- Helper Functions ---
def get_json_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f: return json.load(f)

def save_json_data(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)


# --- App Routes ---
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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
    return render_template('manage_testimonials.html', testimonials=get_json_data(TESTIMONIALS_FILE), active_page='testimonials')
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
        data[item_id]['feedback'] = request.form['feedback']
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
    if image_file:
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'team', filename))
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
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'team', filename))
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
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], 'team', image_to_delete))
            print(f"Deleted image file: {image_to_delete}")
        except OSError as e:
            print(f"Error deleting image file '{image_to_delete}': {e}")
    data.pop(item_id)
    save_json_data(TEAM_FILE, data)
    return redirect(url_for('manage_team'))

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