# ============================================================================
# process.py - Procesamiento de secuencias (GC, longitud, filtrado)
# ============================================================================

import os
import pandas as pd
from pathlib import Path
from src.utils import (
    load_config, get_full_path, calculate_gc, 
    calculate_length, setup_logger
)

# ============================================================================
# FUNCIONES DE PROCESAMIENTO
# ============================================================================

def calculate_metrics(df, config, logger):
    """
    Calcula métricas para cada secuencia (GC, longitud).
    
    Args:
        df (pd.DataFrame): DataFrame con secuencias validadas
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        pd.DataFrame: DataFrame con métricas añadidas
    """
    logger.info("=" * 70)
    logger.info("ETAPA 2: CALCULO DE METRICAS")
    logger.info("=" * 70)
    
    df_metrics = df.copy()
    
    # Calcular longitud
    if config.get("processing", {}).get("calculate_length", True):
        logger.info("Calculando longitud de secuencias...")
        df_metrics["length"] = df_metrics["sequence"].apply(calculate_length)
        logger.info(f"  ✓ Longitud: min={df_metrics['length'].min()}, "
                   f"max={df_metrics['length'].max()}, "
                   f"media={df_metrics['length'].mean():.2f}")
    
    # Calcular fracción GC
    if config.get("processing", {}).get("calculate_gc", True):
        logger.info("Calculando fracción GC...")
        df_metrics["gc_fraction"] = df_metrics["sequence"].apply(calculate_gc)
        logger.info(f"  ✓ GC: min={df_metrics['gc_fraction'].min():.4f}, "
                   f"max={df_metrics['gc_fraction'].max():.4f}, "
                   f"media={df_metrics['gc_fraction'].mean():.4f}")
    
    logger.info("")
    return df_metrics


def save_metrics_file(df_metrics, config, logger):
    """
    Guarda la tabla de métricas en data/processed.
    
    Args:
        df_metrics (pd.DataFrame): DataFrame con métricas
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        str: Ruta del archivo guardado
    """
    processed_dir = get_full_path(config, "processed")
    output_file = os.path.join(processed_dir, "sequences_metrics.tsv")
    
    Path(processed_dir).mkdir(parents=True, exist_ok=True)
    
    df_metrics.to_csv(output_file, sep="\t", index=False, encoding="utf-8")
    
    logger.info(f"✓ Tabla de métricas guardada: {output_file}")
    
    return output_file


def filter_sequences(df_metrics, config, logger):
    """
    Filtra secuencias según umbrales parametrizables.
    
    Args:
        df_metrics (pd.DataFrame): DataFrame con métricas
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        tuple: (df_filtered, df_rejected, estadisticas)
    """
    logger.info("=" * 70)
    logger.info("ETAPA 3: FILTRADO SEGUN UMBRALES")
    logger.info("=" * 70)
    
    thresholds = config.get("thresholds", {})
    
    min_length = thresholds.get("min_length", 10)
    max_length = thresholds.get("max_length", 1000)
    gc_min = thresholds.get("gc_min", 0.0)
    gc_max = thresholds.get("gc_max", 1.0)
    
    logger.info(f"Umbrales configurados:")
    logger.info(f"  - Longitud: {min_length} - {max_length} bp")
    logger.info(f"  - Fracción GC: {gc_min} - {gc_max}")
    logger.info("")
    
    # Crear máscara de filtrado
    mask_length = (df_metrics["length"] >= min_length) & (df_metrics["length"] <= max_length)
    mask_gc = (df_metrics["gc_fraction"] >= gc_min) & (df_metrics["gc_fraction"] <= gc_max)
    
    mask_combined = mask_length & mask_gc
    
    # Separar
    df_filtered = df_metrics[mask_combined].reset_index(drop=True)
    df_rejected = df_metrics[~mask_combined].reset_index(drop=True)
    
    # Estadísticas
    stats = {
        "total": len(df_metrics),
        "passed": len(df_filtered),
        "rejected": len(df_rejected),
        "pass_rate": (len(df_filtered) / len(df_metrics) * 100) if len(df_metrics) > 0 else 0
    }
    
    logger.info(f"Resultados del filtrado:")
    logger.info(f"  - Total: {stats['total']}")
    logger.info(f"  - Pasan filtro: {stats['passed']} ({stats['pass_rate']:.1f}%)")
    logger.info(f"  - Rechazan filtro: {stats['rejected']}")
    logger.info("")
    
    if len(df_rejected) > 0:
        logger.info(f"Razones de rechazo:")
        
        # Contar razones
        length_fail = ((~mask_length) & mask_gc).sum()
        gc_fail = ((~mask_gc) & mask_length).sum()
        both_fail = (~mask_length & ~mask_gc).sum()
        
        if length_fail > 0:
            logger.info(f"  - Longitud fuera de rango: {length_fail}")
        if gc_fail > 0:
            logger.info(f"  - Fracción GC fuera de rango: {gc_fail}")
        if both_fail > 0:
            logger.info(f"  - Ambas métricas fuera de rango: {both_fail}")
        logger.info("")
    
    return df_filtered, df_rejected, stats


def save_filtered_file(df_filtered, config, logger):
    """
    Guarda las secuencias filtradas.
    
    Args:
        df_filtered (pd.DataFrame): DataFrame filtrado
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        str: Ruta del archivo guardado
    """
    processed_dir = get_full_path(config, "processed")
    output_file = os.path.join(processed_dir, "sequences_filtered.tsv")
    
    Path(processed_dir).mkdir(parents=True, exist_ok=True)
    
    df_filtered.to_csv(output_file, sep="\t", index=False, encoding="utf-8")
    
    logger.info(f"✓ Secuencias filtradas guardadas: {output_file}")
    
    return output_file


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def run_processing(config_path="config.yaml", input_file=None):
    """
    Ejecuta la etapa de procesamiento completa.
    
    Args:
        config_path (str): Ruta al archivo de configuración
        input_file (str, optional): Ruta del archivo de entrada (si no, usa sequences_valid.tsv)
        
    Returns:
        tuple: (df_metrics, df_filtered, estadisticas, es_exitoso)
    """
    # Cargar configuración
    config = load_config(config_path)
    
    # Setup logger
    logger, log_file = setup_logger("process", config)
    
    # Cargar archivo validado
    if input_file is None:
        input_file = os.path.join(get_full_path(config, "processed"), "sequences_valid.tsv")
    
    logger.info(f"Cargando archivo de entrada: {input_file}")
    
    try:
        df = pd.read_csv(input_file, sep="\t", encoding="utf-8")
        logger.info(f"✓ Archivo cargado: {len(df)} filas")
    except Exception as e:
        logger.error(f"ERROR al leer archivo: {str(e)}")
        return None, None, {}, False
    
    logger.info("")
    
    # Calcular métricas
    df_metrics = calculate_metrics(df, config, logger)
    
    # Guardar métricas
    metrics_file = save_metrics_file(df_metrics, config, logger)
    
    # Filtrar
    df_filtered, df_rejected, stats = filter_sequences(df_metrics, config, logger)
    
    # Guardar filtradas
    filtered_file = save_filtered_file(df_filtered, config, logger)
    
    logger.info("=" * 70)
    logger.info("✅ PROCESAMIENTO COMPLETADO")
    logger.info("=" * 70)
    
    return df_metrics, df_filtered, stats, True
