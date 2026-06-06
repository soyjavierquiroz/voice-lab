# voice-lab

voice-lab es un sistema privado para preparar audios, organizar datasets y ejecutar flujos futuros de voice-to-voice / voice conversion en batch con RVC/Applio, FFmpeg y Python.

Esta fase crea solamente la estructura inicial del repositorio. No instala dependencias, no clona repositorios externos, no entrena modelos, no ejecuta inferencia real y no toca Docker Swarm, Portainer, Traefik ni ningun stack existente del servidor.

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

## Flujo futuro de inferencia individual

1. Colocar un archivo de audio autorizado en `input/manual/`.
2. Ejecutar `scripts/infer_one.sh input/manual/audio.mp3 mi_voz`.
3. Normalizar el audio a WAV limpio en `processing/`.
4. Invocar el motor RVC/Applio configurado.
5. Guardar resultados en `output/wav/` y `output/mp3/`.
6. Registrar eventos en `logs/jobs/`.

En Fase 1 este flujo solo valida argumentos y explica el estado pendiente.

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
