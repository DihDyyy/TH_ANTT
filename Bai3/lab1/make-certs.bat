@echo off
setlocal enabledelayedexpansion

cd /d %~dp0

set "OPENSSL=openssl"
if exist "C:\Program Files\Git\usr\bin\openssl.exe" set "OPENSSL=C:\Program Files\Git\usr\bin\openssl.exe"

mkdir certs\ca 2>nul
mkdir certs\server 2>nul
mkdir certs\client 2>nul

:: CA
"%OPENSSL%" genrsa -out certs\ca\ca.key 2048
"%OPENSSL%" req -x509 -new -nodes -key certs\ca\ca.key -sha256 -days 3650 -out certs\ca\ca.crt -config openssl.cnf -extensions v3_ca

:: Server
"%OPENSSL%" genrsa -out certs\server\server.key 2048
"%OPENSSL%" req -new -key certs\server\server.key -out certs\server\server.csr -subj "/C=VN/ST=HN/L=HN/O=MyOrg/OU=IT Dept/CN=localhost"
"%OPENSSL%" x509 -req -in certs\server\server.csr -CA certs\ca\ca.crt -CAkey certs\ca\ca.key -CAcreateserial -out certs\server\server.crt -days 365 -sha256

:: Client
"%OPENSSL%" genrsa -out certs\client\client.key 2048
"%OPENSSL%" req -new -key certs\client\client.key -out certs\client\client.csr -subj "/C=VN/ST=HN/L=HN/O=MyOrg/OU=IT Dept/CN=client"
"%OPENSSL%" x509 -req -in certs\client\client.csr -CA certs\ca\ca.crt -CAkey certs\ca\ca.key -CAcreateserial -out certs\client\client.crt -days 365 -sha256

move certs\ca\ca.srl certs\ca\ca.srl.bak >nul 2>&1

echo.
echo ===============================
echo Cac chung chi da tao xong!
echo - CA: certs\ca\
echo - Server: certs\server\
echo - Client: certs\client\
echo ===============================
pause