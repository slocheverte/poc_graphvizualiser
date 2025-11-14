import os


def main():
    try:
        from livereload import Server
    except ImportError:
        print("Error: 'livereload' is not installed.\n")
        print("Install it with:\n  pip install -r frontend/requirements.txt\n")
        return

    root = os.path.dirname(__file__)
    server = Server()

    # Watch common frontend files for live reload
    server.watch(os.path.join(root, 'index.html'))
    server.watch(os.path.join(root, 'script.js'))
    server.watch(os.path.join(root, 'style.css'))

    # Serve the frontend directory on port 3000
    server.serve(root=root, port=3000, host='0.0.0.0', open_url_delay=1)


if __name__ == '__main__':
    main()
