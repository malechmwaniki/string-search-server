import socket
import sys

def search(query, host='localhost', port=44445):
  
    try:
        # socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        #Connect
        sock.connect((host, port))
        
        # Send query
        sock.sendall(query.encode('utf-8'))
        
        # Receive response
        response = sock.recv(1024).decode('utf-8').strip()
        
        sock.close()
        
        return response
        
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 client.py 'search_string'")
        sys.exit(1)
    
    query = sys.argv[1]
    result = search(query)
    print(result)