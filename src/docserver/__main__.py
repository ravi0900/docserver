import os
import git
import mistune
from flask import Flask, render_template, abort
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import argparse

# --- Configuration ---
DOCS_DIR = "docs"
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
EXCLUDED_DIRS = ["venv", ".git", "__pycache__", "docs", "templates"]
SUPPORTED_EXTENSIONS = [".py", ".js", ".html", ".css", ".md"] # Add more as needed

# --- Flask App ---
app = Flask(__name__, template_folder=TEMPLATES_DIR)

# --- Core Logic ---
def get_git_repo(path):
    """Initializes and returns the Git repository object."""
    try:
        return git.Repo(path, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        return None

def is_ignored(filepath, repo):
    """Checks if a file is ignored by .gitignore."""
    if not repo:
        return False
    try:
        return repo.is_ignored(filepath)
    except Exception:
        return False

def extract_comments(filepath):
    """Extracts comments from a file and returns them as a string."""
    comments = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"): # Python comments
                    comments.append(line.lstrip("# ").strip())
                elif line.startswith("//"): # JavaScript, CSS comments
                    comments.append(line.lstrip("// ").strip())
                elif line.startswith("/*") and line.endswith("*/"): # CSS, JS block comments
                    comments.append(line.strip("/*").strip("*/").strip())
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return "\\n".join(comments)

def generate_doc(filepath, project_path):
    """Generates a markdown documentation file from a source file."""
    filename = os.path.basename(filepath)
    doc_content = f"# {filename}\\n\\n"
    doc_content += "## Summary\\n\\n"
    doc_content += extract_comments(filepath)
    doc_content += "\\n\\n## Full Code\\n\\n"
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        doc_content += f"```\\n{code}\\n```"
    except Exception as e:
        print(f"Error reading {filepath} for code block: {e}")
        return

    doc_filename = f"{os.path.splitext(filename)[0]}.md"
    doc_filepath = os.path.join(project_path, DOCS_DIR, doc_filename)
    
    with open(doc_filepath, "w", encoding="utf-8") as f:
        f.write(doc_content)
    print(f"Generated documentation for {filename}")

def scan_and_generate(project_path):
    """Scans the project directory and generates documentation for all supported files."""
    repo = get_git_repo(project_path)
    for root, _, files in os.walk(project_path):
        # Exclude specified directories
        if any(d in root for d in EXCLUDED_DIRS):
            continue
            
        for file in files:
            filepath = os.path.join(root, file)
            if not is_ignored(filepath, repo) and os.path.splitext(file)[1] in SUPPORTED_EXTENSIONS:
                generate_doc(filepath, project_path)

# --- File Watching ---
class DocGeneratorEventHandler(FileSystemEventHandler):
    """Handles file system events to trigger documentation generation."""
    def __init__(self, project_path):
        self.project_path = project_path

    def on_modified(self, event):
        if not event.is_directory and os.path.splitext(event.src_path)[1] in SUPPORTED_EXTENSIONS:
            generate_doc(event.src_path, self.project_path)

    def on_created(self, event):
        if not event.is_directory and os.path.splitext(event.src_path)[1] in SUPPORTED_EXTENSIONS:
            generate_doc(event.src_path, self.project_path)

# --- Flask Routes ---
@app.route("/")
def index():
    """Renders the index page with a list of available documentation."""
    docs_dir = app.config.get("DOCS_DIR", DOCS_DIR)
    docs = [f for f in os.listdir(docs_dir) if f.endswith(".md")]
    return render_template("index.html", docs=docs)

@app.route("/docs/<filename>")
def doc_page(filename):
    """Renders a specific documentation page."""
    docs_dir = app.config.get("DOCS_DIR", DOCS_DIR)
    filepath = os.path.join(docs_dir, filename)
    if not os.path.exists(filepath):
        abort(404)
        
    with open(filepath, "r", encoding="utf-8") as f:
        content_md = f.read()
        
    content_html = mistune.html(content_md)
    return render_template("doc_page.html", content=content_html, title=filename)

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="Generate and serve documentation for a code project.")
    parser.add_argument("project_dir", nargs="?", default=".", help="The directory of the project to document.")
    parser.add_argument("-ig", "--ignore-git", action="store_true", help="Run docserver even if the directory is not a Git repository.")
    args = parser.parse_args()

    project_path = os.path.abspath(args.project_dir)

    # Check if it's a git repository
    if not args.ignore_git:
        try:
            git.Repo(project_path, search_parent_directories=True)
        except git.InvalidGitRepositoryError:
            print("Error: This is not a Git repository. Use the -ig or --ignore-git flag to run anyway.")
            return

    docs_path = os.path.join(project_path, DOCS_DIR)
    
    app.config["DOCS_DIR"] = docs_path

    if not os.path.exists(docs_path):
        os.makedirs(docs_path)

    # Initial scan and generation
    scan_and_generate(project_path)

    # Start the file watcher
    event_handler = DocGeneratorEventHandler(project_path)
    observer = Observer()
    observer.schedule(event_handler, project_path, recursive=True)
    observer.start()

    # Start the Flask app
    app.run(debug=True)

if __name__ == "__main__":
    main()