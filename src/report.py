# ============================================================================
# report.py - Generación de reportes finales (Markdown + HTML)
# ============================================================================

import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.utils import (
    load_config, get_full_path, setup_logger, get_timestamp
)

# ============================================================================
# FUNCIONES DE REPORTE
# ============================================================================

def generate_markdown_report(df_metrics, df_filtered, stats, config, logger):
    """
    Genera un reporte en Markdown con resumen y métricas.
    
    Args:
        df_metrics (pd.DataFrame): DataFrame con todas las métricas
        df_filtered (pd.DataFrame): DataFrame filtrado (pasó filtros)
        stats (dict): Estadísticas del filtrado
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        str: Contenido del reporte en Markdown
    """
    logger.info("=" * 70)
    logger.info("ETAPA 4: GENERACION DE REPORTES")
    logger.info("=" * 70)
    logger.info("")
    
    report = []
    
    # Encabezado
    report.append("# Reporte Final del Pipeline\n\n")
    report.append(f"**Fecha de ejecución:** {get_timestamp()}\n")
    report.append(f"**Nombre del pipeline:** {config.get('pipeline', {}).get('name', 'N/A')}\n")
    report.append(f"**Versión:** {config.get('pipeline', {}).get('version', 'N/A')}\n\n")
    
    # Resumen ejecutivo
    report.append("## 📊 Resumen Ejecutivo\n\n")
    report.append(f"| Métrica | Valor |\n")
    report.append(f"|---------|-------|\n")
    report.append(f"| Total de muestras | {stats.get('total', 0)} |\n")
    report.append(f"| Muestras válidas | {stats.get('passed', 0)} |\n")
    report.append(f"| Muestras filtradas | {stats.get('rejected', 0)} |\n")
    report.append(f"| Tasa de éxito | {stats.get('pass_rate', 0):.1f}% |\n\n")
    
    # Estadísticas de entrada
    report.append("## 📈 Estadísticas de Entrada\n\n")
    
    if "length" in df_metrics.columns:
        report.append("### Longitud de Secuencias\n\n")
        report.append(f"| Métrica | Valor |\n")
        report.append(f"|---------|-------|\n")
        report.append(f"| Mínimo | {df_metrics['length'].min()} bp |\n")
        report.append(f"| Máximo | {df_metrics['length'].max()} bp |\n")
        report.append(f"| Media | {df_metrics['length'].mean():.2f} bp |\n")
        report.append(f"| Mediana | {df_metrics['length'].median():.2f} bp |\n")
        report.append(f"| Desv. Est. | {df_metrics['length'].std():.2f} bp |\n\n")
    
    if "gc_fraction" in df_metrics.columns:
        report.append("### Fracción GC\n\n")
        report.append(f"| Métrica | Valor |\n")
        report.append(f"|---------|-------|\n")
        report.append(f"| M��nimo | {df_metrics['gc_fraction'].min():.4f} |\n")
        report.append(f"| Máximo | {df_metrics['gc_fraction'].max():.4f} |\n")
        report.append(f"| Media | {df_metrics['gc_fraction'].mean():.4f} |\n")
        report.append(f"| Mediana | {df_metrics['gc_fraction'].median():.4f} |\n")
        report.append(f"| Desv. Est. | {df_metrics['gc_fraction'].std():.4f} |\n\n")
    
    # Umbrales aplicados
    report.append("## ⚙️ Umbrales Configurados\n\n")
    thresholds = config.get("thresholds", {})
    report.append(f"| Parámetro | Valor |\n")
    report.append(f"|-----------|-------|\n")
    report.append(f"| Longitud mínima | {thresholds.get('min_length', 'N/A')} bp |\n")
    report.append(f"| Longitud máxima | {thresholds.get('max_length', 'N/A')} bp |\n")
    report.append(f"| Fracción GC mínima | {thresholds.get('gc_min', 'N/A')} |\n")
    report.append(f"| Fracción GC máxima | {thresholds.get('gc_max', 'N/A')} |\n\n")
    
    # Tabla de muestras filtradas
    if len(df_filtered) > 0:
        report.append("## ✅ Muestras que Pasan el Filtro\n\n")
        report.append(f"Total: {len(df_filtered)} muestras\n\n")
        
        # Mostrar primeras 10
        report.append("| sample_id | length | gc_fraction |\n")
        report.append("|-----------|--------|-------------|\n")
        
        for idx, row in df_filtered.head(10).iterrows():
            sample_id = row.get("sample_id", "N/A")
            length = row.get("length", "N/A")
            gc = row.get("gc_fraction", "N/A")
            
            if isinstance(gc, float):
                gc = f"{gc:.4f}"
            
            report.append(f"| {sample_id} | {length} | {gc} |\n")
        
        if len(df_filtered) > 10:
            report.append(f"\n*... y {len(df_filtered) - 10} muestras más*\n\n")
        else:
            report.append("\n")
    
    # Tabla de muestras rechazadas
    df_rejected = df_metrics[~df_metrics.index.isin(df_filtered.index)]
    
    if len(df_rejected) > 0:
        report.append("## ❌ Muestras Rechazadas\n\n")
        report.append(f"Total: {len(df_rejected)} muestras\n\n")
        
        report.append("| sample_id | length | gc_fraction | razón |\n")
        report.append("|-----------|--------|-------------|-------|\n")
        
        for idx, row in df_rejected.head(10).iterrows():
            sample_id = row.get("sample_id", "N/A")
            length = row.get("length", "N/A")
            gc = row.get("gc_fraction", "N/A")
            
            if isinstance(gc, float):
                gc = f"{gc:.4f}"
            
            # Determinar razón del rechazo
            razones = []
            if length < thresholds.get("min_length", 0) or length > thresholds.get("max_length", 999999):
                razones.append("longitud")
            if gc < thresholds.get("gc_min", 0) or gc > thresholds.get("gc_max", 1):
                razones.append("GC")
            
            razon = ", ".join(razones) if razones else "desconocida"
            
            report.append(f"| {sample_id} | {length} | {gc} | {razon} |\n")
        
        if len(df_rejected) > 10:
            report.append(f"\n*... y {len(df_rejected) - 10} muestras más*\n\n")
        else:
            report.append("\n")
    
    # Pie de página
    report.append("---\n\n")
    report.append("*Reporte generado automáticamente por el Pipeline UD4*\n")
    
    return "".join(report)


def save_report(report_content, filename, config, logger):
    """
    Guarda el reporte en archivo.
    
    Args:
        report_content (str): Contenido del reporte
        filename (str): Nombre del archivo (sin extensión)
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        str: Ruta del archivo guardado
    """
    results_dir = get_full_path(config, "results")
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    
    output_file = os.path.join(results_dir, f"{filename}.md")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    logger.info(f"✓ Reporte guardado: {output_file}")
    
    return output_file


def generate_summary_json(stats, config, logger):
    """
    Genera un resumen en JSON para consumo de máquina.
    
    Args:
        stats (dict): Estadísticas del pipeline
        config (dict): Configuración del pipeline
        logger: Logger configurado
        
    Returns:
        dict: Resumen en formato JSON
    """
    import json
    
    summary = {
        "timestamp": get_timestamp(),
        "pipeline": config.get("pipeline", {}),
        "statistics": stats,
        "thresholds": config.get("thresholds", {}),
        "status": "completed"
    }
    
    results_dir = get_full_path(config, "results")
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    
    summary_file = os.path.join(results_dir, "summary.json")
    
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"✓ Resumen JSON guardado: {summary_file}")
    
    return summary


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def run_reporting(config_path="config.yaml", df_metrics=None, df_filtered=None, stats=None):
    """
    Ejecuta la etapa de generación de reportes.
    
    Args:
        config_path (str): Ruta al archivo de configuración
        df_metrics (pd.DataFrame, optional): DataFrame con métricas
        df_filtered (pd.DataFrame, optional): DataFrame filtrado
        stats (dict, optional): Estadísticas del pipeline
        
    Returns:
        tuple: (reporte_markdown, resumen_json, es_exitoso)
    """
    # Cargar configuración
    config = load_config(config_path)
    
    # Setup logger
    logger, log_file = setup_logger("report", config)
    
    # Si no se proporcionan datos, cargarlos de archivos
    if df_metrics is None or df_filtered is None:
        logger.warning("Cargando datos desde archivos guardados...")
        
        try:
            metrics_file = os.path.join(get_full_path(config, "processed"), "sequences_metrics.tsv")
            df_metrics = pd.read_csv(metrics_file, sep="\t", encoding="utf-8")
            
            filtered_file = os.path.join(get_full_path(config, "processed"), "sequences_filtered.tsv")
            df_filtered = pd.read_csv(filtered_file, sep="\t", encoding="utf-8")
            
            logger.info(f"✓ Datos cargados: {len(df_metrics)} métricas, {len(df_filtered)} filtradas")
        except Exception as e:
            logger.error(f"ERROR al cargar datos: {str(e)}")
            return "", {}, False
    
    # Generar reporte Markdown
    report_md = generate_markdown_report(df_metrics, df_filtered, stats or {}, config, logger)
    
    # Guardar reporte
    report_file = save_report(report_md, "final_report", config, logger)
    
    # Generar resumen JSON
    summary = generate_summary_json(stats or {}, config, logger)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ GENERACION DE REPORTES COMPLETADA")
    logger.info("=" * 70)
    
    return report_md, summary, True
