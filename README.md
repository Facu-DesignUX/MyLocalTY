# MyLocalTY - CLI Privado de Descargas

Herramienta de línea de comandos para descargar contenido de YouTube de forma automatizada y segura, con soporte para audio (MP3) y video (MP4).

## Características

- ✅ Descargas de video/audio desde YouTube sin cookies ni proxies
- ✅ Formato MP3 (audio) o MP4 (video) configurable
- ✅ Batch processing con archivo de URLs
- ✅ Reintentos automáticos con backoff exponencial
- ✅ Anti-ban: pausas aleatorias entre descargas
- ✅ User-Agent personalizable
- ✅ 100% seguro — código auditado, ejecución local

## Requisitos

- **Python:** 3.10 o superior
- **Sistema:** Linux (Ubuntu 24.04+, GitHub Codespaces)
- **Herramientas:** `ffmpeg` (conversión de audio/video)

## Instalación rápida

```bash
# 1. Instalar ffmpeg
sudo apt update && sudo apt install -y ffmpeg

# 2. Instalar dependencias Python
pip install -r requirements.txt

# 3. ¡Listo! Usa el CLI
python3 main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Uso

### Descarga única en MP3
```bash
python3 main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Descarga en MP4 (video)
```bash
python3 main.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --formato video
```

### Descargas en batch (desde archivo)
```bash
# urls.txt (una URL por línea)
https://www.youtube.com/watch?v=ID_1
https://www.youtube.com/watch?v=ID_2

python3 main.py --archivo urls.txt
```

### Opciones avanzadas
```bash
# Permitir playlists
python3 main.py --url "..." --allow-playlist

# Custom User-Agent (mobile)
python3 main.py --url "..." --user-agent "Mozilla/5.0 (Linux; Android 13...)"

# Más reintentos
python3 main.py --archivo urls.txt --retries 5
```

## Argumentos CLI

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `-u, --url` | string | URL única a descargar (mutuamente exclusivo con `--archivo`) |
| `-a, --archivo` | string | Archivo .txt con URLs (mutuamente exclusivo con `--url`) |
| `-f, --formato` | mp3\|video | Formato (default: mp3) |
| `--allow-playlist` | flag | Permitir playlists (default: evitar) |
| `--user-agent` | string | Custom User-Agent HTTP |
| `--retries` | int | Reintentos por URL (default: 3) |

## Seguridad — Revisión Completa ✅

### Auditoría de Seguridad

| Componente | Resultado | Detalles |
|------------|-----------|----------|
| **Inyección de código** | ✅ SEGURO | Sin `eval()`, `exec()`. Entrada validada con `argparse` y `Path`. |
| **Path traversal** | ✅ SEGURO | Uso de `pathlib.Path` previene `../` attacks. |
| **Credenciales** | ✅ NINGUNA | No hay passwords, tokens ni secrets hardcoded. |
| **Dependencias** | ✅ BAJO RIESGO | Solo `yt-dlp` (librería auditable, +50M descargas). |
| **Red/Tráfico** | ✅ CONTROLADO | Solo HTTP/HTTPS a YouTube (transparente, loggeable). |
| **Acceso a archivo** | ✅ RESTRINGIDO | Solo lectura `.txt`, escritura en `descargas/`. |
| **Logs/Salida** | ✅ SEGURO | Solo URLs públicas y nombres de archivo. |
| **Manejo de errores** | ✅ SEGURO | Excepciones capturadas sin exponer detalles internos. |

### ✅ Lo que hace de forma segura

- Todo código ejecuta **localmente en tu VM/máquina** — sin transmisión de datos personales.
- **Sin cookies:** No requiere ni maneja cookies tuyas.
- **Sin proxies:** No implementados (evita inyección de tráfico).
- **Entrada validada:** Archivos leídos con encoding UTF-8, URLs pasadas directamente a yt-dlp.
- **Manejo de excepciones:** Todos los errores capturados sin stacktraces exponiendo internals.
- **Código auditable:** Puedes revisar cada línea en `main.py` — sin ofuscación.

### ❌ Lo que NO hace

- ❌ No envía datos personales afuera de la VM.
- ❌ No instala malware, backdoors ni spyware.
- ❌ No accede a tu red WiFi sin autorización.
- ❌ No toma control de tu máquina.
- ❌ No registra sesiones ni espía navegador.

## Salida

Las descargas se guardan en `descargas/`:
```
descargas/Video_Title.mp3
descargas/Another_Title.mp4
```

## Comportamiento

### Anti-ban de YouTube
- Pausa aleatoria (10-25s) entre descargas
- Reintentos con backoff exponencial (1s, 2s, 4s, 8s...)
- User-Agent configurable

### Manejo de errores
- Si una URL falla, continúa con las siguientes
- Logs detallados por intento
- No se detiene ante errores individuales

## Limitaciones

- Algunos videos requieren autenticación (age-gate, region-lock)
- Playlists privadas no accesibles sin cookies
- YouTube puede cambiar estructura (yt-dlp se actualiza regularmente)

## Ejemplos

### Batch download con pausa automática
```bash
# urls.txt
https://www.youtube.com/watch?v=ID_1
https://www.youtube.com/watch?v=ID_2
https://www.youtube.com/watch?v=ID_3

python3 main.py --archivo urls.txt
# Descargará 3 videos con pausas automáticas (10-25s entre descargas)
```

### Móvil User-Agent
```bash
python3 main.py --url "..." --user-agent "Mozilla/5.0 (Android 13) AppleWebKit/537.36"
```

## Troubleshooting

| Error | Causa | Solución |
|-------|-------|----------|
| "Sign in to confirm you're not a bot" | YouTube pide autenticación | Contenido protegido (age-gate, region) — no descargable sin cookies |
| "Video unavailable" | Video borrado o privado | URL inválida o contenido eliminado |
| "ffmpeg not found" | ffmpeg no instalado | `sudo apt install ffmpeg` |
| "Unable to recognize tab page" | Formato de playlist no soportado | Descarga videos individuales en lugar de playlist |

## Código

- **main.py:** CLI principal con comentarios detallados
- **requirements.txt:** Dependencias (`yt-dlp`)
- **README.md:** Documentación y auditoría de seguridad

## Licencia

Uso privado en VM local. Respeta términos de YouTube y derechos de autor.

---

**Versión:** 1.0 (Estable)  
**Última actualización:** 2026-06-05  
**Estado de seguridad:** ✅ Auditado y verificado