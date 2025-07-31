import os
import shutil
import json
import markdown2
from jinja2 import Environment, FileSystemLoader
from PIL import Image
import csscompressor
import jsmin

# --- Configuration ---
SRC_DIR = 'src'
OUTPUT_DIR = 'docs'
TEMPLATES_DIR = os.path.join(SRC_DIR, 'templates')
DATA_DIR = os.path.join(SRC_DIR, 'data')
CONTENT_DIR = os.path.join(SRC_DIR, 'content')
ASSETS_DIR = os.path.join(SRC_DIR, 'assets')
CONTENT_IMAGES_DIR = os.path.join(CONTENT_DIR, 'images')
PORTFOLIO_IMAGES_DIR = os.path.join(CONTENT_IMAGES_DIR, 'portfolio')


# --- Optimization Functions ---
def optimize_images_to_webp(source_root, output_root):
    print("-> Optimizing and converting images to WebP...")
    for dirpath, _, filenames in os.walk(source_root):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                source_path = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(source_path, source_root)
                output_path = os.path.join(output_root, os.path.splitext(relative_path)[0] + '.webp')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                try:
                    with Image.open(source_path) as img:
                        img.save(output_path, 'webp', quality=80)
                except Exception as e:
                    print(f"  - Could not convert {filename}: {e}")

def minify_and_copy_assets(source_dir, output_dir):
    print("-> Minifying and copying assets...")
    os.makedirs(output_dir, exist_ok=True)
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        output_item = os.path.join(output_dir, item)
        if os.path.isdir(source_item):
            minify_and_copy_assets(source_item, output_item)
        elif item.endswith('.css'):
            with open(source_item, 'r', encoding='utf-8') as f_in, open(output_item, 'w', encoding='utf-8') as f_out:
                f_out.write(csscompressor.compress(f_in.read()))
        elif item.endswith('.js'):
            with open(source_item, 'r', encoding='utf-8') as f_in, open(output_item, 'w', encoding='utf-8') as f_out:
                f_out.write(jsmin.jsmin(f_in.read()))
        else:
            shutil.copy2(source_item, output_item)

# --- Main Build Logic ---
def load_site_data():
    print("-> Loading all .json data from:", DATA_DIR)
    data = {}
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            key = os.path.splitext(filename)[0]
            filepath = os.path.join(DATA_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data[key] = json.load(f)
                    print(f"  - Loaded '{filename}' successfully.")
            except json.JSONDecodeError:
                print(f"  - ERROR: Could not decode JSON from '{filename}'. File might be empty or malformed.")
            except Exception as e:
                print(f"  - ERROR: Could not read '{filename}': {e}")
    return data

def build():
    print("\n>>> Starting SUPERCHARGED website build...")
    
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    minify_and_copy_assets(ASSETS_DIR, os.path.join(OUTPUT_DIR, 'assets'))
    optimize_images_to_webp(CONTENT_IMAGES_DIR, os.path.join(OUTPUT_DIR, 'content', 'images'))
    
    if os.path.exists(os.path.join(SRC_DIR, 'CNAME')):
        shutil.copy(os.path.join(SRC_DIR, 'CNAME'), OUTPUT_DIR)
    if os.path.exists(os.path.join(CONTENT_DIR, 'blog')):
        shutil.copytree(os.path.join(CONTENT_DIR, 'blog'), os.path.join(OUTPUT_DIR, 'content', 'blog'))

    site_data = load_site_data()
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)

    print("-> Rendering main pages...")
    for filename in [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.html')]:
        template = env.get_template(filename)
        context = site_data.copy()
        context['active_page'] = os.path.splitext(filename)[0]
        with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(template.render(context))

    print("-> Rendering portfolio pages...")
    if 'portfolio' in site_data:
        category_template = env.get_template('partials/portfolio_category.html')
        for category in site_data.get('portfolio', []):
            image_path = os.path.join(PORTFOLIO_IMAGES_DIR, category['folder'])
            images = [img for img in os.listdir(image_path) if img.lower().endswith(('.png', '.jpg', '.jpeg'))] if os.path.exists(image_path) else []
            context = site_data.copy()
            context.update({'active_page': 'portfolio', 'category_name': category['label'], 'images': images, 'category_folder': category['folder']})
            output_filename = f"portfolio-{category['folder']}.html"
            with open(os.path.join(OUTPUT_DIR, output_filename), 'w', encoding='utf-8') as f:
                f.write(category_template.render(context))
    
    print("-> Rendering blog posts...")
    if 'blog' in site_data:
        blog_output_dir = os.path.join(OUTPUT_DIR, 'blog')
        os.makedirs(blog_output_dir, exist_ok=True)
        post_template = env.get_template('partials/post_detail.html')
        for post in site_data.get('blog', []):
            md_path = os.path.join(CONTENT_DIR, 'blog', f"{post['slug']}.md")
            if os.path.exists(md_path):
                with open(md_path, 'r', encoding='utf-8') as f:
                    html_content = markdown2.markdown(f.read())
                context = site_data.copy()
                context.update({'active_page': 'blog', 'post': post, 'content': html_content})
                output_filename = f"{post['slug']}.html"
                with open(os.path.join(blog_output_dir, output_filename), 'w', encoding='utf-8') as f:
                    f.write(post_template.render(context))
            else:
                print(f"  - WARNING: Markdown file not found for slug '{post['slug']}'")

    # --- THIS IS THE CORRECTED LINE ---
    print("\nBuild finished. Your website is now faster!")

if __name__ == "__main__":
    build()