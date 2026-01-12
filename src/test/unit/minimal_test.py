from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "<h1>Hello World</h1>"

if __name__ == '__main__':
    import sys
    import traceback
    print("Starting minimal Flask server...")
    sys.stdout.flush()
    try:
        print("About to call app.run()...")
        sys.stdout.flush()
        app.run(host='0.0.0.0', port=5001, debug=False)
        print("app.run() returned normally")
        sys.stdout.flush()
    except Exception as e:
        print(f"Exception during app.run(): {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.stdout.flush()
    except SystemExit as e:
        print(f"SystemExit raised with code: {e.code}")
        sys.stdout.flush()
        raise
    finally:
        print("Exiting __main__ block")
        sys.stdout.flush()
