"""Types d'erreur d'exécution et utilitaires de catégorisation."""

from __future__ import annotations

from enum import Enum

import polars.exceptions as pl_exc


class ErrorCategory(str, Enum):
    RESOURCE = "resource"  # fichier manquant, chemin invalide, permissions
    DATA = "data"  # colonne introuvable, erreur de schéma, compute error


class ExecutionError(Exception):
    """Levée quand un nœud échoue à l'exécution.

    Attributes:
        category: catégorie de l'erreur (RESOURCE ou DATA)
        node_id: id du nœud culpable ; None si l'erreur n'a pu être isolée
        node_type: type du nœud culpable ; None si l'erreur n'a pu être isolée
    """

    def __init__(
        self,
        message: str,
        *,
        category: ErrorCategory,
        node_id: str | None = None,
        node_type: str | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.node_id = node_id
        self.node_type = node_type


def _categorize(exc: BaseException) -> ErrorCategory:
    if isinstance(exc, OSError):
        return ErrorCategory.RESOURCE
    return ErrorCategory.DATA


def _translate(exc: BaseException) -> str:
    """Traduit une exception en courte description (après 'Nœud ... : ')."""
    if isinstance(exc, FileNotFoundError):
        detail = str(exc.filename) if exc.filename else str(exc)
        return f"fichier introuvable — {detail}"
    if isinstance(exc, OSError):
        return f"chemin invalide — {exc.strerror or str(exc)}"
    if isinstance(exc, pl_exc.ColumnNotFoundError):
        return f"colonne introuvable — {exc}"
    if isinstance(exc, pl_exc.SchemaError):
        return f"incompatibilité de schéma — {exc}"
    if isinstance(exc, pl_exc.ComputeError):
        return f"erreur de calcul — {exc}"
    return f"erreur d'exécution — {exc}"
