# QA Pipeline - Pipeline de Control de Calidad para DVH Radiotherapy Analysis

## 📋 Descripción

Pipeline completo de **auditoría técnica** y **control de calidad** para el proyecto **DVH Radiotherapy Analysis Pipeline**.

Verifica automáticamente:

- ✅ Estructura y organización del proyecto
- ✅ Dependencias y compatibilidades
- ✅ Calidad de código (PEP8, imports, etc)
- ✅ Reproducibilidad y configuración
- ✅ Documentación completitud
- ✅ Módulos DVH críticos
- ✅ Arquitectura y modularidad
- ✅ Validación de archivos DICOM
- ✅ Integridad de cálculos DVH

---

## 🚀 Uso rápido

### Opción 1: Ejecutar pipeline completo

```bash
# Desde el directorio raíz del proyecto TFM_2
python run_qa_complete.py /ruta/a/TFM_2
```

### Opción 2: Ejecutar módulos individuales

```powershell
# En PowerShell - QA Pipeline principal
py quality_assurance/qa_pipeline.py /ruta/a/TFM_2

# Validar archivos DICOM
py quality_assurance/dicom_validator.py data/raw

# Validar cálculos DVH
py quality_assurance/dvh_validator.py
```

---

## 📁 Estructura

```
quality_assurance/
│
├── run_qa_complete.py      # Script maestro (orquestador)
├── qa_pipeline.py          # QA principal (estructura, dependencias, código)
├── dicom_validator.py      # Validación DICOM
├── dvh_validator.py        # Validación DVH y métricas
├── README.md               # Este archivo
└── requirements_qa.txt     # Dependencias (si las hay)
```

---

## 🔍 Módulos de QA

### 1. **qa_pipeline.py** - Auditoría General

Verifica:
- Directorios requeridos (src/, data/, scripts/, results/, logs/)
- Archivos críticos (requirements.txt, README.md, src/__init__.py)
- Compatibilidad de versiones de dependencias
- Calidad de código (PEP8, imports, line length)
- Reproducibilidad (setup.py, config.py, .gitignore)
- Documentación (README, docstrings)
- Módulos DVH (dicom_loader, dvh_pipeline, plotting, qa)
- Arquitectura modular

**Genera**: `qa_reports/qa_report_YYYYMMDD_HHMMSS.json`

### 2. **dicom_validator.py** - Validación DICOM

Verifica:
- Presencia de archivos .dcm
- Magic number DICOM (byte 128 = "DICM")
- Detección de modalidades (CT, RTSTRUCT, RTDOSE, RTPLAN)
- Tamaño y integridad de archivos
- Completitud de dataset para DVH

**Genera**: Reporte de validación en consola

### 3. **dvh_validator.py** - Validación DVH

Verifica:
- Positividad: volumen > 0, dosis > 0
- Monotonicidad: Dmax ≥ Dmean ≥ Dmin
- Consistencia: D100 ≤ D95 ≤ D98
- Relaciones lógicas D2cc vs Dmax
- Rango clínico realista (0-150 Gy)
- Advertencias clínicas específicas (PTV, OAR)

**Genera**: `qa_reports/dvh_validation.txt`

---

## 📊 Ejemplo de Salida

```
========================================================================
🔍 PIPELINE DE CONTROL DE CALIDAD - DVH RADIOTHERAPY ANALYSIS
========================================================================

📁 Verificando estructura de directorios...
  ✅ src/ - Código fuente principal
  ✅ data/ - Directorio de datos
  ✅ scripts/ - Scripts de ejecución
  ...

📦 Verificando dependencias...
  ✅ requirements.txt encontrado
  📌 Total de dependencias: 4
    - pandas
    - matplotlib
    - pydicom==1.4.2
    - dicompyler-core

...

========================================================================
📊 REPORTE DE CONTROL DE CALIDAD
========================================================================

📈 RESUMEN:
  ✅ Aprobados:  12
  ⚠️  Advertencias: 2
  ❌ Fallos:      0
  ℹ️  Informativos: 1

========================================================================
🎯 RECOMENDACIONES DE MEJORA
========================================================================

🟡 MEDIO (Mejorar):
  • Code Analysis: Problemas de calidad de código detectados
  • Setup & Config: Configuración de reproducibilidad incompleta

✅ PRÓXIMOS PASOS:
  1. Revisar reporte JSON generado
  2. Corregir problemas críticos
  3. Implementar mejoras recomendadas
  4. Re-ejecutar pipeline de QA
  5. Preparar para CI/CD en GitHub

📄 Reporte JSON guardado: qa_reports/qa_report_20260520_154322.json
```

---

## 🔧 Estados de Chequeos

| Estado | Símbolo | Significado |
|--------|---------|------------|
| PASSED | ✅ | Chequeo exitoso |
| WARNING | ⚠️ | Advertencia (revisar) |
| FAILED | ❌ | Error crítico |
| INFO | ℹ️ | Información |

---

## 🎯 Severidades

| Severidad | Acción |
|-----------|--------|
| 🔴 critical | **Resolver inmediatamente** - Bloquea proyecto |
| 🟠 high | **Resolver pronto** - Afecta funcionalidad |
| 🟡 medium | **Mejorar** - Afecta mantenibilidad |
| ℹ️ low | **Considerar** - Recomendaciones |

---

## 📝 Reporte JSON

El archivo `qa_report_YYYYMMDD_HHMMSS.json` contiene:

```json
{
  "timestamp": "2026-05-20T15:43:22.123456",
  "summary": {
    "total_checks": 15,
    "passed": 12,
    "warnings": 2,
    "failed": 0
  },
  "results": [
    {
      "category": "Project Structure",
      "check_name": "Required Directories",
      "status": "PASSED",
      "message": "Todos los directorios requeridos existen",
      "severity": "info",
      "details": []
    },
    ...
  ]
}
```

---

## 🔄 Integración CI/CD

Para automatizar el QA en GitHub Actions:

```yaml
# .github/workflows/qa.yml
name: QA Pipeline

on: [push, pull_request]

jobs:
  qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: python quality_assurance/run_qa_complete.py .
```

---

## ⚙️ Personalización

### Modificar tolerancias DVH

En `dvh_validator.py`:

```python
TOLERANCE_DOSE_Gy = 0.5      # Cambiar tolerancia en Gy
TOLERANCE_VOLUME = 0.1       # Cambiar tolerancia en volumen
```

### Agregar nuevos chequeos

En `qa_pipeline.py`, agregar método:

```python
def _check_custom(self) -> None:
    """Tu nuevo chequeo"""
    self.results.append(CheckResult(
        category="Custom Category",
        check_name="Your Check",
        status=CheckStatus.PASSED,
        message="Descripción",
        severity="info"
    ))
```

---

## 🐛 Troubleshooting

### Error: "Script no encontrado"

**Solución**: Asegurar que estás ejecutando desde el directorio correcto:

```powershell
# Correcto
python quality_assurance/run_qa_complete.py /ruta/a/TFM_2

# O desde TFM_2
cd C:\ruta\a\TFM_2
python ..\quality_assurance\run_qa_complete.py .
```

### Error: "requirements.txt no encontrado"

**Solución**: Crear un `requirements.txt` en la raíz de TFM_2:

```
pandas>=1.0
matplotlib>=3.0
pydicom==1.4.2
dicompyler-core
numpy
```

### Reporte vacío

**Solución**: Verificar que la ruta al proyecto es correcta y contiene estructura esperada.

---

## 📚 Referencias Rápidas

- **Normalización código**: PEP 8 (120 chars línea máx)
- **DICOM**: Medical imaging standard ISO 12052
- **DVH**: Dose-Volume Histogram (radiotherapy)
- **QA**: Quality Assurance / Control

---

## 🎓 Próximos Pasos Post-QA

1. ✅ Ejecutar pipeline QA
2. ✅ Revisar reportes generados
3. ✅ Corregir problemas críticos
4. ✅ Implementar mejoras recomendadas
5. ✅ Re-ejecutar para validar correcciones
6. ✅ Subir a GitHub (público o privado)
7. ✅ Configurar CI/CD automático
8. ✅ Documentar en README.md
9. ✅ Versionar releases

---

## 📞 Soporte

Para preguntas o problemas:

1. Revisar archivo `qa_report_*.json`
2. Consultar sección "Troubleshooting" arriba
3. Verificar documentación de módulos individuales

---

**Última actualización**: 2026-05-20
**Versión**: 1.0
