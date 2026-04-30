# ============================================================================
# manifest.py - Gestión de hashes y idempotencia
# ============================================================================

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

# ============================================================================
# FUNCIONES DE HASH
# ============================================================================

def calculate_file_hash(filepath, algorithm="md5"):
    """
    Calcula el hash de un archivo.
    
    Args:
        filepath (str): Ruta al archivo
        algorithm (str): Algoritmo (md5, sha256, etc.)
        
    Returns:
        str: Hash en hexadecimal
    """
    hash_obj = hashlib.new(algorithm)
    
    with open(filepath, "rb") as f:
        # Leer en chunks para archivos grandes
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def calculate_dict_hash(data, algorithm="md5"):
    """
    Calcula el hash de un diccionario (JSON serializado).
    
    Args:
        data (dict): Diccionario a hashear
        algorithm (str): Algoritmo (md5, sha256, etc.)
        
    Returns:
        str: Hash en hexadecimal
    """
    json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(json_str.encode("utf-8"))
    
    return hash_obj.hexdigest()


# ============================================================================
# CLASE MANIFEST
# ============================================================================

class Manifest:
    """
    Gestiona el manifest de ejecución del pipeline.
    
    El manifest almacena:
    - Hashes de entrada (para detectar cambios)
    - Hashes de parámetros (config)
    - Metadata de ejecución
    - Estado de cada etapa
    """
    
    def __init__(self, manifest_path="results/metadata.json"):
        """
        Inicializa el manifest.
        
        Args:
            manifest_path (str): Ruta al archivo manifest.json
        """
        self.manifest_path = manifest_path
        self.data = self._load()
    
    def _load(self):
        """Carga manifest existente o crea uno nuevo."""
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        return {
            "pipeline": {
                "name": "Sequence Analysis Pipeline",
                "version": "1.0"
            },
            "executions": []
        }
    
    def save(self):
        """Guarda el manifest en disco."""
        Path(self.manifest_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
    
    def add_execution(self, config, input_hash, params_hash):
        """
        Agrega una nueva ejecución al manifest.
        
        Args:
            config (dict): Configuración del pipeline
            input_hash (str): Hash del archivo de entrada
            params_hash (str): Hash de los parámetros
        """
        execution = {
            "timestamp": datetime.now().isoformat(),
            "input_hash": input_hash,
            "params_hash": params_hash,
            "status": "running",
            "stages": {}
        }
        
        self.data["executions"].append(execution)
        self.save()
    
    def get_last_execution(self):
        """Retorna la última ejecución."""
        if self.data["executions"]:
            return self.data["executions"][-1]
        return None
    
    def is_idempotent(self, input_hash, params_hash):
        """
        Verifica si la entrada y parámetros no han cambiado.
        
        Args:
            input_hash (str): Hash actual de entrada
            params_hash (str): Hash actual de parámetros
            
        Returns:
            bool: True si no ha cambiado nada
        """
        last_exec = self.get_last_execution()
        
        if not last_exec:
            return False
        
        # Si los hashes coinciden, es idempotente
        return (last_exec["input_hash"] == input_hash and 
                last_exec["params_hash"] == params_hash)
    
    def update_stage(self, stage_name, status, details=None):
        """
        Actualiza el estado de una etapa.
        
        Args:
            stage_name (str): Nombre de la etapa
            status (str): Estado (running, completed, failed)
            details (dict, optional): Detalles adicionales
        """
        last_exec = self.get_last_execution()
        
        if not last_exec:
            return
        
        last_exec["stages"][stage_name] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self.save()
    
    def mark_complete(self):
        """Marca la ejecución como completada."""
        last_exec = self.get_last_execution()
        
        if last_exec:
            last_exec["status"] = "completed"
            last_exec["completed_at"] = datetime.now().isoformat()
            self.save()
    
    def mark_failed(self, error_msg):
        """Marca la ejecución como fallida."""
        last_exec = self.get_last_execution()
        
        if last_exec:
            last_exec["status"] = "failed"
            last_exec["failed_at"] = datetime.now().isoformat()
            last_exec["error"] = error_msg
            self.save()
    
    def __str__(self):
        """Representación en string del manifest."""
        return json.dumps(self.data, indent=2)
