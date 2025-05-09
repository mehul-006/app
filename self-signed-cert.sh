#!/bin/bash
# generate-self-signed-cert.sh
# Script to generate a self-signed TLS certificate for development use

# Create a directory for the certificates
mkdir -p certs
cd certs

# Generate a private key
openssl genrsa -out tls.key 2048

# Create a self-signed certificate valid for 365 days
openssl req -x509 -new -nodes -key tls.key -sha256 -days 365 -out tls.crt \
  -subj "/CN=app.example.com/O=MyApp/C=US" \
  -addext "subjectAltName = DNS:app.example.com, DNS:pgadmin.example.com"

# Create a Kubernetes TLS secret from the generated files
kubectl create secret tls tls-secret --cert=tls.crt --key=tls.key

echo "Self-signed certificate created and added as Kubernetes secret 'tls-secret'"
echo "Certificate details:"
openssl x509 -in tls.crt -text -noout | grep -E 'Subject:|Not|DNS:'
