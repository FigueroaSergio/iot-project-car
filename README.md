## Tools 🔧
* Raspberry PI 3B+
* Servo motore
* Sensore a ultrasuoni
* H-bridge
* Motore DC
* Uno o più smartphone (per la fotocamera)
* Visual Studio Code (per editing codice e run debug)
* VNC (per desktop remoto e run debug)

## Installazione 💻

```sh
    pip install requirements.txt
```

####  conda

```sh
    conda create --name <my-env> python=3.11
    conda active <my-env>
    conda install --yes --file requirements.txt
```

####  VSC
Installare estensione di Visual Studio Code `Remote SSH` per il tunneling (modifica dei file su Raspberry tramite VSC da remoto).

##  run 🚗
ATTENZIONE: i dispositivi che si connetteranno tra di loro devono appartenere alla stessa rete (fotocamera, RPI, computer, ecc.).

Su VNC o applicazione che supporta desktop remoto, connettersi al Raspberry, aprire un terminale sulla cartella corrente del progetto e eseguire i seguenti comandi:
```sh
    sudo pigpiod
    python server_controller.py
```
Dopo aver eseguito `python server_controller.py` inserire la password `hola`.

Per visualizzare la telecamera per la guida autonoma inserire nel browser del dispositivo che farà da telecamera il seguente url.

URL CAMERA: `[ip_rasp]:[port]/static/index.html`

Per trasmettere lo stream video della telecamera e inviare comandi all'auto, passare alla modalità di guida autonoma e visualizzare la posizione GPS (se il dispositivo che fa da telecamera lo supporta), inserire nel browser il seguente url

URL WATCHER: `[ip_rasp]:[port]/static/watcher.html`