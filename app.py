from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello Teacher! Deployed on AWS Cloud via Jenkins!"

@app.after_request
def add_security_headers(response):
    """Add security headers to prevent common vulnerabilities"""
    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME-sniffing attacks
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS protection in browsers
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy - prevent XSS attacks
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    
    # Permissions Policy - restrict browser features
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # Cross-Origin isolation against Spectre attacks
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    
    # Cache control for sensitive content
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    
    # Hide server version information
    response.headers.pop('Server', None)
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
# Updated for demo
