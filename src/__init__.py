# ============================================================================
# __init__.py - Paquete src del pipeline
# ============================================================================

"""
Pipeline UD4: Análisis reproducible e idempotente de secuencias

Módulos:
  - utils: Utilidades comunes (config, logging, cálculos)
  - manifest: Gestión de hashes y idempotencia
  - validate: Validación de datos de entrada
  - process: Procesamiento de secuencias (GC, longitud, filtrado)
  - report: Generación de reportes
  - run_pipeline: Orquestador principal
"""

__version__ = "1.0"
__author__ = "edwinges-max"

from . import utils
from . import manifest
from . import validate
from . import process
from . import report

__all__ = ["utils", "manifest", "validate", "process", "report"]
