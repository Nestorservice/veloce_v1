GO_PROMPT = """\
Tu es un expert Go et Clean Architecture.
Traduis les fichiers PHP/Laravel suivants en Go selon ces regles :
- Architecture hexagonale : domain/, usecase/, infra/, handler/
- Utilise net/http standard (pas de framework externe sauf si necessaire)
- Requetes SQL via database/sql avec requetes preparees (pas d'injection)
- Gestion des erreurs explicite, pas de panic()
- Chaque fichier PHP = un fichier .go dans le package approprie

Reponds UNIQUEMENT avec le code Go complet, sans explication.
Commence par le nom du package et les imports.

### FICHIERS PHP :
{php_content}

### CODE GO :
"""

DART_PROMPT = """\
Tu es un expert Flutter/Dart avec Riverpod.
Traduis les vues Blade Laravel suivantes en Widgets Flutter selon ces regles :
- StatelessWidget ou ConsumerWidget (Riverpod)
- Architecture feature-first : lib/features/<nom>/presentation/
- Chaque vue Blade = un Widget Flutter dans son propre fichier
- Appels API via Repository + Provider Riverpod
- Pas de setState direct

Reponds UNIQUEMENT avec le code Dart complet, sans explication.

### VUES BLADE :
{blade_content}

### CODE DART :
"""
