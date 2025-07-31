import os
import json
import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

# --- Configuration ---
WEBSITE_ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(WEBSITE_ROOT_PATH, 'src', 'data')
CONTENT_DIR = os.path.join(WEBSITE_ROOT_PATH, 'src', 'content')
UPLOAD_FOLDER = os.path.join(CONTENT_DIR, 'images') # Base images folder for website content

# Define specific data file paths
FOOTER_FILE = os.path.join(DATA_PATH, 'footer.json')
TESTIMONIALS_FILE = os.path.join(DATA_PATH, 'testimonials.json')
TEAM_FILE = os.path.join(DATA_PATH, 'team.json')
BANNERS_FILE = os.path.join(DATA_PATH, 'banners.json')
OFFERS_FILE = os.path.join(DATA_PATH, 'offers.json')
PROJECTS_FILE = os.path.join(DATA_PATH, 'projects.json') # NEW
VIDEOS_FILE = os.path.join(DATA_PATH, 'videos.json')     # NEW
ABOUT_FILE = os.path.join(DATA_PATH, 'about.json')       # NEW
SERVICES_FILE = os.path.join(DATA_PATH, 'services.json') # NEW
CONTACT_FILE = os.path.join(DATA_PATH, 'contact.json')   # NEW
PORTFOLIO_FILE = os.path.join(DATA_PATH, 'portfolio.json') # NEW
BLOG_FILE = os.path.join(DATA_PATH, 'blog.json')         # NEW

# Define specific image upload subfolders
TEAM_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'team')
BANNERS_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'banners')
OFFERS_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'offers')
PROJECTS_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'projects') # NEW
ABOUT_UPLOAD_FOLDER = UPLOAD_FOLDER # About images like company-photo.jpg might be in base UPLOAD_FOLDER or dedicated sub-folder. Assuming root 'images' for 'company-photo.jpg' and 'about-banner.jpg'
BLOG_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'blog') # NEW
PORTFOLIO_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'portfolio') # NEW

# Define blog content directory (for markdown files)
BLOG_CONTENT_DIR = os.path.join(CONTENT_DIR, 'blog') # NEW


# --- Flask App Initialization ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Base UPLOAD_FOLDER for serving images later
app.secret_key = 'your_secret_key_here' # Needed for flash messages. CHANGE THIS IN PRODUCTION!


# --- Helper Functions ---
def get_json_data(filepath):
    if not os.path.exists(filepath):
        # Determine if the file should contain a list or an object by default
        list_files = [
            BANNERS_FILE, TESTIMONIALS_FILE, TEAM_FILE, OFFERS_FILE,
            PROJECTS_FILE, VIDEOS_FILE, BLOG_FILE, PORTFOLIO_FILE
        ]
        return [] if filepath in list_files else {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_data(filepath, data):
    # Ensure directory exists before saving
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def delete_image_file(image_filename, subfolder=""):
    """Deletes an image file from a specific subfolder within UPLOAD_FOLDER."""
    if not image_filename:
        return
    try:
        # If subfolder is empty, it implies image is directly in UPLOAD_FOLDER (e.g., about-banner.jpg)
        file_path = os.path.join(UPLOAD_FOLDER, subfolder, image_filename) if subfolder else os.path.join(UPLOAD_FOLDER, image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted image file: {file_path}")
        else:
            print(f"Image file not found for deletion: {file_path}")
    except OSError as e:
        print(f"Error deleting image file '{image_filename}': {e}")

# --- App Routes ---

# Serves images from the content/images directory (and its subdirectories)
@app.route('/content/images/<path:filename>')
def serve_content_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Root route - Edit Footer (Already exists)
@app.route('/', methods=['GET', 'POST'])
def edit_footer():
    data = get_json_data(FOOTER_FILE)
    if request.method == 'POST':
        data['email'] = request.form['email']
        data['copyright_text'] = request.form['copyright_text']
        # Handle social links
        social_links = []
        for i in range(len(request.form.getlist('social_name'))):
            name = request.form.getlist('social_name')[i]
            url = request.form.getlist('social_url')[i]
            if name and url: # Only add if both fields are provided
                social_links.append({"name": name, "url": url})
        data['social_links'] = social_links
        
        save_json_data(FOOTER_FILE, data)
        flash('Footer updated successfully!', 'success')
        return redirect(url_for('edit_footer'))
    return render_template('edit_footer.html', data=data, active_page='footer')

# Testimonials Routes (Already exists)
@app.route('/testimonials')
def manage_testimonials():
    return render_template('manage_testimonials.html', testimonials=get_json_data(TESTIMONIALS_FILE), active_page='testimonials')
@app.route('/testimonials/add', methods=['POST'])
def add_testimonial():
    data = get_json_data(TESTIMONIALS_FILE)
    data.append({"client_name": request.form['client_name'], "feedback": request.form['feedback']})
    save_json_data(TESTIMONIALS_FILE, data)
    flash('Testimonial added successfully!', 'success')
    return redirect(url_for('manage_testimonials'))
@app.route('/testimonials/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_testimonial(item_id):
    data = get_json_data(TESTIMONIALS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Testimonial not found.', 'error')
        return redirect(url_for('manage_testimonials'))
    testimonial_to_edit = data[item_id]
    if request.method == 'POST':
        testimonial_to_edit['client_name'] = request.form['client_name']
        testimonial_to_edit['feedback'] = request.form['feedback']
        save_json_data(TESTIMONIALS_FILE, data)
        flash('Testimonial updated successfully!', 'success')
        return redirect(url_for('manage_testimonials'))
    return render_template('edit_testimonial.html', testimonial=testimonial_to_edit, active_page='testimonials')
@app.route('/testimonials/delete/<int:item_id>', methods=['POST'])
def delete_testimonial(item_id):
    data = get_json_data(TESTIMONIALS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Testimonial not found.', 'error')
        return redirect(url_for('manage_testimonials'))
    data.pop(item_id)
    save_json_data(TESTIMONIALS_FILE, data)
    flash('Testimonial deleted successfully!', 'success')
    return redirect(url_for('manage_testimonials'))

# Team Routes (Already exists)
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
        os.makedirs(TEAM_UPLOAD_FOLDER, exist_ok=True)
        image_file.save(os.path.join(TEAM_UPLOAD_FOLDER, filename))
    new_member = {
        "name": request.form['name'],
        "title": request.form['title'],
        "bio": request.form.get('bio', ''),
        "image": filename,
        "is_ceo": 'is_ceo' in request.form
    }
    data.append(new_member)
    save_json_data(TEAM_FILE, data)
    flash('Team member added successfully!', 'success')
    return redirect(url_for('manage_team'))
@app.route('/team/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_team_member(item_id):
    data = get_json_data(TEAM_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Team member not found.', 'error')
        return redirect(url_for('manage_team'))
    member_to_edit = data[item_id]
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if member_to_edit.get('image'):
                delete_image_file(member_to_edit['image'], subfolder='team')
            filename = secure_filename(image_file.filename)
            os.makedirs(TEAM_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(TEAM_UPLOAD_FOLDER, filename))
            member_to_edit['image'] = filename
        member_to_edit['name'] = request.form['name']
        member_to_edit['title'] = request.form['title']
        member_to_edit['bio'] = request.form.get('bio', '')
        member_to_edit['is_ceo'] = 'is_ceo' in request.form
        save_json_data(TEAM_FILE, data)
        flash('Team member updated successfully!', 'success')
        return redirect(url_for('manage_team'))
    return render_template('edit_team_member.html', member=member_to_edit, active_page='team')
@app.route('/team/delete/<int:item_id>', methods=['POST'])
def delete_team_member(item_id):
    data = get_json_data(TEAM_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Team member not found.', 'error')
        return redirect(url_for('manage_team'))
    image_to_delete = data[item_id].get('image')
    if image_to_delete:
        delete_image_file(image_to_delete, subfolder='team')
    data.pop(item_id)
    save_json_data(TEAM_FILE, data)
    flash('Team member deleted successfully!', 'success')
    return redirect(url_for('manage_team'))

# Banner Management Routes (Already exists)
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
            os.makedirs(BANNERS_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(BANNERS_UPLOAD_FOLDER, filename))
        new_banner = {"image": filename}
        data.append(new_banner)
        save_json_data(BANNERS_FILE, data)
        flash('Banner added successfully!', 'success')
        return redirect(url_for('manage_banners'))
    return render_template('add_edit_banner.html', active_page='banners', title="Add New Banner")
@app.route('/banners/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_banner(item_id):
    data = get_json_data(BANNERS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Banner not found.', 'error')
        return redirect(url_for('manage_banners'))
    banner_to_edit = data[item_id]
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if banner_to_edit.get('image'):
                delete_image_file(banner_to_edit['image'], subfolder='banners')
            filename = secure_filename(image_file.filename)
            os.makedirs(BANNERS_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(BANNERS_UPLOAD_FOLDER, filename))
            banner_to_edit['image'] = filename
        save_json_data(BANNERS_FILE, data)
        flash('Banner updated successfully!', 'success')
        return redirect(url_for('manage_banners'))
    return render_template('add_edit_banner.html', active_page='banners', banner=banner_to_edit, banner_id=item_id, title="Edit Banner")
@app.route('/banners/delete/<int:item_id>', methods=['POST'])
def delete_banner(item_id):
    data = get_json_data(BANNERS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Banner not found.', 'error')
        return redirect(url_for('manage_banners'))
    image_to_delete = data[item_id].get('image')
    if image_to_delete:
        delete_image_file(image_to_delete, subfolder='banners')
    data.pop(item_id)
    save_json_data(BANNERS_FILE, data)
    flash('Banner deleted successfully!', 'success')
    return redirect(url_for('manage_banners'))

# Offer Management Routes (Already exists)
@app.route('/offers')
def manage_offers():
    offers_data = get_json_data(OFFERS_FILE)
    return render_template('manage_offers.html', offers=offers_data, active_page='offers')
@app.route('/offers/add', methods=['GET', 'POST'])
def add_offer():
    if request.method == 'POST':
        data = get_json_data(OFFERS_FILE)
        image_file = request.files.get('image')
        filename = ""
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            os.makedirs(OFFERS_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(OFFERS_UPLOAD_FOLDER, filename))
        new_offer = {
            "title": request.form['title'],
            "image": filename,
            "url": request.form['url']
        }
        data.append(new_offer)
        save_json_data(OFFERS_FILE, data)
        flash('Offer added successfully!', 'success')
        return redirect(url_for('manage_offers'))
    return render_template('add_edit_offer.html', active_page='offers', title="Add New Offer")
@app.route('/offers/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_offer(item_id):
    data = get_json_data(OFFERS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Offer not found.', 'error')
        return redirect(url_for('manage_offers'))
    offer_to_edit = data[item_id]
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if offer_to_edit.get('image'):
                delete_image_file(offer_to_edit['image'], subfolder='offers')
            filename = secure_filename(image_file.filename)
            os.makedirs(OFFERS_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(OFFERS_UPLOAD_FOLDER, filename))
            offer_to_edit['image'] = filename
        offer_to_edit['title'] = request.form['title']
        offer_to_edit['url'] = request.form['url']
        save_json_data(OFFERS_FILE, data)
        flash('Offer updated successfully!', 'success')
        return redirect(url_for('manage_offers'))
    return render_template('add_edit_offer.html', active_page='offers', offer=offer_to_edit, offer_id=item_id, title="Edit Offer")
@app.route('/offers/delete/<int:item_id>', methods=['POST'])
def delete_offer(item_id):
    data = get_json_data(OFFERS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Offer not found.', 'error')
        return redirect(url_for('manage_offers'))
    image_to_delete = data[item_id].get('image')
    if image_to_delete:
        delete_image_file(image_to_delete, subfolder='offers')
    data.pop(item_id)
    save_json_data(OFFERS_FILE, data)
    flash('Offer deleted successfully!', 'success')
    return redirect(url_for('manage_offers'))


# --- NEW: Projects Management Routes ---
@app.route('/projects')
def manage_projects():
    projects_data = get_json_data(PROJECTS_FILE)
    return render_template('manage_projects.html', projects=projects_data, active_page='projects')

@app.route('/projects/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        data = get_json_data(PROJECTS_FILE)
        image_file = request.files.get('image')
        filename = ""
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            os.makedirs(PROJECTS_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(PROJECTS_UPLOAD_FOLDER, filename))
        new_project = {
            "title": request.form['title'],
            "image": filename,
            "url": request.form['url']
        }
        data.append(new_project)
        save_json_data(PROJECTS_FILE, data)
        flash('Project added successfully!', 'success')
        return redirect(url_for('manage_projects'))
    return render_template('add_edit_project.html', active_page='projects', title="Add New Project")

@app.route('/projects/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_project(item_id):
    data = get_json_data(PROJECTS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Project not found.', 'error')
        return redirect(url_for('manage_projects'))
    project_to_edit = data[item_id]
    if request.method == 'POST':
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if project_to_edit.get('image'):
                delete_image_file(project_to_edit['image'], subfolder='projects')
            filename = secure_filename(image_file.filename)
            os.makedirs(PROJECTS_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(PROJECTS_UPLOAD_FOLDER, filename))
            project_to_edit['image'] = filename
        project_to_edit['title'] = request.form['title']
        project_to_edit['url'] = request.form['url']
        save_json_data(PROJECTS_FILE, data)
        flash('Project updated successfully!', 'success')
        return redirect(url_for('manage_projects'))
    return render_template('add_edit_project.html', active_page='projects', project=project_to_edit, project_id=item_id, title="Edit Project")

@app.route('/projects/delete/<int:item_id>', methods=['POST'])
def delete_project(item_id):
    data = get_json_data(PROJECTS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Project not found.', 'error')
        return redirect(url_for('manage_projects'))
    image_to_delete = data[item_id].get('image')
    if image_to_delete:
        delete_image_file(image_to_delete, subfolder='projects')
    data.pop(item_id)
    save_json_data(PROJECTS_FILE, data)
    flash('Project deleted successfully!', 'success')
    return redirect(url_for('manage_projects'))


# --- NEW: Videos Management Routes ---
@app.route('/videos')
def manage_videos():
    videos_data = get_json_data(VIDEOS_FILE)
    return render_template('manage_videos.html', videos=videos_data, active_page='videos')

@app.route('/videos/add', methods=['GET', 'POST'])
def add_video():
    if request.method == 'POST':
        data = get_json_data(VIDEOS_FILE)
        new_video = {
            "title": request.form['title'],
            "youtube_id": request.form['youtube_id']
        }
        data.append(new_video)
        save_json_data(VIDEOS_FILE, data)
        flash('Video added successfully!', 'success')
        return redirect(url_for('manage_videos'))
    return render_template('add_edit_video.html', active_page='videos', title="Add New Video")

@app.route('/videos/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_video(item_id):
    data = get_json_data(VIDEOS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Video not found.', 'error')
        return redirect(url_for('manage_videos'))
    video_to_edit = data[item_id]
    if request.method == 'POST':
        video_to_edit['title'] = request.form['title']
        video_to_edit['youtube_id'] = request.form['youtube_id']
        save_json_data(VIDEOS_FILE, data)
        flash('Video updated successfully!', 'success')
        return redirect(url_for('manage_videos'))
    return render_template('add_edit_video.html', active_page='videos', video=video_to_edit, video_id=item_id, title="Edit Video")

@app.route('/videos/delete/<int:item_id>', methods=['POST'])
def delete_video(item_id):
    data = get_json_data(VIDEOS_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Video not found.', 'error')
        return redirect(url_for('manage_videos'))
    data.pop(item_id)
    save_json_data(VIDEOS_FILE, data)
    flash('Video deleted successfully!', 'success')
    return redirect(url_for('manage_videos'))


# --- NEW: About Page Management Routes ---
@app.route('/about_page', methods=['GET', 'POST'])
def edit_about_page():
    data = get_json_data(ABOUT_FILE)
    if request.method == 'POST':
        # Handle banner image
        banner_image_file = request.files.get('banner_image')
        if banner_image_file and banner_image_file.filename != '':
            if data.get('banner_image'):
                delete_image_file(data['banner_image']) # No subfolder for about-banner.jpg
            banner_filename = secure_filename(banner_image_file.filename)
            banner_image_file.save(os.path.join(UPLOAD_FOLDER, banner_filename)) # Save to base images folder
            data['banner_image'] = banner_filename

        # Handle about_us_image
        about_us_image_file = request.files.get('about_us_image')
        if about_us_image_file and about_us_image_file.filename != '':
            if data.get('about_us_image'):
                delete_image_file(data['about_us_image']) # No subfolder for company-photo.jpg
            about_filename = secure_filename(about_us_image_file.filename)
            about_us_image_file.save(os.path.join(UPLOAD_FOLDER, about_filename)) # Save to base images folder
            data['about_us_image'] = about_filename
        
        data['about_us_heading'] = request.form['about_us_heading']
        data['about_us_text'] = request.form['about_us_text']
        data['who_we_are_heading'] = request.form['who_we_are_heading']
        data['who_we_are_text'] = request.form['who_we_are_text']
        
        save_json_data(ABOUT_FILE, data)
        flash('About page content updated successfully!', 'success')
        return redirect(url_for('edit_about_page'))
    return render_template('edit_about_page.html', data=data, active_page='about_page')


# --- NEW: Services Page Management Routes ---
@app.route('/services_page', methods=['GET', 'POST'])
def edit_services_page():
    data = get_json_data(SERVICES_FILE)
    if request.method == 'POST':
        data['heading'] = request.form['heading']
        # Services list from comma-separated string
        services_input = request.form['services_list']
        data['services_list'] = [s.strip() for s in services_input.split('\n') if s.strip()] # Split by new line
        save_json_data(SERVICES_FILE, data)
        flash('Services page content updated successfully!', 'success')
        return redirect(url_for('edit_services_page'))
    # Join services list into a string for textarea display, each on a new line
    services_list_str = "\n".join(data.get('services_list', []))
    return render_template('edit_services_page.html', data=data, services_list_str=services_list_str, active_page='services_page')


# --- NEW: Contact Page Management Routes ---
@app.route('/contact_page', methods=['GET', 'POST'])
def edit_contact_page():
    data = get_json_data(CONTACT_FILE)
    if request.method == 'POST':
        data['page_heading'] = request.form['page_heading']
        data['page_subheading'] = request.form['page_subheading']
        
        data['email']['label'] = request.form['email_label']
        data['email']['address'] = request.form['email_address']
        
        data['phone']['label'] = request.form['phone_label']
        data['phone']['number'] = request.form['phone_number']
        
        data['address']['label'] = request.form['address_label']
        data['address']['line1'] = request.form['address_line1']
        data['address']['line2'] = request.form['address_line2']
        
        data['business_hours']['label'] = request.form['business_hours_label']
        data['business_hours']['days'] = request.form['business_hours_days']
        data['business_hours']['hours'] = request.form['business_hours_hours']
        
        save_json_data(CONTACT_FILE, data)
        flash('Contact page content updated successfully!', 'success')
        return redirect(url_for('edit_contact_page'))
    return render_template('edit_contact_page.html', data=data, active_page='contact_page')


# --- NEW: Blog Posts Management Routes ---
@app.route('/blog_posts')
def manage_blog_posts():
    blog_posts_data = get_json_data(BLOG_FILE)
    return render_template('manage_blog_posts.html', blog_posts=blog_posts_data, active_page='blog_posts')

@app.route('/blog_posts/add', methods=['GET', 'POST'])
def add_blog_post():
    if request.method == 'POST':
        data = get_json_data(BLOG_FILE)
        
        title = request.form['title']
        author = request.form['author']
        excerpt = request.form['excerpt']
        raw_markdown = request.form['content']
        
        # Generate a slug (simple version, could be improved for uniqueness/collisions)
        slug = secure_filename(title.lower().replace(' ', '-'))
        # Ensure slug is unique, append a number if necessary
        original_slug = slug
        counter = 1
        while any(p['slug'] == slug for p in data):
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Handle image upload
        image_file = request.files.get('image')
        image_filename = ""
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            os.makedirs(BLOG_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(BLOG_UPLOAD_FOLDER, image_filename))
        
        new_post = {
            "title": title,
            "date": request.form.get('date', datetime.now().strftime("%B %d, %Y")), # Use current date if not provided
            "author": author,
            "image": image_filename,
            "excerpt": excerpt,
            "slug": slug
        }
        data.append(new_post)
        save_json_data(BLOG_FILE, data)
        
        # Save markdown content to a new .md file
        markdown_filepath = os.path.join(BLOG_CONTENT_DIR, f"{slug}.md")
        os.makedirs(BLOG_CONTENT_DIR, exist_ok=True)
        with open(markdown_filepath, 'w', encoding='utf-8') as f:
            f.write(raw_markdown)
        
        flash('Blog post added successfully!', 'success')
        return redirect(url_for('manage_blog_posts'))
    
    # Import datetime for default date
    from datetime import datetime
    return render_template('add_edit_blog_post.html', active_page='blog_posts', title="Add New Blog Post", current_date=datetime.now().strftime("%B %d, %Y"))

@app.route('/blog_posts/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_blog_post(item_id):
    data = get_json_data(BLOG_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Blog post not found.', 'error')
        return redirect(url_for('manage_blog_posts'))
    post_to_edit = data[item_id]
    
    # Load existing markdown content
    markdown_filepath = os.path.join(BLOG_CONTENT_DIR, f"{post_to_edit['slug']}.md")
    current_markdown_content = ""
    if os.path.exists(markdown_filepath):
        with open(markdown_filepath, 'r', encoding='utf-8') as f:
            current_markdown_content = f.read()

    if request.method == 'POST':
        # Handle title change possibly changing slug
        new_title = request.form['title']
        new_slug = secure_filename(new_title.lower().replace(' ', '-'))
        
        # If title changed, and new slug is different, check for uniqueness and rename .md file
        if new_slug != post_to_edit['slug']:
            old_markdown_filepath = os.path.join(BLOG_CONTENT_DIR, f"{post_to_edit['slug']}.md")
            original_new_slug = new_slug
            counter = 1
            while any(p['slug'] == new_slug for p in data if p != post_to_edit): # Check against other posts
                new_slug = f"{original_new_slug}-{counter}"
                counter += 1
            new_markdown_filepath = os.path.join(BLOG_CONTENT_DIR, f"{new_slug}.md")
            if os.path.exists(old_markdown_filepath):
                os.rename(old_markdown_filepath, new_markdown_filepath)
            post_to_edit['slug'] = new_slug # Update slug in JSON
            
        # Handle image upload
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if post_to_edit.get('image'):
                delete_image_file(post_to_edit['image'], subfolder='blog')
            image_filename = secure_filename(image_file.filename)
            os.makedirs(BLOG_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(BLOG_UPLOAD_FOLDER, image_filename))
            post_to_edit['image'] = image_filename
            
        post_to_edit['title'] = new_title
        post_to_edit['author'] = request.form['author']
        post_to_edit['date'] = request.form['date']
        post_to_edit['excerpt'] = request.form['excerpt']
        
        save_json_data(BLOG_FILE, data)
        
        # Save updated markdown content
        updated_markdown = request.form['content']
        with open(os.path.join(BLOG_CONTENT_DIR, f"{post_to_edit['slug']}.md"), 'w', encoding='utf-8') as f:
            f.write(updated_markdown)
        
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('manage_blog_posts'))

    return render_template('add_edit_blog_post.html', active_page='blog_posts', post=post_to_edit, post_id=item_id, title="Edit Blog Post", current_markdown_content=current_markdown_content)

@app.route('/blog_posts/delete/<int:item_id>', methods=['POST'])
def delete_blog_post(item_id):
    data = get_json_data(BLOG_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Blog post not found.', 'error')
        return redirect(url_for('manage_blog_posts'))
    
    post_to_delete = data[item_id]
    
    # Delete associated image
    image_to_delete = post_to_delete.get('image')
    if image_to_delete:
        delete_image_file(image_to_delete, subfolder='blog')
        
    # Delete associated markdown file
    markdown_filepath = os.path.join(BLOG_CONTENT_DIR, f"{post_to_delete['slug']}.md")
    if os.path.exists(markdown_filepath):
        try:
            os.remove(markdown_filepath)
            print(f"Deleted markdown file: {markdown_filepath}")
        except OSError as e:
            print(f"Error deleting markdown file '{markdown_filepath}': {e}")
            
    data.pop(item_id)
    save_json_data(BLOG_FILE, data)
    flash('Blog post deleted successfully!', 'success')
    return redirect(url_for('manage_blog_posts'))


# --- NEW: Portfolio Categories Management Routes ---
@app.route('/portfolio_categories')
def manage_portfolio_categories():
    portfolio_data = get_json_data(PORTFOLIO_FILE)
    return render_template('manage_portfolio_categories.html', categories=portfolio_data, active_page='portfolio_categories')

@app.route('/portfolio_categories/add', methods=['GET', 'POST'])
def add_portfolio_category():
    if request.method == 'POST':
        data = get_json_data(PORTFOLIO_FILE)
        label = request.form['label']
        folder = secure_filename(request.form['folder_name'].lower().replace(' ', '-')) # Sanitize folder name

        # Ensure folder name is unique
        original_folder = folder
        counter = 1
        while any(c['folder'] == folder for c in data):
            folder = f"{original_folder}-{counter}"
            counter += 1
            
        # Handle image upload for category thumbnail
        image_file = request.files.get('image')
        image_filename = ""
        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            # Save category thumbnail to portfolio base image folder
            os.makedirs(PORTFOLIO_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(PORTFOLIO_UPLOAD_FOLDER, image_filename))
        
        new_category = {
            "label": label,
            "folder": folder,
            "image": image_filename # This is the thumbnail for the category
        }
        data.append(new_category)
        save_json_data(PORTFOLIO_FILE, data)

        # Create the physical folder for the category's images
        category_images_path = os.path.join(PORTFOLIO_UPLOAD_FOLDER, folder)
        os.makedirs(category_images_path, exist_ok=True)
        
        flash('Portfolio category added successfully!', 'success')
        return redirect(url_for('manage_portfolio_categories'))
    return render_template('add_edit_portfolio_category.html', active_page='portfolio_categories', title="Add New Portfolio Category")

@app.route('/portfolio_categories/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_portfolio_category(item_id):
    data = get_json_data(PORTFOLIO_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Portfolio category not found.', 'error')
        return redirect(url_for('manage_portfolio_categories'))
    category_to_edit = data[item_id]
    
    if request.method == 'POST':
        old_folder = category_to_edit['folder']
        new_label = request.form['label']
        new_folder = secure_filename(request.form['folder_name'].lower().replace(' ', '-')) # Sanitize new folder name

        # Handle folder name change (and rename the actual directory)
        if new_folder != old_folder:
            old_path = os.path.join(PORTFOLIO_UPLOAD_FOLDER, old_folder)
            
            # Ensure new_folder is unique
            original_new_folder = new_folder
            counter = 1
            while any(c['folder'] == new_folder for c in data if c != category_to_edit):
                new_folder = f"{original_new_folder}-{counter}"
                counter += 1
            
            new_path = os.path.join(PORTFOLIO_UPLOAD_FOLDER, new_folder)
            
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                print(f"Renamed portfolio folder from '{old_folder}' to '{new_folder}'")
            else:
                # If old path didn't exist, just create the new one
                os.makedirs(new_path, exist_ok=True)
                print(f"Old portfolio folder '{old_folder}' not found, created new folder '{new_folder}'")

            category_to_edit['folder'] = new_folder # Update folder name in JSON
        
        # Handle image upload for category thumbnail
        image_file = request.files.get('image')
        if image_file and image_file.filename != '':
            if category_to_edit.get('image'):
                delete_image_file(category_to_edit['image'], subfolder='portfolio') # Delete old thumbnail
            image_filename = secure_filename(image_file.filename)
            os.makedirs(PORTFOLIO_UPLOAD_FOLDER, exist_ok=True)
            image_file.save(os.path.join(PORTFOLIO_UPLOAD_FOLDER, image_filename))
            category_to_edit['image'] = image_filename

        category_to_edit['label'] = new_label
        save_json_data(PORTFOLIO_FILE, data)
        flash('Portfolio category updated successfully!', 'success')
        return redirect(url_for('manage_portfolio_categories'))
    
    return render_template('add_edit_portfolio_category.html', active_page='portfolio_categories', category=category_to_edit, category_id=item_id, title="Edit Portfolio Category")

@app.route('/portfolio_categories/delete/<int:item_id>', methods=['POST'])
def delete_portfolio_category(item_id):
    data = get_json_data(PORTFOLIO_FILE)
    if item_id >= len(data) or item_id < 0:
        flash('Portfolio category not found.', 'error')
        return redirect(url_for('manage_portfolio_categories'))
    
    category_to_delete = data[item_id]
    
    # Delete associated category thumbnail image
    image_to_delete = category_to_delete.get('image')
    if image_to_delete:
        delete_image_file(image_to_delete, subfolder='portfolio')
        
    # Delete the entire category folder and its contents (be careful!)
    category_folder_path = os.path.join(PORTFOLIO_UPLOAD_FOLDER, category_to_delete['folder'])
    if os.path.exists(category_folder_path):
        try:
            shutil.rmtree(category_folder_path)
            print(f"Deleted portfolio category folder: {category_folder_path}")
            flash(f"Category '{category_to_delete['label']}' and its images deleted.", 'success')
        except OSError as e:
            print(f"Error deleting portfolio category folder '{category_folder_path}': {e}")
            flash(f"Error deleting folder for '{category_to_delete['label']}': {e}", 'error')
    else:
        flash(f"Category folder for '{category_to_delete['label']}' not found, but JSON entry deleted.", 'warning')

    data.pop(item_id)
    save_json_data(PORTFOLIO_FILE, data)
    flash('Portfolio category deleted successfully!', 'success')
    return redirect(url_for('manage_portfolio_categories'))


# --- DEPLOY ROUTE ---
@app.route('/deploy', methods=['GET', 'POST'])
def deploy():
    output = ""
    if request.method == 'POST':
        commit_message = request.form.get('commit_message', 'Updated website content via CMS')
        try:
            output += ">>> Running build.py...\n"
            build_process = subprocess.run(['python', os.path.join(WEBSITE_ROOT_PATH, 'build.py')], 
                                            cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += build_process.stdout + "\n"
            output += build_process.stderr + "\n"
            
            output += ">>> Running git add . ...\n"
            add_process = subprocess.run(['git', 'add', '.'], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += add_process.stdout + "\n"

            output += f">>> Running git commit -m \"{commit_message}\"...\n"
            commit_process = subprocess.run(['git', 'commit', '-m', commit_message], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += commit_process.stdout + "\n"
            if "nothing to commit" in commit_process.stdout.lower():
                output += "No changes detected. Skipping git push.\n"
                flash('Deployment successful (no changes to push)!', 'success')
                return render_template('deploy.html', output=output, active_page='deploy')

            output += ">>> Running git push...\n"
            push_process = subprocess.run(['git', 'push'], cwd=WEBSITE_ROOT_PATH, capture_output=True, text=True, check=True, encoding='utf-8')
            output += push_process.stdout + "\n"
            output += push_process.stderr + "\n"
            
            output += "\n✅ DEPLOYMENT SUCCESSFUL! ✅\nYour website is now live."
            flash('Website deployed successfully!', 'success')
            
        except subprocess.CalledProcessError as e:
            output += f"\n\n❌ DEPLOYMENT FAILED! ❌\n"
            output += f"Command '{' '.join(e.cmd)}' returned non-zero exit status {e.returncode}.\n"
            output += "\n--- STDOUT ---\n" + e.stdout
            output += "\n--- STDERR ---\n" + e.stderr
            flash('Deployment failed. Check log for details.', 'error')
        except Exception as e:
            output += f"\n\n❌ DEPLOYMENT FAILED! ❌\n"
            output += f"An unexpected error occurred: {e}\n"
            flash('Deployment failed. Check log for details.', 'error')
            
    return render_template('deploy.html', output=output, active_page='deploy')


# --- Run the App ---
if __name__ == '__main__':
    print("===================================================")
    print("Starting your local Content Management Server...")
    print("Open your web browser and go to: http://127.0.0.1:5000")
    print("===================================================")
    app.run(port=5000, debug=True)