# ============================================================================
# Makefile - DAG del Pipeline UD4
# ============================================================================
# 
# Uso:
#   make all              Ejecutar todo el pipeline
#   make validate         Ejecutar solo validación
#   make process          Ejecutar procesamiento
#   make report           Ejecutar reporte
#   make clean            Limpiar archivos generados
#   make help             Ver esta ayuda
#
# DAG (Directed Acyclic Graph):
#   raw → validate → sequences_valid → process → filter → report
#

.PHONY: all validate process report clean help install

# Variables
PYTHON := python
CONFIG := config.yaml
FORCE :=

# Directorios
DATA_RAW := data/raw
DATA_PROCESSED := data/processed
RESULTS := results
LOGS := logs

# Archivos clave
INPUT_FILE := \/sequences.tsv
VALID_FILE := \/sequences_valid.tsv
METRICS_FILE := \/sequences_metrics.tsv
FILTERED_FILE := \/sequences_filtered.tsv
REPORT_FILE := \/final_report.md
MANIFEST_FILE := \/metadata.json

# ============================================================================
# TARGETS
# ============================================================================

help:
	@echo "Pipeline UD4 - Análisis de Secuencias"
	@echo ""
	@echo "Targets disponibles:"
	@echo "  make all       - Ejecutar todo el pipeline"
	@echo "  make validate  - Validar entrada"
	@echo "  make process   - Procesar (métricas + filtrado)"
	@echo "  make report    - Generar reportes"
	@echo "  make clean     - Limpiar archivos generados"
	@echo "  make install   - Instalar dependencias"
	@echo ""

install:
	@echo "📦 Instalando dependencias..."
	\ -m pip install -r requirements.txt
	@echo "✅ Dependencias instaladas"

# Target principal: ejecutar todo
all: validate process report
	@echo ""
	@echo "=========================================="
	@echo "✅ PIPELINE COMPLETADO"
	@echo "=========================================="

# ETAPA 1: Validación
validate: \ \

\: \ config.yaml
	@echo ""
	@echo "=========================================="
	@echo "ETAPA 1: VALIDACION"
	@echo "=========================================="
	\ -m src.validate
	@echo "✅ Validación completada"

# ETAPA 2: Procesamiento (depende de validación)
process: \ \

\ \: \ config.yaml
	@echo ""
	@echo "=========================================="
	@echo "ETAPA 2: PROCESAMIENTO"
	@echo "=========================================="
	\ -m src.process
	@echo "✅ Procesamiento completado"

# ETAPA 3: Reporte (depende de procesamiento)
report: \

\: \ \ config.yaml
	@echo ""
	@echo "=========================================="
	@echo "ETAPA 3: REPORTE"
	@echo "=========================================="
	\ -m src.report
	@echo "✅ Reporte generado"

# Limpiar
clean:
	@echo "🧹 Limpiando archivos generados..."
	@rm -rf \/*
	@rm -rf \/*
	@rm -rf \/*
	@echo "✅ Limpieza completada"

# Mostrar DAG
dag:
	@echo ""
	@echo "DAG del Pipeline:"
	@echo ""
	@echo "  INPUT (raw)"
	@echo "     ↓"
	@echo "  VALIDATE → sequences_valid.tsv"
	@echo "     ↓"
	@echo "  PROCESS → sequences_metrics.tsv"
	@echo "     ↓     → sequences_filtered.tsv"
	@echo "     ↓"
	@echo "  REPORT → final_report.md"
	@echo "     ↓"
	@echo "  OUTPUT (results)"
	@echo ""

.PHONY: dag
