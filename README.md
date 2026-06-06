# voice-lab

voice-lab es un sistema privado para preparar audios, organizar datasets y ejecutar flujos futuros de voice-to-voice / voice conversion en batch con RVC/Applio, FFmpeg y Python.

La Fase 2A agrega preparacion real de datasets para entrenamiento futuro de voces RVC/Applio. Convierte audios autorizados desde `datasets/<dataset>/raw/` hacia WAV limpios en `datasets/<dataset>/clean/`, genera metadata y reportes, y mantiene el flujo sin entrenar modelos ni integrar RVC todavia. No instala dependencias, no clona repositorios externos, no entrena modelos, no ejecuta inferencia RVC real y no toca Docker Swarm, Portainer, Traefik ni ningun stack existente del servidor.

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

### Fase 1C: cola batch local

- Leer audios desde `input/pending/`.
- Crear jobs JSON en `queue/jobs/`.
- Evitar duplicados por ruta absoluta de input.
- Procesar un job por ejecucion con baja prioridad usando `nice` e `ionice` si esta disponible.
- Mover jobs terminados a `queue/done/` o `queue/failed/`.
- Seguir usando `infer_one.sh` como placeholder: no hay RVC real todavia.

### Fase 1D: ejecucion limitada y cron seguro

- Mantener `scripts/run_batch_lowprio.sh` como runner real con `flock`, `nice`, `ionice` si esta disponible y `process-all --limit 1`.
- Agregar `scripts/run_batch_limited.sh` como wrapper con una unidad transitoria `systemd` tipo `service`, `systemd-run --wait --collect`, `CPUQuota` y `MemoryMax`.
- Usar `CPU_QUOTA=60%` y `MEMORY_MAX=5G` por defecto, configurables desde `.env`.
- Preparar `scripts/install_cron.sh` para instalar cron solo con `--yes`; por defecto hace `--dry-run`.
- Preparar `scripts/remove_cron.sh` para remover solo la linea de voice-lab, tambien con `--dry-run` por defecto.
- Mantener el flujo sin RVC real todavia: la conversion sigue siendo placeholder con FFmpeg.

### Fase 2A: preparacion real de datasets

- Escanear audios en `datasets/<dataset>/raw/` con `ffprobe` si esta disponible.
- Convertir audios raw a WAV mono `pcm_s16le`, `40000 Hz` por defecto, en `datasets/<dataset>/clean/`.
- Usar filtros prudentes de remuestreo sin cambiar tempo, pitch, emocionalidad ni ritmo de voz.
- Generar `metadata/report.json`, `metadata/report.md` y `logs/prepare_dataset.log`.
- Saltar salidas existentes salvo que se use `--overwrite`.
- Mantener audios raw intactos.
- Todavia no entrena modelos ni integra RVC/Applio.

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
    dataset_cli.py
    jobs.py
    queue_cli.py
    rvc_runner.py
    main.py
  scripts/
    setup_cpu.sh
    setup_gpu.sh
    prepare_dataset.sh
    train_gpu.sh
    infer_one.sh
    run_batch_lowprio.sh
    run_batch_limited.sh
    install_cron.sh
    remove_cron.sh
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

Estructura de dataset por voz:

```text
datasets/mi_voz/
  raw/
  clean/
  metadata/
  logs/
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

## Fase 1C: cola batch placeholder

Colocar un audio autorizado en la cola pendiente:

```bash
cp archivo.mp3 input/pending/
```

Crear jobs JSON para los audios pendientes:

```bash
python3 -m app.queue_cli enqueue-pending
```

Listar jobs en cola, terminados y fallidos:

```bash
python3 -m app.queue_cli list
```

Ejecutar un ciclo batch de baja prioridad:

```bash
./scripts/run_batch_lowprio.sh
```

El batch llama internamente:

```bash
python3 -m app.queue_cli enqueue-pending
python3 -m app.queue_cli process-all --limit 1
```

Los JSON se guardan en `queue/jobs/`, `queue/done/` y `queue/failed/`. Los audios permanecen en `input/pending/` y los jobs referencian su ruta absoluta. La salida se infiere por nombre base:

- `output/wav/<nombre>.clean.wav`
- `output/mp3/<nombre>.clean.mp3`
- `logs/jobs/<nombre>.log`

Por ahora este flujo sigue siendo placeholder sin RVC real: normaliza audio con FFmpeg, copia el WAV limpio como salida WAV y exporta MP3.

## Fase 1D: batch limitado y cron controlado

`run_batch_lowprio.sh` es el runner real. Se encarga de tomar `input/pending/`, crear jobs, adquirir `flock`, bajar prioridad con `nice`/`ionice` y procesar como maximo un job por corrida con `process-all --limit 1`.

`run_batch_limited.sh` es el wrapper seguro para ejecucion nocturna. Llama al runner real dentro de una unidad transitoria `systemd` tipo `service` con limites conservadores:

- `CPUQuota=${CPU_QUOTA:-60%}`
- `MemoryMax=${MEMORY_MAX:-5G}`
- `Nice=19`
- `IOSchedulingClass=idle`

`CPUQuota=60%` en systemd es deliberadamente conservador: protege el servidor y otros servicios, pero puede hacer que el procesamiento tarde mas.

Nota de compatibilidad: en Ubuntu/systemd actual, `systemd-run` no permite combinar `--scope` con `--wait`, por eso el wrapper usa una unidad transitoria tipo `service`.

Ejecutar una corrida limitada manual:

```bash
./scripts/run_batch_limited.sh
```

Revisar la instalacion propuesta de cron sin modificar nada:

```bash
./scripts/install_cron.sh --dry-run
```

Instalar cron solo cuando se confirme explicitamente:

```bash
./scripts/install_cron.sh --yes
```

La linea propuesta por defecto es:

```cron
0 2 * * * /opt/voice-lab/scripts/run_batch_limited.sh >> /opt/voice-lab/logs/cron.log 2>&1
```

El cron futuro llama a `run_batch_limited.sh`, no directamente a `run_batch_lowprio.sh`. No se usa `flock` externo en cron porque `run_batch_lowprio.sh` ya lo aplica internamente.

Revisar la remocion propuesta sin modificar nada:

```bash
./scripts/remove_cron.sh --dry-run
```

## Fase 2A: preparar dataset de voz

Colocar audios autorizados en `raw/`:

```bash
cp mis_audios/*.wav datasets/mi_voz/raw/
```

Escanear sin modificar archivos:

```bash
python -m app.dataset_cli scan --dataset mi_voz
```

Preparar WAV limpios y reportes:

```bash
./scripts/prepare_dataset.sh mi_voz
```

Sobrescribir WAV limpios existentes solo cuando sea intencional:

```bash
./scripts/prepare_dataset.sh mi_voz --overwrite
```

Ver el ultimo reporte humano:

```bash
python -m app.dataset_cli report --dataset mi_voz
```

Recomendaciones para datasets RVC/Applio futuros:

- Minimo viable: 10 minutos limpios.
- Recomendado: 30 a 60 minutos.
- Una sola voz.
- Sin musica.
- Sin eco.
- Sin ruido.
- Sin voces cruzadas.

Esta fase solo prepara el dataset. No entrena modelos, no descarga RVC/Applio y no hace conversion de voz.

## Flujo de inferencia individual

1. Colocar un archivo de audio autorizado en `input/manual/`.
2. Ejecutar `scripts/infer_one.sh input/manual/audio.mp3 mi_voz`.
3. Normalizar el audio a WAV limpio en `processing/`.
4. Copiar el WAV limpio a `output/wav/` como placeholder hasta integrar RVC/Applio.
5. Guardar el MP3 en `output/mp3/`.
6. Registrar eventos en `logs/jobs/`.

En Fase 1B este flujo procesa audio real con FFmpeg, pero no ejecuta inferencia RVC real.

## Flujo de batch nocturno

1. Colocar audios autorizados en `input/pending/`.
2. Crear jobs simples en `queue/jobs/`.
3. Ejecutar `scripts/run_batch_limited.sh` para una corrida controlada con limites de systemd.
4. Procesar como maximo un job por corrida en esta fase.
5. Mover trabajos finalizados a `queue/done/` o `queue/failed/`.

El wrapper limitado llama internamente a `scripts/run_batch_lowprio.sh`, que mantiene el `flock` y la baja prioridad. En Fase 1D se procesa audio real con FFmpeg, pero la conversion de voz sigue siendo placeholder sin RVC real.

## Flujo futuro de entrenamiento GPU

1. Preparar dataset en `datasets/mi_voz/raw/`.
2. Limpiar y normalizar hacia `datasets/mi_voz/clean/`.
3. Sincronizar dataset hacia un GPU Droplet temporal.
4. Entrenar con RVC/Applio en GPU.
5. Sincronizar `.pth`, `.index`, configs y logs hacia `models/mi_voz/`.
6. Apagar y destruir el GPU Droplet temporal.

## Nota sobre Docker Swarm

Esta fase no modifica Docker, Docker Swarm, Portainer, Traefik, n8n, Postgres, Redis, Evolution API ni ningun stack existente. voice-lab se prepara como repositorio local independiente dentro de `/opt/voice-lab`.
