import os
import shutil
import json
import markdown2
from jinja2 import Environment, FileSystemLoader

# --- Configuration ---
SRC_DIR = 'src'
TEMPLATES_DIR = os.path.join(SRC_DIR, 'templates')
DATA_DIR = os.path.join(SRC_DIR, 'data')
CONTENT_DIR = os.path.join(SRC_DIR, 'content')
OUTPUT_DIR = 'docs'

# THE FIX: This is the base path for your GitHub Pages site.
BASE_URL = "/identitywind.github.io"

def setup_project_directories():
    """Creates all necessary source folders if they don't exist."""
    print("Verifying project structure...")
    required_dirs = [
        TEMPLATES_DIR, os.path.join(TEMPLATES_DIR, 'partials'), DATA_DIR,
        os.path.join(SRC_DIR, 'assets', 'img'),
        os.path.join(CONTENT_DIR, 'images', 'portfolio'),
        os.path.join(CONTENT_DIR, 'images', 'blog'), os.path.join(CONTENT_DIR, 'blog')
    ]
    portfolio_data_path = os.path.join(DATA_DIR, 'portfolio.json')
    if os.path.exists(portfolio_data_path):
        with open(portfolio_data_path, 'r', encoding='utf-8') as f:
            p_data = json.load(f)
            for cat in p_data: required_dirs.append(os.path.join(CONTENT_DIR, 'images', 'portfolio', cat['folder']))
    for path in required_dirs:
        if not os.path.exists(path):
            print(f"Directory not found. Creating: {path}")
            os.makedirs(path)

def load_site_data():
    """Loads all JSON files from the data directory."""
    print("Loading content data...")
    data = {}
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            key = filename.split('.')[0]
            path = os.path.join(DATA_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f: data[key] = json.load(f)
    print("Data loaded successfully.")
    return data

def build():
    """The main function to build the entire website."""
    print("\nStarting website build...")
    setup_project_directories()

    # Copy static content
    print("Copying static files...")
    if os.path.exists(os.path.join(OUTPUT_DIR, 'assets')): shutil.rmtree(os.path.join(OUTPUT_DIR, 'assets'))
    shutil.copytree(os.path.join(SRC_DIR, 'assets'), os.path.join(OUTPUT_DIR, 'assets'))
    if os.path.exists(os.path.join(OUTPUT_DIR, 'content')): shutil.rmtree(os.path.join(OUTPUT_DIR, 'content'))
    shutil.copytree(CONTENT_DIR, os.path.join(OUTPUT_DIR, 'content'))
    print("Static files copied successfully.")

    site_data = load_site_data()
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)

    # THE FIX: Add the base_url to the data available to all templates
    site_data['base_url'] = BASE_URL

    # Render Main Pages
    print("Rendering main pages...")
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.html'):
            template = env.get_template(filename)
            page_data = site_data.copy()
            page_data['active_page'] = filename.split('.')[0]
            if filename == "index.html" and os.path.exists(os.path.join(CONTENT_DIR, 'images', 'banners')):
                page_data['banners'] = os.listdir(os.path.join(CONTENT_DIR, 'images', 'banners'))
            output_html = template.render(page_data)
            with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f: f.write(output_html)
            print(f"- Generated Main Page: {filename}")

    # Render Portfolio Pages
    print("Rendering portfolio pages...")
    category_template = env.get_template('partials/portfolio_category.html')
    for category in site_data.get('portfolio', []):
        image_path = os.path.join(CONTENT_DIR, 'images', 'portfolio', category['folder'])
        page_data = site_data.copy()
        page_data.update({'active_page': 'portfolio', 'category_name': category['label'], 'images': os.listdir(image_path), 'category_folder': category['folder']})
        output_html = category_template.render(page_data)
        output_filename = f"portfolio-{category['folder']}.html"
        with open(os.path.join(OUTPUT_DIR, output_filename), 'w', encoding='utf-8') as f: f.write(output_html)
        print(f"- Generated Portfolio Page: {output_filename}")

    # Render Blog Posts
    print("Rendering blog posts...")
    post_template = env.get_template('partials/post_detail.html')
    blog_output_dir = os.path.join(OUTPUT_DIR, 'blog')
    if not os.path.exists(blog_output_dir): os.makedirs(blog_output_dir)
    for post in site_data.get('blog', []):
        md_path = os.path.join(CONTENT_DIR, 'blog', f"{post['slug']}.md")
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f: md_content = f.read()
            html_content = markdown2.markdown(md_content)
            page_data = site_data.copy()
            page_data.update({'active_page': 'blog', 'post': post, 'content': html_content})
            output_html = post_template.render(page_data)
            output_filename = f"{post['slug']}.html"
            with open(os.path.join(blog_output_dir, output_filename), 'w', encoding='utf-8') as f: f.write(output_html)
            print(f"- Generated Blog Post: {output_filename}")
        else:
            print(f"- WARNING: Markdown file not found for slug '{post['slug']}'")

    print("Build finished.")

if __name__ == "__main__":
    build()