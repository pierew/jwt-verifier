from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
import jwt
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import json
import base64
import os

serverPort = os.environ.get('SERVER_PORT', 8080)

def verify_with_jwts(token: str,jwks_endpoint: str):
    header = jwt.get_unverified_header(token)
    alg = header["alg"]
    kid = header["kid"]
    
    jwk_client = jwt.PyJWKClient(jwks_endpoint)
    key = jwk_client.get_signing_key(kid).key

    token_decoded = jwt.decode(token,key,algorithms=[alg],options={"verify_aud": False, "verify_signature": True})
    return token_decoded

def verify_without_jwks(token: str, public_key: str):
    key = load_pem_x509_certificate(base64.b64decode(public_key.encode('ascii')), default_backend()).public_key()
    header = jwt.get_unverified_header(token)
    alg = header["alg"]
    
    try:
        jwt.decode(token,key,algorithms=[alg],options={"verify_aud": False, "verify_signature": True})
        return {'verified': False}
    except Exception as e:
        return {'verified': False, 'exception': str(e)}

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        query = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        
        response = None
        
        if 'access_token' in query.keys() and 'jwts_endpoint' in query.keys():
            response = verify_with_jwts(token=query['access_token'][0],jwks_endpoint=query['jwts_endpoint'][0])

        elif 'access_token' in query.keys() and 'public_key' in query.keys():
            response = verify_without_jwks(token=query['access_token'][0],public_key=query['public_key'][0])
            
        
        self.wfile.write(bytes(json.dumps(response),"utf-8"))

def main():
    
    webServer = HTTPServer(("0.0.0.0", serverPort), MyServer)
    print("Server started http://%s:%s" % ("0.0.0.0", serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

if __name__ == "__main__":
    main()