import http.server
import socketserver
import os
import urllib.parse
import re

PORT = 9005
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(ROOT_DIR, "Images")
VIDEOS_LINKS_FILE = os.path.join(ROOT_DIR, "Videos", "Links.txt")

PAGE_TITLE = "Universal Display Corporation IT Picnic"
EVENT_DATE = "6/4/2026"
EVENT_TIME = "4:00 PM onwards"

VIDEO_PANEL_COUNT = 3


def read_image_files():
    if not os.path.isdir(IMAGES_DIR):
        return []
    return sorted(
        [f for f in os.listdir(IMAGES_DIR) if os.path.isfile(os.path.join(IMAGES_DIR, f))],
        key=lambda x: x.lower(),
    )


def read_video_links():
    if not os.path.isfile(VIDEOS_LINKS_FILE):
        return []
    with open(VIDEOS_LINKS_FILE, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]
    return links[:VIDEO_PANEL_COUNT]


def get_video_embed_url(url):
    # Support YouTube video URLs and direct video links
    if "youtube.com" in url or "youtu.be" in url:
        # Extract video id
        patterns = [r"v=([\w-]+)", r"youtu\.be/([\w-]+)", r"embed/([\w-]+)"]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"https://www.youtube.com/embed/{match.group(1)}"
    return url


def build_homepage():
    images = read_image_files()
    video_links = read_video_links()
    image_cards = "\n".join(
        f"<div class=\"photo-card\"><img src=\"/Images/{urllib.parse.quote(image)}\" alt=\"{image}\"><div class=\"caption\">{image}</div></div>"
        for image in images
    )
    video_panels = "\n".join(
        f"<div class=\"video-panel\"><iframe src=\"{get_video_embed_url(link)}\" title=\"Video {idx + 1}\" frameborder=\"0\" allowfullscreen></iframe></div>"
        for idx, link in enumerate(video_links)
    )
    if not video_panels:
        video_panels = "<p>No video links found. Add URLs to Videos/Links.txt.</p>"

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{PAGE_TITLE}</title>
    <style>
        body {{ margin: 0; font-family: Arial, sans-serif; background: #f4f7fb; color: #1a1a1a; }}
        header {{ background: #003366; color: #fff; padding: 30px 20px; text-align: center; }}
        header h1 {{ margin: 0 0 12px; font-size: 2.8em; }}
        header p {{ margin: 6px 0; font-size: 1.1em; }}
        .content {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
        .overview {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 18px; margin-bottom: 34px; }}
        .overview .card {{ background: #fff; border-radius: 16px; padding: 24px; box-shadow: 0 12px 24px rgba(0,0,0,.08); }}
        .overview .card h2 {{ margin-top: 0; font-size: 1.25em; }}
        .gallery {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 16px; }}
        .photo-card {{ background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 18px rgba(0,0,0,.08); text-align: center; }}
        .photo-card img {{ display: block; width: 100%; height: auto; object-fit: cover; }}
        .caption {{ padding: 12px; font-size: 0.95em; }}
        .video-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-top: 20px; }}
        .video-panel {{ background: #000; border-radius: 16px; overflow: hidden; position: relative; padding-top: 56.25%; }}
        .video-panel iframe {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; }}
        .footer {{ margin-top: 40px; text-align: center; color: #555; font-size: 0.95em; }}
        a {{ color: #0066cc; text-decoration: none; }}
        @media (max-width: 640px) {{ header h1 {{ font-size: 2.2em; }} }}
    </style>
</head>
<body>
    <header>
        <h1>{PAGE_TITLE}</h1>
        <p><strong>Date:</strong> {EVENT_DATE} &nbsp; | &nbsp; <strong>Time:</strong> {EVENT_TIME}</p>
    </header>
    <main class="content">
        <div class="overview">
            <div class="card">
                <h2>What to expect</h2>
                <p>Enjoy plenty of food, drinks, music, and games at the picnic. This site highlights photos from the IT team and provides video panels to keep the celebration lively.</p>
            </div>
            <div class="card">
                <h2>Food & drinks</h2>
                <p>Come hungry and thirsty — appetizers, snacks, refreshments, and savory favorites will be available throughout the event.</p>
            </div>
            <div class="card">
                <h2>Music & games</h2>
                <p>Bring your team spirit. We’ll have upbeat music, friendly games, and plenty of space to relax with coworkers and friends.</p>
            </div>
        </div>
        <section>
            <h2>Photo Gallery</h2>
            <div class="gallery">
                {image_cards if image_cards else '<p>No images found in the Images folder.</p>'}
            </div>
        </section>
        <section>
            <h2>Video Panels</h2>
            <div class="video-grid">
                {video_panels}
            </div>
        </section>
        <div class="footer">
            <p>Images are served from the <code>Images/</code> folder. Video links are read from <code>Videos/Links.txt</code>.</p>
        </div>
    </main>
</body>
</html>
"""


class PicnicHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/" or parsed_path.path == "":
            content = build_homepage().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            return super().do_GET()


if __name__ == "__main__":
    os.chdir(ROOT_DIR)
    with socketserver.TCPServer(("", PORT), PicnicHandler) as httpd:
        print(f"Serving UDC IT Picnic site at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
            httpd.server_close()
