# ============================================================================
# run_pipeline.py - Orquestador principal del pipeline
# ============================================================================

import sys
import os
from pathlib import Path

# Agregar directorio actual al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import load_config, ensure_directories, setup_logger
from src.manifest import Manifest, calculate_file_hash, calculate_dict_hash
from src.validate import run_validation
from src.process import run_processing
from src.report import run_reporting

# ============================================================================
# FUNCIONES DE ORQUESTACION
# ============================================================================

def setup_pipeline(config_path="config.yaml"):
    """
    Configura el pipeline: carga config, crea directorios, setup logger.
    
    Args:
        config_path (str): Ruta al archivo de configuración
        
    Returns:
        tuple: (config, logger, log_file)
    """
    # Cargar configuración
    config = load_config(config_path)
    
    # Asegurar que existen los directorios
    ensure_directories(config)
    
    # Setup logger principal
    logger, log_file = setup_logger("pipeline", config)
    
    return config, logger, log_file


def calculate_input_hash(config):
    """
    Calcula el hash del archivo de entrada para detectar cambios.
    
    Args:
        config (dict): Configuración del pipeline
        
    Returns:
        str: Hash MD5 del archivo de entrada
    """
    import os
    
    raw_dir = config.get("directories", {}).get("raw", "data/raw")
    input_file = config.get("input", {}).get("file", "sequences.tsv")
    input_path = os.path.join(raw_dir, input_file)
    
    if not os.path.exists(input_path):
        return "FILE_NOT_FOUND"
    
    return calculate_file_hash(input_path)


def check_idempotence(config, logger):
    """
    Verifica si el pipeline es idempotente (entrada y parámetros sin cambios).
    
    Args:
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        tuple: (is_idempotent, manifest)
    """
    logger.info("=" * 70)
    logger.info("VERIFICACION DE IDEMPOTENCIA")
    logger.info("=" * 70)
    
    # Calcular hashes actuales
    input_hash = calculate_input_hash(config)
    params_hash = calculate_dict_hash(config.get("thresholds", {}))
    
    logger.info(f"Hash de entrada: {input_hash[:8]}...")
    logger.info(f"Hash de parámetros: {params_hash[:8]}...")
    logger.info("")
    
    # Cargar manifest
    results_dir = config.get("directories", {}).get("results", "results")
    manifest_path = os.path.join(results_dir, "metadata.json")
    manifest = Manifest(manifest_path)
    
    # Verificar idempotencia
    is_idempotent = manifest.is_idempotent(input_hash, params_hash)
    
    if is_idempotent:
        logger.info("✓ Los datos y parámetros no han cambiado desde la última ejecución")
        logger.info("  SKIPPING: El pipeline NO se ejecutará (idempotencia)")
        last_exec = manifest.get_last_execution()
        if last_exec:
            logger.info(f"  Última ejecución: {last_exec.get('timestamp', 'N/A')}")
    else:
        logger.info("⚠ Datos o parámetros han cambiado, ejecutando pipeline completo")
        logger.info("")
        
        # Agregar nueva ejecución al manifest
        manifest.add_execution(config, input_hash, params_hash)
    
    logger.info("")
    
    return is_idempotent, manifest, input_hash, params_hash


# ============================================================================
# ORQUESTADOR PRINCIPAL
# ============================================================================

def run_full_pipeline(config_path="config.yaml", force_rerun=False):
    """
    Ejecuta el pipeline completo:
    1. Validación
    2. Procesamiento
    3. Reporte
    
    Args:
        config_path (str): Ruta al archivo de configuración
        force_rerun (bool): Forzar reejecución incluso si es idempotente
        
    Returns:
        bool: True si fue exitoso
    """
    # Setup
    config, logger, log_file = setup_pipeline(config_path)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("🎯 INICIO DEL PIPELINE")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"Configuración: {config_path}")
    logger.info(f"Log: {log_file}")
    logger.info("")
    
    # Verificar idempotencia
    is_idempotent, manifest, input_hash, params_hash = check_idempotence(config, logger)
    
    if is_idempotent and not force_rerun:
        logger.info("Pipeline skipped (idempotencia activada)")
        logger.info("")
        logger.info("=" * 70)
        logger.info("⏭️  PIPELINE COMPLETADO (SKIPPED - Sin cambios)")
        logger.info("=" * 70)
        manifest.mark_complete()
        return True
    
    try:
        # ====================================================================
        # ETAPA 1: VALIDACION
        # ====================================================================
        logger.info("")
        df_valid, success_validate, report_validation = run_validation(config_path)
        
        if not success_validate:
            logger.error("Validación fallida. Abortando pipeline.")
            manifest.mark_failed("Validación fallida")
            return False
        
        manifest.update_stage("validation", "completed", {"rows": len(df_valid)})
        
        # ====================================================================
        # ETAPA 2: PROCESAMIENTO
        # ====================================================================
        logger.info("")
        df_metrics, df_filtered, stats, success_process = run_processing(config_path)
        
        if not success_process:
            logger.error("Procesamiento fallido. Abortando pipeline.")
            manifest.mark_failed("Procesamiento fallido")
            return False
        
        manifest.update_stage("processing", "completed", stats)
        
        # ====================================================================
        # ETAPA 3: REPORTE
        # ====================================================================
        logger.info("")
        report_md, summary_json, success_report = run_reporting(
            config_path, df_metrics, df_filtered, stats
        )
        
        if not success_report:
            logger.error("Generación de reportes fallida.")
            manifest.mark_failed("Generación de reportes fallida")
            return False
        
        manifest.update_stage("reporting", "completed", {"report_generated": True})
        
        # ====================================================================
        # FINALIZACION
        # ====================================================================
        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ PIPELINE COMPLETADO EXITOSAMENTE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("📊 Resumen Final:")
        logger.info(f"  - Total de muestras: {stats.get('total', 0)}")
        logger.info(f"  - Muestras válidas: {stats.get('passed', 0)}")
        logger.info(f"  - Tasa de éxito: {stats.get('pass_rate', 0):.1f}%")
        logger.info("")
        logger.info("📁 Archivos generados:")
        logger.info(f"  - data/processed/sequences_valid.tsv")
        logger.info(f"  - data/processed/sequences_metrics.tsv")
        logger.info(f"  - data/processed/sequences_filtered.tsv")
        logger.info(f"  - results/validation_report.md")
        logger.info(f"  - results/final_report.md")
        logger.info(f"  - results/summary.json")
        logger.info(f"  - results/metadata.json")
        logger.info("")
        
        # Marcar como completado
        manifest.mark_complete()
        
        return True
    
    except Exception as e:
        logger.error(f"ERROR no capturado: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        manifest.mark_failed(f"Error: {str(e)}")
        return False


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Pipeline UD4: Análisis reproducible de secuencias"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Ruta al archivo de configuración (default: config.yaml)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar reejecución incluso si no hay cambios"
    )
    
    args = parser.parse_args()
    
    # Ejecutar pipeline
    success = run_full_pipeline(args.config, args.force)
    
    # Exit code
    sys.exit(0 if success else 1)
