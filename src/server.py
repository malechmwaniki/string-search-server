"""TCP String Search Server."""
import socket
import threading
import time
import configparser
import os
import sys
import ssl
from typing import Tuple
from searcher import FileSearcher


# Load configuration
config = configparser.ConfigParser()
if not config.read('config.ini'):
    print("ERROR: config.ini not found or invalid")
    sys.exit(1)

try:
    cfg = config['SERVER']
    HOST = cfg.get('host', '0.0.0.0')
    PORT = cfg.getint('port', 44445)
    FILEPATH = os.path.expanduser(cfg.get('linuxpath'))
    REREAD = cfg.getboolean('REREAD_ON_QUERY', fallback=False)
    SSL_ENABLED = cfg.getboolean('SSL_ENABLED', fallback=False)
    CERT_PATH = cfg.get('cert_path', 'cert.pem')
    KEY_PATH = cfg.get('key_path', 'key.pem')
except Exception as e:
    print(f"Config error: {e}")
    sys.exit(1)

# Initialize searcher
searcher = FileSearcher(FILEPATH, REREAD)

# Setup SSL if enabled
ssl_context = None
if SSL_ENABLED:
    if not os.path.exists(CERT_PATH) or not os.path.exists(KEY_PATH):
        print("SSL enabled but certificate or key not found")
        sys.exit(1)
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile=CERT_PATH, keyfile=KEY_PATH)


def handle_client(conn: socket.socket, addr: Tuple[str, int]) -> None:
    """Handle individual client connection."""
    start = time.perf_counter()
    try:
        # Receive data (max 1024 bytes)
        data = conn.recv(1024).rstrip(b'\x00')
        query = data.decode('utf-8', errors='ignore').strip()
        
        # Search for string
        found = searcher.exists(query)
        response = "STRING EXISTS\n" if found else "STRING NOT FOUND\n"
        
        # Calculate elapsed time
        elapsed_ms = (time.perf_counter() - start) * 1000
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Log debug info
        print(
            f"DEBUG: [{ts}] IP={addr[0]} Port={addr[1]} "
            f"Query=\"{query[:50]}\" Time={elapsed_ms:.3f}ms "
            f"Result={'EXISTS' if found else 'NOT_FOUND'}"
        )
        
        # Send response
        conn.sendall(response.encode('utf-8'))
        
    except Exception as e:
        print(f"DEBUG: Client error {addr}: {e}")
    finally:
        conn.close()


def main() -> None:
    """Main server loop."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(130)
    
    print("=" * 60)
    print("String Search Server Started")
    print("=" * 60)
    print(f"Listening on: {HOST}:{PORT}")
    print(f"Search file: {FILEPATH}")
    print(f"REREAD_ON_QUERY: {REREAD}")
    print(f"SSL enabled: {SSL_ENABLED}")
    if searcher.lines_set:
        print(f"Lines loaded: {len(searcher.lines_set)}")
    else:
        print("Lines loaded: dynamic (reread mode)")
    print("=" * 60)
    
    while True:
        try:
            conn, addr = server_socket.accept()
            
            # Wrap with SSL if enabled
            if SSL_ENABLED and ssl_context:
                try:
                    conn = ssl_context.wrap_socket(conn, server_side=True)
                except ssl.SSLError as e:
                    print(f"SSL handshake failed from {addr}: {e}")
                    conn.close()
                    continue
            
            # Handle in new thread
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True
            t.start()
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Accept error: {e}")


if __name__ == "__main__":
    main()