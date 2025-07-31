import os
import json
import subprocess
import shutil
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from datetime import datetime

# --- Configuration ---
WEBSITE_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(WEBSITE_ROOT_PATH, 'src', 'data')
CONTENT_DIR = os.path.join(WEBSITE_ROOT_PATH, 'src', 'content')
UPLOAD_FOLDER = os.path.join(CONTENT_DIR, 'images')

# --- Data File Paths ---
FOOTER_FILE = os.path.join(DATA_PATH, 'footer.json')
TESTIMONIALS_FILE = os.path.join(DATA_PATH, 'testimonials.json')
TEAM_FILE = os.path.join(DATA_PATH, 'team.json')
BANNERS_FILE = os.path.join(DATA_PATH, 'banners.json')
OFFERS_FILE = os.path.join(DATA_PATH, 'offers.json')
PROJECTS_FILE = os.path.join(DATA_PATH, 'projects.json')
VIDEOS_FILE = os.path.join(DATA_PATH, 'videos.json')
ABOUT_FILE = os.path.join(DATA_PATH, 'about.json')
SERVICES_FILE = os.path.join(DATA_PATH, 'services.json')
CONTACT_FILE = os.path.join(DATA_PATH, 'contact.json')
PORTFOLIO_FILE = os.path.join(DATA_PATH, 'portfolio.json')
BLOG_FILE = os.path.join(DATA_PATH, 'blog.json')
CLIENTS_FILE = os.path.join(DATA_PATH, 'clients.json')
NAVIGATION_FILE = os.path.join(DATA_PATH, 'navigation.json')
STYLES_FILE = os.path.join(DATA_PATH, 'styles.json')

# --- Image Upload Subfolders ---
TEAM_UPLOAD_FOLDER, BANNERS_UPLOAD_FOLDER, OFFERS_UPLOAD_FOLDER, PROJECTS_UPLOAD_FOLDER, BLOG_UPLOAD_FOLDER, PORTFOLIO_UPLOAD_FOLDER, CLIENTS_UPLOAD_FOLDER = [
    os.path.join(UPLOAD_FOLDER, d) for d in 
    ['team', 'banners', 'offers', 'projects', 'blog', 'portfolio', 'clients']
]
BLOG_CONTENT_DIR = os.path.join(CONTENT_DIR, 'blog')

# --- Flask App Initialization ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_final_working_secret_key'

# --- Helper Functions ---
def get_json_data(filepath):
    list_files = [BANNERS_FILE, TESTIMONIALS_FILE, TEAM_FILE, OFFERS_FILE, PROJECTS_FILE, VIDEOS_FILE, BLOG_FILE, PORTFOLIO_FILE, CLIENTS_FILE, NAVIGATION_FILE]
    if not os.path.exists(filepath): return [] if filepath in list_files else {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content: return [] if filepath in list_files else {}
            return json.loads(content)
    except json.JSONDecodeError: return [] if filepath in list_files else {}

def save_json_data(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)

def delete_image_file(image_filename, subfolder=""):
    if not image_filename: return
    try:
        path = os.path.join(UPLOAD_FOLDER, subfolder, image_filename) if subfolder else os.path.join(UPLOAD_FOLDER, image_filename)
        if os.path.exists(path): os.remove(path)
    except OSError as e: print(f"Error deleting file '{path}': {e}")

# --- App Routes ---
@app.route('/content/images/<path:filename>')
def serve_content_image(filename): return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def index(): return redirect(url_for('manage_navigation'))

# --- Navigation ---
@app.route('/navigation', methods=['GET'])
def manage_navigation():
    return render_template('manage_navigation.html', navigation=get_json_data(NAVIGATION_FILE), active_page='navigation', title="Manage Navigation")
@app.route('/navigation/add', methods=['POST'])
def add_nav_item():
    data = get_json_data(NAVIGATION_FILE); data.append({"label": request.form['label'], "url": request.form['url'], "id": request.form['id']}); save_json_data(NAVIGATION_FILE, data); flash('Item added!', 'success'); return redirect(url_for('manage_navigation'))
@app.route('/navigation/update_all', methods=['POST'])
def update_all_nav_items():
    data = []; labels, urls, ids = request.form.getlist('label'), request.form.getlist('url'), request.form.getlist('id')
    for i in range(len(labels)): data.append({"label": labels[i], "url": urls[i], "id": ids[i]})
    save_json_data(NAVIGATION_FILE, data); flash('Navigation updated!', 'success'); return redirect(url_for('manage_navigation'))
@app.route('/navigation/delete/<int:item_id>', methods=['POST'])
def delete_nav_item(item_id):
    data = get_json_data(NAVIGATION_FILE)
    if 0 <= item_id < len(data): data.pop(item_id); save_json_data(NAVIGATION_FILE, data); flash('Item deleted.', 'success')
    return redirect(url_for('manage_navigation'))
@app.route('/navigation/move/<int:item_id>/<direction>', methods=['POST'])
def move_nav_item(item_id, direction):
    data = get_json_data(NAVIGATION_FILE)
    if 0 <= item_id < len(data):
        if direction == 'up' and item_id > 0: data[item_id], data[item_id - 1] = data[item_id - 1], data[item_id]
        elif direction == 'down' and item_id < len(data) - 1: data[item_id], data[item_id + 1] = data[item_id + 1], data[item_id]
        save_json_data(NAVIGATION_FILE, data)
    return redirect(url_for('manage_navigation'))

# --- Theme Settings ---
@app.route('/theme_settings', methods=['GET', 'POST'])
def edit_theme_settings():
    if request.method == 'POST':
        data = {"google_font_url": request.form['google_font_url'], "body_font_family": request.form['body_font_family'], "heading_font_family": request.form['heading_font_family'], "heading_font_size_px": int(request.form['heading_font_size_px'])}
        save_json_data(STYLES_FILE, data); flash('Theme settings updated!', 'success'); return redirect(url_for('edit_theme_settings'))
    return render_template('edit_theme_settings.html', data=get_json_data(STYLES_FILE), active_page='theme_settings', title="Theme Settings")

# --- All Other Routes ---
@app.route('/footer', methods=['GET', 'POST'])
def edit_footer():
    if request.method == 'POST':
        data = {'email': request.form['email'], 'copyright_text': request.form['copyright_text'], 'social_links': []}
        names, urls = request.form.getlist('social_name'), request.form.getlist('social_url')
        for i in range(len(names)):
            if names[i] and urls[i]: data['social_links'].append({'name': names[i], 'url': urls[i]})
        save_json_data(FOOTER_FILE, data); flash('Footer updated!', 'success'); return redirect(url_for('edit_footer'))
    return render_template('edit_footer.html', data=get_json_data(FOOTER_FILE), active_page='footer', title="Edit Footer")

@app.route('/testimonials')
def manage_testimonials(): return render_template('manage_testimonials.html', testimonials=get_json_data(TESTIMONIALS_FILE), active_page='testimonials', title="Manage Testimonials")
# ... All Testimonial add/edit/delete routes are here ...
@app.route('/testimonials/add', methods=['GET', 'POST'])
def add_testimonial():
    if request.method == 'POST':
        data = get_json_data(TESTIMONIALS_FILE); filename = ""
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(TEAM_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(TEAM_UPLOAD_FOLDER, filename))
        data.append({"feedback": request.form['feedback'], "stars": int(request.form['stars']), "image": filename, "client_name": request.form['client_name'], "client_company": request.form['client_company']})
        save_json_data(TESTIMONIALS_FILE, data); flash('Testimonial added!', 'success'); return redirect(url_for('manage_testimonials'))
    return render_template('add_edit_testimonial.html', active_page='testimonials', title="Add New Testimonial")
@app.route('/testimonials/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_testimonial(item_id):
    data = get_json_data(TESTIMONIALS_FILE)
    if not 0 <= item_id < len(data): abort(404)
    item = data[item_id]
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename != '':
            delete_image_file(item.get('image'), 'team'); image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(TEAM_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(TEAM_UPLOAD_FOLDER, filename)); item['image'] = filename
        item['feedback'] = request.form['feedback']; item['stars'] = int(request.form['stars']); item['client_name'] = request.form['client_name']; item['client_company'] = request.form['client_company']
        save_json_data(TESTIMONIALS_FILE, data); flash('Testimonial updated!', 'success'); return redirect(url_for('manage_testimonials'))
    return render_template('add_edit_testimonial.html', testimonial=item, testimonial_id=item_id, active_page='testimonials', title="Edit Testimonial")
@app.route('/testimonials/delete/<int:item_id>', methods=['POST'])
def delete_testimonial(item_id):
    data = get_json_data(TESTIMONIALS_FILE)
    if 0 <= item_id < len(data): delete_image_file(data[item_id].get('image'), 'team'); data.pop(item_id); save_json_data(TESTIMONIALS_FILE, data); flash('Testimonial deleted.', 'success')
    return redirect(url_for('manage_testimonials'))

# ... All other routes from your original app.py are here and complete ...
@app.route('/clients')
def manage_clients(): return render_template('manage_clients.html', clients=get_json_data(CLIENTS_FILE), active_page='clients', title="Manage Clients")
@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        data = get_json_data(CLIENTS_FILE); filename = ""
        if 'logo' in request.files and request.files['logo'].filename != '':
            image_file = request.files['logo']; filename = secure_filename(image_file.filename); os.makedirs(CLIENTS_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(CLIENTS_UPLOAD_FOLDER, filename))
        data.append({"logo": filename, "url": request.form['url']}); save_json_data(CLIENTS_FILE, data); flash('Client logo added.', 'success'); return redirect(url_for('manage_clients'))
    return render_template('add_edit_client.html', active_page='clients', title="Add New Client Logo")
@app.route('/clients/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_client(item_id):
    data = get_json_data(CLIENTS_FILE)
    if not 0 <= item_id < len(data): return redirect(url_for('manage_clients'))
    item = data[item_id]
    if request.method == 'POST':
        if 'logo' in request.files and request.files['logo'].filename != '':
            delete_image_file(item.get('logo'), 'clients'); image_file = request.files['logo']; filename = secure_filename(image_file.filename); os.makedirs(CLIENTS_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(CLIENTS_UPLOAD_FOLDER, filename)); item['logo'] = filename
        item['url'] = request.form['url']; save_json_data(CLIENTS_FILE, data); flash('Client logo updated.', 'success'); return redirect(url_for('manage_clients'))
    return render_template('add_edit_client.html', client=item, client_id=item_id, active_page='clients', title="Edit Client Logo")
@app.route('/clients/delete/<int:item_id>', methods=['POST'])
def delete_client(item_id):
    data = get_json_data(CLIENTS_FILE)
    if 0 <= item_id < len(data): delete_image_file(data[item_id].get('logo'), 'clients'); data.pop(item_id); save_json_data(CLIENTS_FILE, data); flash('Client logo deleted.', 'success')
    return redirect(url_for('manage_clients'))

@app.route('/team')
def manage_team(): return render_template('manage_team.html', team=get_json_data(TEAM_FILE), active_page='team', title="Manage Team")
@app.route('/team/add', methods=['POST'])
def add_team_member():
    data = get_json_data(TEAM_FILE); filename = ""
    if 'image' in request.files and request.files['image'].filename != '':
        image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(TEAM_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(TEAM_UPLOAD_FOLDER, filename))
    data.append({"name": request.form['name'], "title": request.form['title'], "bio": request.form.get('bio', ''), "image": filename, "is_ceo": 'is_ceo' in request.form})
    save_json_data(TEAM_FILE, data); flash('Team member added!', 'success'); return redirect(url_for('manage_team'))
@app.route('/team/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_team_member(item_id):
    data = get_json_data(TEAM_FILE)
    if not 0 <= item_id < len(data): return redirect(url_for('manage_team'))
    member = data[item_id]
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename != '':
            delete_image_file(member.get('image'), 'team'); image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(TEAM_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(TEAM_UPLOAD_FOLDER, filename)); member['image'] = filename
        member['name'] = request.form['name']; member['title'] = request.form['title']; member['bio'] = request.form.get('bio', ''); member['is_ceo'] = 'is_ceo' in request.form
        save_json_data(TEAM_FILE, data); flash('Team member updated!', 'success'); return redirect(url_for('manage_team'))
    return render_template('edit_team_member.html', member=member, item_id=item_id, active_page='team', title="Edit Team Member")
@app.route('/team/delete/<int:item_id>', methods=['POST'])
def delete_team_member(item_id):
    data = get_json_data(TEAM_FILE)
    if 0 <= item_id < len(data): delete_image_file(data[item_id].get('image'), 'team'); data.pop(item_id); save_json_data(TEAM_FILE, data); flash('Team member deleted.', 'success')
    return redirect(url_for('manage_team'))

@app.route('/banners')
def manage_banners(): return render_template('manage_banners.html', banners=get_json_data(BANNERS_FILE), active_page='banners', title="Manage Banners")
@app.route('/banners/add', methods=['GET', 'POST'])
def add_banner():
    if request.method == 'POST':
        data = get_json_data(BANNERS_FILE); filename = ""
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(BANNERS_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(BANNERS_UPLOAD_FOLDER, filename))
        data.append({"image": filename}); save_json_data(BANNERS_FILE, data); flash('Banner added!', 'success'); return redirect(url_for('manage_banners'))
    return render_template('add_edit_banner.html', active_page='banners', title="Add New Banner")
@app.route('/banners/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_banner(item_id):
    data = get_json_data(BANNERS_FILE)
    if not 0 <= item_id < len(data): return redirect(url_for('manage_banners'))
    banner = data[item_id]
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename != '':
            delete_image_file(banner.get('image'), 'banners'); image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(BANNERS_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(BANNERS_UPLOAD_FOLDER, filename)); banner['image'] = filename
        save_json_data(BANNERS_FILE, data); flash('Banner updated!', 'success'); return redirect(url_for('manage_banners'))
    return render_template('add_edit_banner.html', banner=banner, banner_id=item_id, active_page='banners', title="Edit Banner")
@app.route('/banners/delete/<int:item_id>', methods=['POST'])
def delete_banner(item_id):
    data = get_json_data(BANNERS_FILE)
    if 0 <= item_id < len(data): delete_image_file(data[item_id].get('image'), 'banners'); data.pop(item_id); save_json_data(BANNERS_FILE, data); flash('Banner deleted.', 'success')
    return redirect(url_for('manage_banners'))

@app.route('/offers')
def manage_offers(): return render_template('manage_offers.html', offers=get_json_data(OFFERS_FILE), active_page='offers', title="Manage Offers")
@app.route('/offers/add', methods=['GET', 'POST'])
def add_offer():
    if request.method == 'POST':
        data = get_json_data(OFFERS_FILE); filename = ""
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(OFFERS_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(OFFERS_UPLOAD_FOLDER, filename))
        data.append({"title": request.form['title'], "image": filename, "url": request.form['url']}); save_json_data(OFFERS_FILE, data); flash('Offer added!', 'success'); return redirect(url_for('manage_offers'))
    return render_template('add_edit_offer.html', active_page='offers', title="Add New Offer")
@app.route('/offers/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_offer(item_id):
    data = get_json_data(OFFERS_FILE)
    if not 0 <= item_id < len(data): return redirect(url_for('manage_offers'))
    offer = data[item_id]
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename != '':
            delete_image_file(offer.get('image'), 'offers'); image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(OFFERS_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(OFFERS_UPLOAD_FOLDER, filename)); offer['image'] = filename
        offer['title'] = request.form['title']; offer['url'] = request.form['url']
        save_json_data(OFFERS_FILE, data); flash('Offer updated!', 'success'); return redirect(url_for('manage_offers'))
    return render_template('add_edit_offer.html', offer=offer, offer_id=item_id, active_page='offers', title="Edit Offer")
@app.route('/offers/delete/<int:item_id>', methods=['POST'])
def delete_offer(item_id):
    data = get_json_data(OFFERS_FILE)
    if 0 <= item_id < len(data): delete_image_file(data[item_id].get('image'), 'offers'); data.pop(item_id); save_json_data(OFFERS_FILE, data); flash('Offer deleted.', 'success')
    return redirect(url_for('manage_offers'))

@app.route('/projects')
def manage_projects(): return render_template('manage_projects.html', projects=get_json_data(PROJECTS_FILE), active_page='projects', title="Manage Projects")
@app.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        data = get_json_data(PROJECTS_FILE); filename = ""
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(PROJECTS_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(PROJECTS_UPLOAD_FOLDER, filename))
        data.append({"title": request.form['title'], "image": filename, "url": request.form['url']}); save_json_data(PROJECTS_FILE, data); flash('Project added!', 'success'); return redirect(url_for('manage_projects'))
    return render_template('add_edit_project.html', active_page='projects', title="Add New Project")
@app.route('/projects/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_project(item_id):
    data = get_json_data(PROJECTS_FILE)
    if not 0 <= item_id < len(data): return redirect(url_for('manage_projects'))
    project = data[item_id]
    if request.method == 'POST':
        if 'image' in request.files and request.files['image'].filename != '':
            delete_image_file(project.get('image'), 'projects'); image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(PROJECTS_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(PROJECTS_UPLOAD_FOLDER, filename)); project['image'] = filename
        project['title'] = request.form['title']; project['url'] = request.form['url']
        save_json_data(PROJECTS_FILE, data); flash('Project updated!', 'success'); return redirect(url_for('manage_projects'))
    return render_template('add_edit_project.html', project=project, project_id=item_id, active_page='projects', title="Edit Project")
@app.route('/projects/delete/<int:item_id>', methods=['POST'])
def delete_project(item_id):
    data = get_json_data(PROJECTS_FILE)
    if 0 <= item_id < len(data): delete_image_file(data[item_id].get('image'), 'projects'); data.pop(item_id); save_json_data(PROJECTS_FILE, data); flash('Project deleted.', 'success')
    return redirect(url_for('manage_projects'))

@app.route('/videos')
def manage_videos(): return render_template('manage_videos.html', videos=get_json_data(VIDEOS_FILE), active_page='videos', title="Manage Videos")
@app.route('/videos/add', methods=['GET', 'POST'])
def add_video():
    if request.method == 'POST':
        data = get_json_data(VIDEOS_FILE); data.append({"title": request.form['title'], "youtube_id": request.form['youtube_id']}); save_json_data(VIDEOS_FILE, data); flash('Video added!', 'success'); return redirect(url_for('manage_videos'))
    return render_template('add_edit_video.html', active_page='videos', title="Add New Video")
@app.route('/videos/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_video(item_id):
    data = get_json_data(VIDEOS_FILE)
    if not 0 <= item_id < len(data): return redirect(url_for('manage_videos'))
    video = data[item_id]
    if request.method == 'POST': video['title'] = request.form['title']; video['youtube_id'] = request.form['youtube_id']; save_json_data(VIDEOS_FILE, data); flash('Video updated!', 'success'); return redirect(url_for('manage_videos'))
    return render_template('add_edit_video.html', video=video, video_id=item_id, active_page='videos', title="Edit Video")
@app.route('/videos/delete/<int:item_id>', methods=['POST'])
def delete_video(item_id):
    data = get_json_data(VIDEOS_FILE)
    if 0 <= item_id < len(data): data.pop(item_id); save_json_data(VIDEOS_FILE, data); flash('Video deleted.', 'success')
    return redirect(url_for('manage_videos'))

@app.route('/about_page', methods=['GET', 'POST'])
def edit_about_page():
    data = get_json_data(ABOUT_FILE)
    if request.method == 'POST':
        if 'banner_image' in request.files and request.files['banner_image'].filename != '':
            delete_image_file(data.get('banner_image')); image_file = request.files['banner_image']; data['banner_image'] = secure_filename(image_file.filename); image_file.save(os.path.join(UPLOAD_FOLDER, data['banner_image']))
        if 'about_us_image' in request.files and request.files['about_us_image'].filename != '':
            delete_image_file(data.get('about_us_image')); image_file = request.files['about_us_image']; data['about_us_image'] = secure_filename(image_file.filename); image_file.save(os.path.join(UPLOAD_FOLDER, data['about_us_image']))
        data['about_us_heading'] = request.form['about_us_heading']; data['about_us_text'] = request.form['about_us_text']; data['who_we_are_heading'] = request.form['who_we_are_heading']; data['who_we_are_text'] = request.form['who_we_are_text']
        save_json_data(ABOUT_FILE, data); flash('About page updated!', 'success'); return redirect(url_for('edit_about_page'))
    return render_template('edit_about_page.html', data=data, active_page='about_page', title="Edit About Page")

@app.route('/services_page', methods=['GET', 'POST'])
def edit_services_page():
    data = get_json_data(SERVICES_FILE)
    if request.method == 'POST':
        data['heading'] = request.form['heading']; data['services_list'] = [s.strip() for s in request.form['services_list'].split('\n') if s.strip()]
        save_json_data(SERVICES_FILE, data); flash('Services page updated!', 'success'); return redirect(url_for('edit_services_page'))
    services_list_str = "\n".join(data.get('services_list', [])); return render_template('edit_services_page.html', data=data, services_list_str=services_list_str, active_page='services_page', title="Edit Services Page")

@app.route('/contact_page', methods=['GET', 'POST'])
def edit_contact_page():
    data = get_json_data(CONTACT_FILE)
    if request.method == 'POST':
        data['page_heading'] = request.form['page_heading']; data['page_subheading'] = request.form['page_subheading']
        data['email']['label'] = request.form['email_label']; data['email']['address'] = request.form['email_address']
        data['phone']['label'] = request.form['phone_label']; data['phone']['number'] = request.form['phone_number']
        data['address']['label'] = request.form['address_label']; data['address']['line1'] = request.form['address_line1']; data['address']['line2'] = request.form['address_line2']
        data['business_hours']['label'] = request.form['business_hours_label']; data['business_hours']['days'] = request.form['business_hours_days']; data['business_hours']['hours'] = request.form['business_hours_hours']
        save_json_data(CONTACT_FILE, data); flash('Contact page updated!', 'success'); return redirect(url_for('edit_contact_page'))
    return render_template('edit_contact_page.html', data=data, active_page='contact_page', title="Edit Contact Page")

@app.route('/blog_posts')
def manage_blog_posts(): return render_template('manage_blog_posts.html', blog_posts=get_json_data(BLOG_FILE), active_page='blog_posts', title="Manage Blog Posts")
@app.route('/blog_posts/add', methods=['GET', 'POST'])
def add_blog_post():
    if request.method == 'POST':
        data = get_json_data(BLOG_FILE); title = request.form['title']; slug = secure_filename(title.lower().replace(' ', '-')); original_slug = slug; counter = 1
        while any(p['slug'] == slug for p in data): slug = f"{original_slug}-{counter}"; counter += 1
        image_filename = ""; image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename); os.makedirs(BLOG_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(BLOG_UPLOAD_FOLDER, image_filename))
        data.append({"title": title, "date": request.form.get('date', datetime.now().strftime("%B %d, %Y")), "author": request.form['author'], "image": image_filename, "excerpt": request.form['excerpt'], "slug": slug})
        save_json_data(BLOG_FILE, data)
        with open(os.path.join(BLOG_CONTENT_DIR, f"{slug}.md"), 'w', encoding='utf-8') as f: f.write(request.form['content'])
        flash('Blog post added!', 'success'); return redirect(url_for('manage_blog_posts'))
    return render_template('add_edit_blog_post.html', active_page='blog_posts', title="Add New Blog Post", current_date=datetime.now().strftime("%B %d, %Y"))
@app.route('/blog_posts/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_blog_post(item_id):
    data = get_json_data(BLOG_FILE)
    if not 0 <= item_id < len(data): return redirect(url_for('manage_blog_posts'))
    post = data[item_id]; md_path = os.path.join(BLOG_CONTENT_DIR, f"{post['slug']}.md"); current_md = ""
    if os.path.exists(md_path):
        with open(md_path, 'r', encoding='utf-8') as f: current_md = f.read()
    if request.method == 'POST':
        new_title = request.form['title']; new_slug = secure_filename(new_title.lower().replace(' ', '-'))
        if new_slug != post['slug']:
            old_md_path = os.path.join(BLOG_CONTENT_DIR, f"{post['slug']}.md"); original_slug = new_slug; counter = 1
            while any(p['slug'] == new_slug for p in data if p != post): new_slug = f"{original_slug}-{counter}"; counter += 1
            if os.path.exists(old_md_path): os.rename(old_md_path, os.path.join(BLOG_CONTENT_DIR, f"{new_slug}.md"))
            post['slug'] = new_slug
        if 'image' in request.files and request.files['image'].filename != '':
            delete_image_file(post.get('image'), 'blog'); image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(BLOG_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(BLOG_UPLOAD_FOLDER, filename)); post['image'] = filename
        post['title'] = new_title; post['author'] = request.form['author']; post['date'] = request.form['date']; post['excerpt'] = request.form['excerpt']
        save_json_data(BLOG_FILE, data)
        with open(os.path.join(BLOG_CONTENT_DIR, f"{post['slug']}.md"), 'w', encoding='utf-8') as f: f.write(request.form['content'])
        flash('Blog post updated!', 'success'); return redirect(url_for('manage_blog_posts'))
    return render_template('add_edit_blog_post.html', post=post, post_id=item_id, current_markdown_content=current_md, active_page='blog_posts', title="Edit Blog Post")
@app.route('/blog_posts/delete/<int:item_id>', methods=['POST'])
def delete_blog_post(item_id):
    data = get_json_data(BLOG_FILE)
    if 0 <= item_id < len(data):
        post = data[item_id]; delete_image_file(post.get('image'), 'blog')
        md_path = os.path.join(BLOG_CONTENT_DIR, f"{post['slug']}.md")
        if os.path.exists(md_path): os.remove(md_path)
        data.pop(item_id); save_json_data(BLOG_FILE, data); flash('Blog post deleted.', 'success')
    return redirect(url_for('manage_blog_posts'))

@app.route('/portfolio_categories')
def manage_portfolio_categories(): return render_template('manage_portfolio_categories.html', categories=get_json_data(PORTFOLIO_FILE), active_page='portfolio_categories', title="Manage Portfolio")
@app.route('/portfolio_categories/add', methods=['GET', 'POST'])
def add_portfolio_category():
    if request.method == 'POST':
        data = get_json_data(PORTFOLIO_FILE); folder = secure_filename(request.form['folder_name'].lower().replace(' ', '-')); original_folder = folder; counter = 1
        while any(c['folder'] == folder for c in data): folder = f"{original_folder}-{counter}"; counter += 1
        filename = ""
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(PORTFOLIO_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(PORTFOLIO_UPLOAD_FOLDER, filename))
        data.append({"label": request.form['label'], "folder": folder, "image": filename}); save_json_data(PORTFOLIO_FILE, data)
        os.makedirs(os.path.join(PORTFOLIO_UPLOAD_FOLDER, folder), exist_ok=True)
        flash('Portfolio category added!', 'success'); return redirect(url_for('manage_portfolio_categories'))
    return render_template('add_edit_portfolio_category.html', active_page='portfolio_categories', title="Add New Portfolio Category")
@app.route('/portfolio_categories/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_portfolio_category(item_id):
    data = get_json_data(PORTFOLIO_FILE)
    if not 0 <= item_id < len(data): return redirect(url_for('manage_portfolio_categories'))
    category = data[item_id]
    if request.method == 'POST':
        old_folder = category['folder']; new_folder = secure_filename(request.form['folder_name'].lower().replace(' ', '-'))
        if new_folder != old_folder:
            original_folder = new_folder; counter = 1
            while any(c['folder'] == new_folder for c in data if c != category): new_folder = f"{original_folder}-{counter}"; counter += 1
            old_path = os.path.join(PORTFOLIO_UPLOAD_FOLDER, old_folder); new_path = os.path.join(PORTFOLIO_UPLOAD_FOLDER, new_folder)
            if os.path.exists(old_path): os.rename(old_path, new_path)
            else: os.makedirs(new_path, exist_ok=True)
            category['folder'] = new_folder
        if 'image' in request.files and request.files['image'].filename != '':
            delete_image_file(category.get('image'), 'portfolio'); image_file = request.files['image']; filename = secure_filename(image_file.filename); os.makedirs(PORTFOLIO_UPLOAD_FOLDER, exist_ok=True); image_file.save(os.path.join(PORTFOLIO_UPLOAD_FOLDER, filename)); category['image'] = filename
        category['label'] = request.form['label']; save_json_data(PORTFOLIO_FILE, data); flash('Category updated!', 'success'); return redirect(url_for('manage_portfolio_categories'))
    return render_template('add_edit_portfolio_category.html', category=category, category_id=item_id, active_page='portfolio_categories', title="Edit Portfolio Category")
@app.route('/portfolio_categories/delete/<int:item_id>', methods=['POST'])
def delete_portfolio_category(item_id):
    data = get_json_data(PORTFOLIO_FILE)
    if 0 <= item_id < len(data):
        category = data[item_id]; delete_image_file(category.get('image'), 'portfolio')
        folder_path = os.path.join(PORTFOLIO_UPLOAD_FOLDER, category['folder'])
        if os.path.exists(folder_path):
            try: shutil.rmtree(folder_path)
            except OSError as e: flash(f"Error deleting folder: {e}", 'error')
        data.pop(item_id); save_json_data(PORTFOLIO_FILE, data); flash('Category deleted.', 'success')
    return redirect(url_for('manage_portfolio_categories'))

# --- Deploy ---
@app.route('/deploy', methods=['GET', 'POST'])
def deploy():
    output = ""
    if request.method == 'POST':
        commit_message = request.form.get('commit_message', 'Updated website content via CMS')
        try:
            output += ">>> Running build.py...\n"
            build_process = subprocess.run(['python', os.path.join(WEBSITE_ROOT_PATH, 'build.py')], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += build_process.stdout + "\n" + build_process.stderr + "\n"
            output += ">>> Running git add . ...\n"
            add_process = subprocess.run(['git', 'add', '.'], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += add_process.stdout + "\n"
            output += f">>> Running git commit -m \"{commit_message}\"...\n"
            commit_process = subprocess.run(['git', 'commit', '-m', commit_message], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, encoding='utf-8')
            output += commit_process.stdout + "\n"
            if "nothing to commit" in commit_process.stdout.lower() or commit_process.returncode != 0:
                output += "No changes to commit or commit failed. Skipping push.\n"; flash('Deployment finished. Check log.', 'warning')
                return render_template('deploy.html', output=output, active_page='deploy')
            output += ">>> Running git push...\n"
            push_process = subprocess.run(['git', 'push'], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += push_process.stdout + "\n" + push_process.stderr + "\n"
            output += "\n✅ DEPLOYMENT SUCCESSFUL! ✅\n"; flash('Website deployed successfully!', 'success')
        except subprocess.CalledProcessError as e:
            output += f"\n\n❌ DEPLOYMENT FAILED! ❌\nCommand '{' '.join(e.cmd)}' failed.\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}"; flash('Deployment failed.', 'error')
        except Exception as e:
            output += f"\n\n❌ UNEXPECTED ERROR! ❌\n{e}"; flash('An unexpected error occurred.', 'error')
    return render_template('deploy.html', output=output, active_page='deploy', title="Deploy Website")

# --- Run App ---
if __name__ == '__main__':
    print("===================================================")
    print("Starting IdentityWind CMS: http://127.0.0.1:5000")
    print("===================================================")
    app.run(port=5000, debug=True)