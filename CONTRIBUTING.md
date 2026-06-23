# Contribuer

## Branches
- `main` : stable. Travailler sur des branches `feat/...`, `fix/...`, `docs/...`.

## Convention de commits
Format conseillé : `type(scope): sujet` — ex. `feat(ir): valider la cardinalité des ports`.
Types : `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.

## Faire évoluer l'IR
Toute modification du format commence par `packages/ir-schema/schema/ir.schema.json`,
puis se répercute sur `packages/backend/app/ir/models.py` et `packages/frontend/src/ir/types.ts`.
Mettre à jour l'exemple de référence et les tests.

## Avant de pousser
- Backend : `ruff check . && pytest -q`
- Frontend : `npm run lint`
