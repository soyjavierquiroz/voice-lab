# Flujo CPU/GPU temporal

Este documento prepara el flujo reproducible entre el Droplet CPU normal y un GPU Droplet temporal para entrenamiento futuro RVC/Applio. En esta fase no se entrena, no se instala CUDA, no se descarga Applio/RVC y no se integra RVC todavia.

## Proposito del GPU Droplet temporal

El servidor CPU mantiene el repositorio, prepara datasets y conserva los modelos recibidos. El GPU Droplet se crea solo cuando haga falta entrenar, recibe una copia controlada del proyecto y dataset, ejecutara setup/entrenamiento en una fase futura, exportara artefactos y despues se destruye.

## Por que no clonar el servidor completo

El servidor actual tiene servicios ajenos a voice-lab. No conviene copiar Docker, Swarm, Portainer, Traefik, stacks, volumenes ni configuracion de produccion hacia una maquina temporal. El GPU Droplet solo necesita el repo de voice-lab, datasets autorizados y espacio para producir modelos.

## Preparacion en CPU

1. Colocar audios autorizados en `datasets/<dataset>/raw/`.
2. Preparar WAV limpios:

```bash
./scripts/prepare_dataset.sh mi_voz
```

3. Revisar reportes en `datasets/<dataset>/metadata/`.
4. Confirmar que `datasets/<dataset>/clean/` contiene WAV reales antes de intentar el placeholder de entrenamiento.

## Creacion manual futura del GPU Droplet

Cuando se vaya a entrenar, crear manualmente un GPU Droplet temporal con acceso SSH. Todavia no hay automatizacion de creacion/destruccion desde este repo.

Despues de crearlo, configurar `.env` en el servidor CPU:

```bash
cp .env.example .env
```

Variables necesarias:

```bash
GPU_HOST=IP_O_HOST_DEL_GPU
GPU_USER=root
GPU_PORT=22
GPU_SSH_KEY=/ruta/a/la/llave_privada
GPU_PROJECT_PATH=/opt/voice-lab
RSYNC_DELETE=false
DEFAULT_DATASET_NAME=mi_voz
DEFAULT_MODEL_NAME=mi_voz
```

`GPU_SSH_KEY` puede quedar vacio si SSH ya resuelve la identidad por agente o configuracion local.

## Enviar proyecto/dataset al GPU

Por defecto el script es dry-run:

```bash
./scripts/sync_to_gpu.sh --dry-run
```

Ejecucion real:

```bash
./scripts/sync_to_gpu.sh --yes
```

El envio incluye `app/`, `scripts/`, `requirements-*.txt`, `README.md`, `.env.example`, `docs/`, `datasets/` y `models/`. Preserva `datasets/raw` y `datasets/clean` porque son necesarios para entrenar. Excluye colas, outputs, temporales, logs `.log`, `.git/`, `.venv/` y caches Python.

Si `RSYNC_DELETE=true`, `--delete` solo se aplica en modo `--yes`. En dry-run el script lo anuncia sin borrar nada.

## setup_gpu futuro

En el GPU Droplet:

```bash
./scripts/setup_gpu.sh
```

Hoy solo imprime checklist y verifica si existe `nvidia-smi`. En una fase futura debera validar CUDA, Python, crear un entorno GPU separado e instalar PyTorch CUDA y dependencias Applio/RVC. No ejecuta `apt` ni `pip` todavia.

## train_gpu futuro

En el GPU Droplet:

```bash
./scripts/train_gpu.sh --dataset mi_voz --model mi_voz
```

Hoy valida que exista `datasets/<dataset>/clean/` con WAV limpios y crea placeholders en `models/<model>/`. No crea `.pth` ni `.index` falsos y no entrena.

## Recibir modelo desde GPU

Dry-run:

```bash
./scripts/sync_from_gpu.sh --model mi_voz --dry-run
```

Ejecucion real:

```bash
./scripts/sync_from_gpu.sh --model mi_voz --yes
```

Este script trae solamente `models/<model>/` desde `${GPU_USER}@${GPU_HOST}:${GPU_PROJECT_PATH}/models/<model>/` hacia `/opt/voice-lab/models/<model>/`. No trae datasets ni outputs.

`--delete` no se usa por defecto. Si `RSYNC_DELETE=true`, solo se permite con `--yes` y se muestra una advertencia.

## Validacion de modelo recibido

Despues del sync real, revisar:

```bash
ls -lah models/mi_voz/
find models/mi_voz -maxdepth 2 -type f
```

En una fase futura se esperaran:

- `model.pth`
- `model.index`
- `config.json`
- `train_notes.md`
- `logs/`

En la fase actual puede existir solo documentacion placeholder.

## Destruir el GPU Droplet

Cuando los artefactos esten copiados y validados en el CPU, destruir el GPU Droplet temporal.

Advertencia de costos: apagar no basta. Mientras el Droplet exista, puede seguir generando costos de recursos reservados, volumenes o snapshots. Destruirlo cuando termine el trabajo.

## Uso autorizado de voces

Usar solo voces propias o con autorizacion explicita. No usar voice-lab para suplantacion, fraude, acoso, engaño, llamadas automatizadas, servicio publico no autorizado ni generacion de identidad vocal sin consentimiento.
