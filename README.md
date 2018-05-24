# Ceres Controller

### Generating certificates

    openssl req -x509 -newkey rsa:2048 -days 3650 -keyout rsa_private.pem -nodes -out rsa_cert.pem -subj "/CN=unused"
    
### Run

    python -m ceres -k ./rsa_private.pem