# Control de Subway Surfers con la Cabeza (MediaPipe Pose + OpenCV)

[![CI](https://github.com/hugoocaabero/subway_surfers/actions/workflows/ci.yml/badge.svg)](https://github.com/hugoocaabero/subway_surfers/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE) ![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![opencv-python](https://img.shields.io/pypi/v/opencv-python?label=opencv-python) ![mediapipe](https://img.shields.io/pypi/v/mediapipe?label=mediapipe) ![pyautogui](https://img.shields.io/pypi/v/pyautogui?label=pyautogui)

Controla Subway Surfers (o juegos similares en emulador) moviendo la cabeza. El sistema usa MediaPipe Pose para detectar la posición de la nariz y `pyautogui` para enviar pulsaciones de teclas al emulador.

## Requisitos
- Python 3.10+
- Cámara web
- Emulador (p.ej. BlueStacks o Nox) con teclas mapeadas
- Dependencias: `mediapipe`, `opencv-python`, `pyautogui` (si no está, se simula en consola)

## Instalación (Windows PowerShell)
```powershell
# Dentro de esta carpeta (subway_surfers)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Instalación rápida (Linux/Mac)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Entorno de desarrollo (lint/format)
```powershell
pip install -r dev-requirements.txt
ruff check .
black .
```

### Pre-commit hooks
```powershell
pip install -r dev-requirements.txt
pre-commit install
# Ejecutar sobre todos los archivos la primera vez
pre-commit run --all-files
```

## Uso
```powershell
python subway_surfers.py
```
- Pulsa `c` para CALIBRAR la posición neutral (mira al centro).
- `+ / -` para ajustar SENSIBILIDAD.
- `r` para resetear calibración.
- `q` o `ESC` para salir.

Acciones al mover la cabeza:
- Arriba: SALTAR
- Abajo: DESLIZAR
- Izquierda/Derecha: moverse de carril

Por defecto, las teclas están configuradas para BlueStacks: flechas `up/down/left/right`. Puedes cambiar a Nox editando el diccionario `EMULATOR_CONFIGS` en el script.

## Consejos
- Enfoca la ventana del emulador para que `pyautogui` envíe las teclas correctamente.
- Si las teclas no se envían, se mostrará “SIMULACIÓN”; instala `pyautogui` y ejecuta como administrador si es necesario.
- Mejora la iluminación y evita fondos muy complejos para una detección más estable.

### Problemas comunes
- En macOS, autoriza “Accesibilidad” para `pyautogui` en Preferencias del Sistema.
- En Linux con Wayland, `pyautogui` puede requerir Xorg.
- En emuladores, verifica que las teclas estén mapeadas a `up/down/left/right`.

## Releases
Publica una versión creando un tag:
```powershell
git tag v0.1.0
git push origin v0.1.0
```
El workflow `Release` adjuntará un `.zip` con el script y archivos esenciales.

## Licencia
Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo [LICENSE](./LICENSE) para más detalles.
