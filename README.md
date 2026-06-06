# voice-lab

voice-lab es un sistema privado para preparar audios, organizar datasets y ejecutar flujos futuros de voice-to-voice / voice conversion en batch con RVC/Applio, FFmpeg y Python.

La Fase 1B convierte los placeholders de audio en herramientas reales para preparar audios con FFmpeg. No instala dependencias, no clona repositorios externos, no entrena modelos, no ejecuta inferencia RVC real y no toca Docker Swarm, Portainer, Traefik ni ningun stack existente del servidor.

## Uso autorizado

Este proyecto esta pensado para uso personal o para voces con autorizacion explicita. No debe usarse para suplantacion, fraude, acoso, engaño, llamadas automatizadas, servicio publico no autorizado ni generacion de identidad vocal sin consentimiento.

## Arquitectura CPU/GPU

### Droplet CPU normal

- Preparar estructura del proyecto.
- Limpiar audios y convertir MP3/M4A/WAV a WAV limpio.
- Organizar datasets.
- Guardar modelos entrenados.
- Ejecutar batch nocturno con baja prioridad.

### GPU Droplet temporal

- Entrenar modelos RVC/Applio.
- Exportar `.pth`, `.index`, configuracion y logs.
- Sincronizar resultados hacia el Droplet CPU.
- Destruir el GPU Droplet al terminar.

## Fases MVP

### Fase 1: esqueleto seguro

- Crear estructura profesional del repositorio.
- Definir configuracion base.
- Crear scripts placeholder seguros.
- Preparar helpers Python minimos.

### Fase 1B: pipeline real de preparacion de audio

- Tomar entradas MP3, M4A o WAV.
- Convertirlas a WAV limpio mono, `40000 Hz` por defecto y PCM signed 16-bit little endian.
- Exportar una version MP3 con `libmp3lame`.
- Inspeccionar audio con `ffprobe` si esta disponible.
- Registrar logs basicos por job.
- Validar el flujo con FFmpeg sin integrar RVC todavia.

### MVP 1: inferencia individual

- Convertir una entrada de audio a WAV limpio.
- Ejecutar inferencia con un modelo ya entrenado.
- Exportar WAV y MP3.
- Registrar logs basicos por job.

### MVP 2: batch nocturno

- Leer archivos desde `input/pending/`.
- Crear jobs en `queue/jobs/`.
- Procesar de a pocos trabajos con baja prioridad.
- Mover jobs a `queue/done/` o `queue/failed/`.

### MVP 3: entrenamiento GPU

- Sincronizar dataset limpio hacia GPU Droplet temporal.
- Ejecutar entrenamiento RVC/Applio.
- Traer modelos, indices, configs y logs.
- Guardar artefactos en `models/mi_voz/`.

## Estructura de carpetas

```text
/opt/voice-lab/
  README.md
  .env.example
  requirements-cpu.txt
  requirements-gpu.txt
  app/
    config.py
    audio_utils.py
    jobs.py
    rvc_runner.py
    main.py
  scripts/
    setup_cpu.sh
    setup_gpu.sh
    prepare_dataset.sh
    train_gpu.sh
    infer_one.sh
    run_batch_lowprio.sh
    sync_to_gpu.sh
    sync_from_gpu.sh
    check_health.sh
  input/
  queue/
  processing/
  output/
  datasets/
  models/
  logs/
  tmp/
```

## Fase 1B: comandos de prueba

Revisar herramientas y carpetas:

```bash
./scripts/check_health.sh
```

Inspeccionar un audio:

```bash
python3 -m app.cli probe --input input/manual/test.mp3
```

Convertir una entrada a WAV limpio:

```bash
python3 -m app.cli normalize --input input/manual/test.mp3 --output processing/test.clean.wav
```

Exportar MP3 desde el WAV limpio:

```bash
python3 -m app.cli export-mp3 --input-wav processing/test.clean.wav --output-mp3 output/mp3/test.clean.mp3
```

Validar el flujo individual placeholder:

```bash
./scripts/infer_one.sh input/manual/test.mp3 mi_voz
```

`infer_one.sh` actualmente valida el pipeline de audio: normaliza a WAV limpio, copia ese WAV a `output/wav/` como placeholder y exporta MP3. Todavia no hace conversion de voz ni llama RVC/Applio.

## Flujo de inferencia individual

1. Colocar un archivo de audio autorizado en `input/manual/`.
2. Ejecutar `scripts/infer_one.sh input/manual/audio.mp3 mi_voz`.
3. Normalizar el audio a WAV limpio en `processing/`.
4. Copiar el WAV limpio a `output/wav/` como placeholder hasta integrar RVC/Applio.
5. Guardar el MP3 en `output/mp3/`.
6. Registrar eventos en `logs/jobs/`.

En Fase 1B este flujo procesa audio real con FFmpeg, pero no ejecuta inferencia RVC real.

## Flujo futuro de batch nocturno

1. Colocar audios autorizados en `input/pending/`.
2. Crear jobs simples en `queue/jobs/`.
3. Ejecutar un worker con baja prioridad usando herramientas como `nice`, `ionice`, `flock` o `systemd-run`.
4. Procesar como maximo `MAX_BATCH_JOBS` en paralelo.
5. Mover trabajos finalizados a `queue/done/` o `queue/failed/`.

En Fase 1 no se procesa audio real.

## Flujo futuro de entrenamiento GPU

1. Preparar dataset en `datasets/mi_voz/raw/`.
2. Limpiar y normalizar hacia `datasets/mi_voz/clean/`.
3. Sincronizar dataset hacia un GPU Droplet temporal.
4. Entrenar con RVC/Applio en GPU.
5. Sincronizar `.pth`, `.index`, configs y logs hacia `models/mi_voz/`.
6. Apagar y destruir el GPU Droplet temporal.

## Nota sobre Docker Swarm

Esta fase no modifica Docker, Docker Swarm, Portainer, Traefik, n8n, Postgres, Redis, Evolution API ni ningun stack existente. voice-lab se prepara como repositorio local independiente dentro de `/opt/voice-lab`.
