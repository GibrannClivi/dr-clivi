# Dialogflow Pages - Organización Modular

Esta carpeta contiene todas las implementaciones de páginas de Dialogflow CX organizadas de manera modular.

## 📁 Estructura de Archivos

### Implementaciones Principales
- **`dialogflow_pages_clean.py`** - Implementación limpia y funcional ✅
- **`dialogflow_pages_original.py`** - Implementación original migrada
- **`dialogflow_pages_optimized.py`** - Versión optimizada (requiere dependencias)
- **`dialogflow_pages.py`** - Implementación modular avanzada

### Componentes Modulares
- **`page_types.py`** - Definiciones de tipos de página
- **`page_renderer.py`** - Lógica de renderizado de páginas
- **`page_router.py`** - Lógica de ruteo entre páginas
- **`main_menu_pages.py`** - Páginas del menú principal
- **`appointment_pages.py`** - Páginas de gestión de citas
- **`measurement_pages.py`** - Páginas de registro de mediciones
- **`admin_pages.py`** - Páginas administrativas

## 🚀 Uso

### Importación Principal
```python
from dr_clivi.flows.dialogflow_pages import DialogflowPageImplementor, PageType
```

### Importación desde la Carpeta
```python
from dr_clivi.flows.dialogflow_pages.dialogflow_pages_clean import DialogflowPageImplementor
```

## ✅ Estado Actual

- ✅ **Funcionando**: `dialogflow_pages_clean.py` - Implementación estable
- ⚠️ **Requiere dependencias**: `dialogflow_pages_optimized.py` 
- 📄 **Documentación**: `dialogflow_pages_original.py`
- 🚧 **En desarrollo**: `dialogflow_pages.py`

## 🔄 Compatibilidad

La reorganización mantiene total compatibilidad con el código existente:

- `deterministic_handler.py` ✅ Funciona sin cambios
- `telegram_handler.py` ✅ Importaciones compatibles  
- Tests existentes ✅ Sin impacto

## 📋 TODO

- [ ] Completar implementación optimizada
- [ ] Unificar todas las versiones en una sola
- [ ] Agregar tests específicos para cada implementación
- [ ] Documentar diferencias entre versiones
