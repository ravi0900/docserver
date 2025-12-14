# docserver

`docserver` is a tool that automatically generates documentation for your projects. It watches for file changes and updates the documentation in real-time. It also includes a web server to view the documentation.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd code2docs
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    ```

3.  **Install the `docserver` package:**
    ```bash
    uv pip install .
    ```

## Usage

To run the `docserver`, use the following command:

```bash
docserver <path_to_your_project>
```

For example, to document the current directory:

```bash
docserver .
```

This will start a web server at `http://127.0.0.1:5000`.

### Help

To see the available options, use the `-h` flag:

```bash
docserver -h
```