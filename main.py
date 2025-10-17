from api import app

import ssl
from http.server import HTTPServer


# if __name__ == "__main__":
#     create_table()

#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Проверяем аргументы командной строки
    import sys
    ssl_enabled = "--ssl-certfile" in sys.argv
    
    if ssl_enabled:
        certfile_index = sys.argv.index("--ssl-certfile") + 1
        keyfile_index = sys.argv.index("--ssl-keyfile") + 1
        certfile = sys.argv[certfile_index]
        keyfile = sys.argv[keyfile_index]
        
        # Создаем SSL контекст
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile, keyfile)
        
        server = HTTPServer(('0.0.0.0', 443), app)  # HTTPS на порту 443
        server.socket = context.wrap_socket(server.socket, server_side=True)
        print("Starting HTTPS server on port 443...")
    else:
        server = HTTPServer(('0.0.0.0', 8000), app)
        print("Starting HTTP server on port 8000...")
    
    server.serve_forever()