"""Registre des nœuds + implémentations (sources / transforms / sinks).

Importer ce package enregistre tous les nœuds disponibles dans le registre.
"""

from app.nodes import sources, transforms, sinks  # noqa: F401  (effet de bord : enregistrement)
