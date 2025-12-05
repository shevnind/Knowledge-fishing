from api import app

import ssl
from http.server import HTTPServer

from database import create_table


if __name__ == "__main__":
    create_table()

    import uvicorn

    # localhost:8443

    uvicorn.run(
        app, 
        host="127.0.0.1",
        port=8000,  # HTTPS порт
        # ssl_keyfile="../ssl/certificate.key",
        # ssl_certfile="../ssl/certificate.crt",
        # ssl_ca_certs="../ssl/certificate_ca.crt"  # опционально
    )

    # uvicorn.run(
    #     app, 
    #     host="0.0.0.0",
    #     port=443,  # HTTPS порт
    #     ssl_keyfile="../ssl/certificate.key",
    #     ssl_certfile="../ssl/certificate.crt",
    #     ssl_ca_certs="../ssl/certificate_ca.crt"  # опционально
    # )
