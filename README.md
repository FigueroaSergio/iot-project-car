## Installatione

```sh
    pip install requirements.txt
```

####  conda

```sh
    conda create --name <my-env> python=3.11
    conda active <my-env>
    conda install --yes --file requirements.txt
```

####  run
```sh
    sudo pigpiod
    python server_controller.py
```
Dopo aver eseguito `python server_controller.py` inserire la password: hola

Per visualizzare la telecamera per la autonoma inserire nel browser del dispositivo che farà da telecamera il seguente url.

url camera: [ip_rasp]:[port]/static/index.html

Per trasmettere il video della telecamera e inviare comandi all'auto, passare alla modalità di guida autonoma e visualizzare la posizione GPS (se il dispositivo che fa da telecamera lo supporta), inserire nel browser il seguente url

url watcher: [ip_rasp]:[port]/static/watcher.html