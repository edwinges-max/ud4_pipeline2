# ============================================================================
# validate.py - Validación de datos de entrada
# ============================================================================

import os
import pandas as pd
from pathlib import Path
from src.utils import (
    load_config, get_full_path, validate_columns, 
    validate_sequence, setup_logger
)

# ============================================================================
# FUNCIONES DE VALIDACION
# ============================================================================

def validate_input_file(config, logger):
    """
    Valida el archivo TSV de entrada.
    
    Args:
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        tuple: (es_valido, df, mensajes_error)
    """
    logger.info("=" * 70)
    logger.info("ETAPA 1: VALIDACION DE ENTRADA")
    logger.info("=" * 70)
    
    # Obtener ruta del archivo
    raw_dir = get_full_path(config, "raw")
    input_file = config.get("input", {}).get("file", "sequences.tsv")
    input_path = os.path.join(raw_dir, input_file)
    
    logger.info(f"Archivo de entrada: {input_path}")
    
    # Verificar existencia
    if not os.path.exists(input_path):
        error_msg = f"ERROR: Archivo no encontrado: {input_path}"
        logger.error(error_msg)
        return False, None, [error_msg]
    
    logger.info(f"✓ Archivo existe")
    
    # Cargar TSV
    try:
        df = pd.read_csv(input_path, sep="\t", encoding="utf-8")
        logger.info(f"✓ Archivo cargado: {len(df)} filas")
    except Exception as e:
        error_msg = f"ERROR al leer TSV: {str(e)}"
        logger.error(error_msg)
        return False, None, [error_msg]
    
    # Validar columnas
    required_cols = config.get("input", {}).get("columns", ["sample_id", "sequence"])
    is_valid, col_msg = validate_columns(df, required_cols)
    
    if not is_valid:
        logger.error(f"ERROR: {col_msg}")
        return False, df, [col_msg]
    
    logger.info(f"✓ Columnas válidas: {required_cols}")
    
    # Validar contenido
    errors = []
    valid_rows = []
    invalid_rows = []
    
    for idx, row in df.iterrows():
        sample_id = str(row.get("sample_id", "")).strip()
        sequence = str(row.get("sequence", "")).strip()
        
        # Validaciones
        if not sample_id:
            errors.append(f"Fila {idx}: sample_id vacío")
            invalid_rows.append(idx)
            continue
        
        if not sequence:
            errors.append(f"Fila {idx}: sequence vacía")
            invalid_rows.append(idx)
            continue
        
        if not validate_sequence(sequence):
            errors.append(f"Fila {idx}: sequence contiene caracteres inválidos: {sequence}")
            invalid_rows.append(idx)
            continue
        
        valid_rows.append(idx)
    
    # Reporte
    logger.info("")
    logger.info(f"Validación de contenido:")
    logger.info(f"  - Filas válidas: {len(valid_rows)}")
    logger.info(f"  - Filas inválidas: {len(invalid_rows)}")
    
    if errors:
        logger.warning(f"Errores encontrados ({len(errors)}):")
        for error in errors[:10]:  # Mostrar primeros 10
            logger.warning(f"  - {error}")
        if len(errors) > 10:
            logger.warning(f"  ... y {len(errors) - 10} errores más")
    
    return len(invalid_rows) == 0, df, errors


def clean_dataframe(df, config, logger):
    """
    Limpia y prepara el DataFrame para procesamiento.
    
    Args:
        df (pd.DataFrame): DataFrame original
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        pd.DataFrame: DataFrame limpio
    """
    logger.info("")
    logger.info("Limpieza de datos:")
    
    df_clean = df.copy()
    
    # Aplicar configuración de procesamiento
    processing_config = config.get("processing", {})
    
    if processing_config.get("trim_whitespace", True):
        df_clean["sample_id"] = df_clean["sample_id"].str.strip()
        df_clean["sequence"] = df_clean["sequence"].str.strip()
        logger.info("  ✓ Espacios en blanco removidos")
    
    if processing_config.get("case_to_upper", True):
        df_clean["sequence"] = df_clean["sequence"].str.upper()
        logger.info("  ✓ Secuencias convertidas a mayúsculas")
    
    return df_clean


def save_validated_file(df, config, logger):
    """
    Guarda el archivo validado en data/processed.
    
    Args:
        df (pd.DataFrame): DataFrame validado
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        str: Ruta del archivo guardado
    """
    processed_dir = get_full_path(config, "processed")
    output_file = os.path.join(processed_dir, "sequences_valid.tsv")
    
    Path(processed_dir).mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_file, sep="\t", index=False, encoding="utf-8")
    
    logger.info(f"✓ Archivo validado guardado: {output_file}")
    
    return output_file


def generate_validation_report(df, errors, config, logger):
    """
    Genera un reporte de validación en Markdown.
    
    Args:
        df (pd.DataFrame): DataFrame validado
        errors (list): Lista de errores encontrados
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        str: Contenido del reporte en Markdown
    """
    report = []
    
    report.append("# Reporte de Validación\n")
    report.append(f"**Total de filas analizadas:** {len(df)}\n")
    report.append(f"**Filas válidas:** {len(df)}\n")
    report.append(f"**Filas inválidas:** {len(errors)}\n\n")
    
    report.append("## Estado\n")
    if len(errors) == 0:
        report.append("✅ **VALIDACION OK** - Todos los datos son válidos\n\n")
    else:
        report.append("❌ **VALIDACION CON ERRORES** - Se encontraron inconsistencias\n\n")
    
    if errors:
        report.append("## Errores Detectados\n\n")
        for i, error in enumerate(errors[:20], 1):
            report.append(f"{i}. {error}\n")
        
        if len(errors) > 20:
            report.append(f"\n... y {len(errors) - 20} errores más\n")
    
    report.append("\n## Resumen de Columnas\n\n")
    report.append(f"| Columna | Tipo | Valores Únicos |\n")
    report.append(f"|---------|------|----------------|\n")
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        unique = df[col].nunique()
        report.append(f"| {col} | {dtype} | {unique} |\n")
    
    return "".join(report)


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def run_validation(config_path="config.yaml"):
    """
    Ejecuta la etapa de validación completa.
    
    Args:
        config_path (str): Ruta al archivo de configuración
        
    Returns:
        tuple: (df_validado, es_exitoso, reporte_markdown)
    """
    # Cargar configuración
    config = load_config(config_path)
    
    # Setup logger
    logger, log_file = setup_logger("validate", config)
    
    # Validar entrada
    is_valid, df, errors = validate_input_file(config, logger)
    
    if df is None:
        logger.error("Validación fallida. Abortando.")
        return None, False, ""
    
    # Limpiar datos
    df_clean = clean_dataframe(df, config, logger)
    
    # Guardar archivo limpio
    output_path = save_validated_file(df_clean, config, logger)
    
    # Generar reporte
    validation_report = generate_validation_report(df_clean, errors, config, logger)
    
    # Guardar reporte
    results_dir = get_full_path(config, "results")
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    report_path = os.path.join(results_dir, "validation_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(validation_report)
    
    logger.info(f"✓ Reporte de validación guardado: {report_path}")
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ VALIDACION COMPLETADA")
    logger.info("=" * 70)
    
    return df_clean, True, validation_report
