# ============================================================================
# utils.py - Utilidades comunes del pipeline
# ============================================================================

import os
import yaml
import logging
from pathlib import Path
from datetime import datetime

# ============================================================================
# FUNCIONES DE CONFIGURACION
# ============================================================================

def load_config(config_path="config.yaml"):
    """
    Carga el archivo YAML de configuración.
    
    Args:
        config_path (str): Ruta al archivo config.yaml
        
    Returns:
        dict: Configuración parseada
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        yaml.YAMLError: Si el YAML es inválido
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Archivo de config no encontrado: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config


def ensure_directories(config):
    """
    Crea los directorios especificados en config si no existen.
    
    Args:
        config (dict): Configuración del pipeline
    """
    dirs = config.get("directories", {})
    
    for key, path in dirs.items():
        Path(path).mkdir(parents=True, exist_ok=True)
        # print(f"  ✓ Directorio '{key}': {path}")


# ============================================================================
# FUNCIONES DE LOGGING
# ============================================================================

def setup_logger(name, config):
    """
    Configura el logger para el pipeline.
    
    Args:
        name (str): Nombre del logger
        config (dict): Configuración del pipeline
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Crear directorio de logs si no existe
    log_dir = config.get("directories", {}).get("logs", "logs")
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Timestamp para el nombre del archivo
    timestamp = datetime.now().strftime(config.get("logging", {}).get("timestamp_format", "%Y%m%d_%H%M%S"))
    log_file = os.path.join(log_dir, f"pipeline_{timestamp}.log")
    
    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        config.get("logging", {}).get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Agregar handlers
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger, log_file


# ============================================================================
# FUNCIONES DE RUTA (PORTABLES)
# ============================================================================

def get_full_path(config, key, filename=None):
    """
    Obtiene la ruta completa portable usando rutas relativas.
    
    Args:
        config (dict): Configuración del pipeline
        key (str): Clave en config["directories"] (ej: "processed")
        filename (str, optional): Nombre de archivo a agregar
        
    Returns:
        str: Ruta completa portable
    """
    base_path = config.get("directories", {}).get(key, "")
    
    if filename:
        return os.path.join(base_path, filename)
    
    return base_path


# ============================================================================
# FUNCIONES DE VALIDACION
# ============================================================================

def validate_columns(df, required_columns):
    """
    Valida que un DataFrame tenga las columnas requeridas.
    
    Args:
        df (pd.DataFrame): DataFrame a validar
        required_columns (list): Columnas requeridas
        
    Returns:
        tuple: (es_valido, mensaje_error)
    """
    missing_cols = set(required_columns) - set(df.columns)
    
    if missing_cols:
        return False, f"Columnas faltantes: {missing_cols}"
    
    return True, "OK"


def validate_sequence(seq):
    """
    Valida que una secuencia sea válida (solo A, T, G, C, N).
    
    Args:
        seq (str): Secuencia a validar
        
    Returns:
        bool: True si es válida
    """
    valid_chars = set("ATGCN")
    return all(c in valid_chars for c in seq.upper())


# ============================================================================
# FUNCIONES DE ESTADISTICAS
# ============================================================================

def calculate_gc(sequence):
    """
    Calcula la fracción GC de una secuencia.
    
    Fracción GC = (G + C) / longitud_total
    
    Args:
        sequence (str): Secuencia ADN
        
    Returns:
        float: Fracción GC (0.0 a 1.0)
    """
    sequence = sequence.upper()
    
    if len(sequence) == 0:
        return 0.0
    
    gc_count = sequence.count('G') + sequence.count('C')
    return gc_count / len(sequence)


def calculate_length(sequence):
    """
    Calcula la longitud de una secuencia.
    
    Args:
        sequence (str): Secuencia ADN
        
    Returns:
        int: Longitud
    """
    return len(sequence.strip())


# ============================================================================
# FUNCIONES DE TIMESTAMP
# ============================================================================

def get_timestamp():
    """Retorna timestamp ISO format."""
    return datetime.now().isoformat()


def get_timestamp_for_filename():
    """Retorna timestamp para nombres de archivo (YYYYMMDD_HHMMSS)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
