# mi_voz training notes

Status: placeholder, no entrenado todavia.

- Dataset esperado: mi_voz
- Uso autorizado: requerido para todo audio de origen y modelo resultante.
- Estado actual: no existe modelo entrenado, `.pth` ni `.index`.

Proximos pasos:

1. Preparar un dataset real con audios autorizados en `datasets/mi_voz/raw/`.
2. Generar WAV limpios con `./scripts/prepare_dataset.sh mi_voz`.
3. Sincronizar el proyecto hacia un GPU Droplet temporal.
4. Ejecutar el placeholder `./scripts/train_gpu.sh --dataset mi_voz --model mi_voz`.
5. En una fase futura, integrar entrenamiento RVC/Applio real.
