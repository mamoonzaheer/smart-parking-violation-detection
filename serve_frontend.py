import http.server
import socketserver
import os

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

# Change to the parksafe_AI_frontend directory
os.chdir('ParkSafe_AI_FrontEnd')

PORT = 3000
Handler = CORSRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving frontend at http://localhost:{PORT}")
    print("Available pages:")
    print("- http://localhost:3000/analytics.html (for parking violation data)")
    print("- http://localhost:3000/dashboard-home.html (for dashboard)")
    print("- http://localhost:3000/cameras.html (for camera feeds)")
    print("- http://localhost:3000/uploads.html (for file uploads)")
    print("\nPress Ctrl+C to stop the server")
    httpd.serve_forever() 