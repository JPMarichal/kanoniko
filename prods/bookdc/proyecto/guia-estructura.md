# Guía de Estructura y Nomenclatura

Este documento establece las reglas permanentes para mantener la estructura escalable y la ubicación correcta de archivos en futuras sesiones de trabajo del proyecto DyC.

## 📁 Estructura Principal (Máximo 3 niveles)

```
prods/bookdc/
├── README.md                    # ÚNICO archivo permitido en raíz
├── contenido/                   # Material final y público
│   ├── biografias/            # Biografías .md (NUNCA subdividir)
│   ├── pericopas/             # Esquemas textuales DyC
│   ├── graficos/
│   │   ├── esquemas/          # PNG: esquema_dyc_XXX.png
│   │   └── personajes/        # PNG: personajes_dyc_XXX.png
│   └── datos/                # JSON: sumario_dyc_XXX.json
├── referencias/                # Documentación de consulta
│   ├── fuentes.md
│   ├── matriz_de_fuentes.md
│   ├── bibliografia.md
│   └── personajes/
│       ├── namelist.md
│       ├── namelist_per_section.md
│       └── namelist_with_passages.md
├── proyecto/                  # Gestión y control
│   ├── normativas_biografias.md
│   ├── auditoria_fuentes_bios.md
│   ├── LOTE-PROGRESO.md
│   └── LOTE-PROGRESO-SEGUNDA-PASADA.md
├── datos/                     # Datos brutos y procesamiento
│   ├── batch1_context.txt
│   ├── batch2_context.txt
│   └── lote1_real.txt
└── herramientas/               # Scripts y utilidades
    ├── get_context.py
    └── get_context2.py
```

## 🏷️ Reglas de Nomenclatura (OBLIGATORIO)

### Biografías
- **Formato**: `Nombre Apellido.md`
- **Ejemplos**: `Joseph Smith Jr.md`, `Emma Smith.md`
- **Ubicación**: `contenido/biografias/`
- **REGLA**: NUNCA subdividir por categorías

### Perícopas Textuales
- **Formato**: `Esquema de DyC XXX.md`
- **Ejemplos**: `Esquema de DyC 001.md`, `Esquema de DyC 138.md`
- **Ubicación**: `contenido/pericopas/`
- **REGLA**: Mantener formato original exacto

### Gráficos - Esquemas
- **Formato**: `esquema_dyc_XXX.png`
- **Ejemplos**: `esquema_dyc_001.png`, `esquema_dyc_138.png`
- **Ubicación**: `contenido/graficos/esquemas/`
- **REGLA**: Números de 3 dígitos (001, 002, etc.)

### Gráficos - Personajes
- **Formato**: `personajes_dyc_XXX.png` o `personajes_od_XXX.png`
- **Ejemplos**: `personajes_dyc_001.png`, `personajes_od_001.png`
- **Ubicación**: `contenido/graficos/personajes/`
- **REGLA**: Mantener prefijo dyC u OD según corresponda

### Datos Estructurados
- **Formato**: `sumario_dyc_XXX.json` o `sumario_dyc_doX.json`
- **Ejemplos**: `sumario_dyc_001.json`, `sumario_dyc_do1.json`
- **Ubicación**: `contenido/datos/`
- **REGLA**: Solo archivos JSON con datos estructurados

## 📋 Checklist de Ubicación (USAR SIEMPRE)

Antes de crear o mover cualquier archivo, verificar:

### ✅ Para Biografías
- [ ] Es archivo .md?
- [ ] Sigue formato "Nombre Apellido.md"?
- [ ] Se ubica en `contenido/biografias/`?
- [ ] NO se está creando subdirectorio dentro de biografias?

### ✅ Para Perícopas
- [ ] Es archivo .md?
- [ ] Sigue formato "Esquema de DyC XXX.md"?
- [ ] Se ubica en `contenido/pericopas/`?
- [ ] Número de sección tiene 3 dígitos?

### ✅ Para Gráficos
- [ ] Es archivo PNG?
- [ ] Sigue formato `esquema_dyc_XXX.png` o `personajes_dyc_XXX.png`?
- [ ] Se ubica en `contenido/graficos/esquemas/` o `contenido/graficos/personajes/`?
- [ ] Número tiene 3 dígitos?

### ✅ Para Datos JSON
- [ ] Es archivo JSON?
- [ ] Sigue formato `sumario_dyc_XXX.json`?
- [ ] Se ubica en `contenido/datos/`?
- [ ] NO se está colocando en gráficos?

### ✅ Para Documentación
- [ ] Es archivo .md de referencia?
- [ ] Se ubica en `referencias/` o subdirectorio apropiado?
- [ ] NO se está colocando en contenido/?

### ✅ Para Gestión
- [ ] Es archivo de seguimiento o auditoría?
- [ ] Se ubica en `proyecto/`?
- [ ] Sigue nomenclatura existente?

### ✅ Para Datos Brutos
- [ ] Es archivo de texto crudo?
- [ ] Se ubica en `datos/`?
- [ ] NO es archivo procesado final?

### ✅ Para Herramientas
- [ ] Es script o utilidad?
- [ ] Se ubica en `herramientas/`?
- [ ] NO es contenido final?

## 🚫 Errores Comunes a Evitar

1. **SUBDIVIDIR BIOGRAFÍAS**: NUNCA crear subdirectorios en `contenido/biografias/`
2. **CONFUNDIR JSON CON GRÁFICOS**: Los JSON van a `contenido/datos/`, no a `contenido/graficos/`
3. **CREAR ARCHIVOS EN RAÍZ**: Solo `README.md` debe estar en la raíz
4. **IGNORAR FORMATO EXISTENTE**: Mantener siempre las nomenclaturas originales
5. **EXCEDER 3 NIVELES**: La estructura máxima es `categoria/subcategoria/archivo`

## 🔄 Proceso para Nuevos Archivos

1. **Identificar tipo** (biografía, perícopa, gráfico, dato, referencia, etc.)
2. **Aplicar nomenclatura** según reglas correspondientes
3. **Verificar ubicación** con checklist apropiado
4. **Confirmar nivel máximo** (no más de 3 niveles)
5. **Actualizar README.md** si se agregan categorías nuevas

## 📞 Referencia Rápida

| Tipo de Archivo | Formato | Ubicación | Niveles |
|---|---|---|---|
| Biografía | `Nombre Apellido.md` | `contenido/biografias/` | 2 |
| Perícopa | `Esquema de DyC XXX.md` | `contenido/pericopas/` | 2 |
| Esquema gráfico | `esquema_dyc_XXX.png` | `contenido/graficos/esquemas/` | 3 |
| Personaje gráfico | `personajes_dyc_XXX.png` | `contenido/graficos/personajes/` | 3 |
| Datos JSON | `sumario_dyc_XXX.json` | `contenido/datos/` | 2 |
| Referencia | `*.md` | `referencias/` | 2-3 |
| Gestión | `*.md` | `proyecto/` | 2 |
| Datos brutos | `*.txt` | `datos/` | 2 |
| Herramientas | `*.py` | `herramientas/` | 2 |

---

**Última actualización**: 6 de mayo de 2026  
**Versión**: 1.0 (Estructura estable)  
**Aplicación**: Obligatoria para todas las sesiones futuras
