# Pipeline UD4: Análisis de Secuencias ADN

## Descripción

Este es un pipeline para analizar secuencias ADN con:
- Validación de datos
- Cálculo de métricas (longitud, fracción GC)
- Filtrado por umbrales
- Reporte final

## Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes Python)

## Instalación

Abre PowerShell en la carpeta del proyecto y ejecuta:

\\\
pip install -r requirements.txt
\\\

Esto instala todas las librerías necesarias.

## Estructura del Proyecto

\\\
ud4_pipeline/
├── config.yaml                    # Configuración (parámetros)
├── requirements.txt               # Librerías necesarias
├── README.md                      # Este archivo
│
├── src/                           # Código Python
│   ├── utils.py                  # Funciones auxiliares
│   ├── manifest.py               # Control de cambios
│   ├── validate.py               # Validación de datos
│   ├── process.py                # Procesamiento
│   ├── report.py                 # Generación de reportes
│   └── run_pipeline.py           # Orquestador (EJECUTAR ESTE)
│
├── data/
│   ├── raw/
│   │   └── sequences.tsv         # Datos de entrada
│   └── processed/                # Datos procesados (generados)
│
├── results/                       # Resultados (generados)
└── logs/                          # Logs (generados)
\\\

## Cómo Ejecutar

### Paso 1: Instalar dependencias

\\\ash
pip install -r requirements.txt
\\\

### Paso 2: Ejecutar el pipeline

\\\ash
python src/run_pipeline.py --config config.yaml
\\\

El pipeline hará lo siguiente:
1. Valida el archivo sequences.tsv
2. Calcula longitud y fracción GC
3. Filtra por umbrales
4. Genera reportes

### Salida

El pipeline genera:
- \data/processed/sequences_valid.tsv\ - Datos validados
- \data/processed/sequences_metrics.tsv\ - Con métricas (longitud, GC)
- \data/processed/sequences_filtered.tsv\ - Filtrados por umbrales
- \esults/final_report.md\ - Reporte en Markdown
- \esults/validation_report.md\ - Reporte de validación
- \esults/summary.json\ - Resumen en JSON
- \esults/metadata.json\ - Histórico de ejecuciones

## Configurar Parámetros

Abre \config.yaml\ y modifica los umbrales:

\\\yaml
thresholds:
  min_length: 10        # Longitud mínima (en bp)
  max_length: 1000      # Longitud máxima (en bp)
  gc_min: 0.0           # Fracción GC mínima (0.0 a 1.0)
  gc_max: 1.0           # Fracción GC máxima (0.0 a 1.0)
\\\

## Reproducibilidad

Si ejecutas el pipeline DOS VECES sin cambiar nada:
- Primera vez: Procesa todo
- Segunda vez: **SALTA el procesamiento** (idempotencia)

Esto se debe a que calcula hashes de los datos y parámetros.

Para forzar reejecución:

\\\ash
python src/run_pipeline.py --config config.yaml --force
\\\

## Ejemplo de Uso

### 1. Archivo de entrada (\data/raw/sequences.tsv\)

\\\
sample_id       sequence
sample_001      ATCGATCGATCGATCGATCG
sample_002      GCTAGCTAGCTAGCTAGCTA
sample_003      AAAAAAAAAA
sample_004      ATGCGTACGTACGTACGTACGTACGTACGT
sample_005      GCGCGCGCGCGCGCGCGCGCGCGCGCGC
\\\

### 2. Ejecutar

\\\ash
python src/run_pipeline.py --config config.yaml
\\\

### 3. Resultado (\esults/final_report.md\)

Se genera un reporte con tablas y estadísticas.

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'yaml'"
Ejecuta: \pip install pyyaml\

### Error: "Archivo no encontrado: data/raw/sequences.tsv"
Asegúrate de que el archivo existe en \data/raw/\

### El pipeline no hace nada (SKIP)
Es la idempotencia funcionando. Usa \--force\ para forzar reejecución.

## Conceptos Importantes

- **Validación**: Verifica que los datos sean correctos
- **Métrica GC**: Fracción de G+C en la secuencia (importante en biología)
- **Idempotencia**: Mismo input = mismo output siempre
- **Reproducibilidad**: Runlog completo para reproducir resultados
