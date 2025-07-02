"""
Dialogflow Pages Module
Organización modular de todas las páginas de Dialogflow CX para Dr. Clivi

Este módulo contiene las implementaciones de páginas de Dialogflow organizadas y limpias.
"""

# Importar la implementación principal que funciona
from .dialogflow_pages_clean import DialogflowPageImplementor, PageType

# Intentar importar implementaciones adicionales sin fallar
try:
    from .dialogflow_pages_original import DialogflowPageImplementor as OriginalImplementor
except ImportError:
    OriginalImplementor = None

# Exportar implementaciones disponibles
__all__ = [
    'DialogflowPageImplementor',
    'PageType'
]

if OriginalImplementor:
    __all__.append('OriginalImplementor')

# Versión por defecto (implementación limpia)
default_implementor = DialogflowPageImplementor
