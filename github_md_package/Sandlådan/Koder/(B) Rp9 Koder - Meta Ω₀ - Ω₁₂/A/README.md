# RP9 Finnish Package

Detta paket innehåller körbara Python-skript, datafiler och rapportmallar för att testa och analysera RP9-modellen med fokus på 1.5-skalning och relaterade strukturer.

## Innehåll
- **Python-skript**: körbara Colab/lokala skript för att generera resultat, figurer och rapporter.
- **Utdatafiler**: `.csv`, `.json`, `.log` samt `.html`-figurer.
- **Rapportmallar**: Markdown-strukturer för att analysera resultat i Obsidian.

## Användning
1. Kör Python-skriptet i Google Colab eller lokalt (Python 3.10+).
2. Resultat sparas automatiskt i en utdata-mapp (`/content/RP9_Colab_Out/`).
3. Packa utdata till `.zip` för enkel nedladdning.
4. Använd `.csv` som tabellunderlag, `.html` för interaktiva figurer, och Markdown för rapportskrivning.

## Viktigt
- Alla beräkningar utgår från **halva-halva (1.5)** som exakt konstant (ej approximation).
- φ ≈ 1.618 används endast som jämförelse i rapporter, aldrig som primär operator.
- Kod och rapporter är avsedda för forsknings- och teständamål.  
  Resultat kan återskapas, modifieras och jämföras av andra, men rättigheterna till koden och metodologin tillhör författaren.

