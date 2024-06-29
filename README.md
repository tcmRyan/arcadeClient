
```shell
python3 -m venv /some/path
python3 -m pip install -r requiremets.txt
alembic upgrade head
python3 -m client.main
```

RaspberryPI setup notes
```shell
# enable wifi
iwconfig
# run wifi config
sudo wifi.sh
# ensure time is sychronized
sudo rdate time.nist.gov
# ensure ca certificates are install.
tce-load -wi ca-certificates
# point git to certificate directory
git config –global http.sslcapath /usr/local/etc/ssl/certs
# clone repository
https://github.com/tcmRyan/arcadeClient.git
```
