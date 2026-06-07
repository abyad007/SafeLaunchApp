# Versigent Safe Launch — Design System

> Phase Design — v1.0. Built with the **UI/UX Pro Max** skill.
> Product class: **Data-Dense / BI-Analytics Dashboard** (enterprise).
> Source of truth: [`design/tokens.json`](./tokens.json) → consumed at runtime by [`core/theme.py`](../core/theme.py).

---

## 1. Principes

1. **Charte Versigent conservée** : navy `#16283F` + copper `#CD7925`, polices Barlow.
2. **Accessibilité d'abord (WCAG AA)** : tout texte ≥ 4.5:1. Le copper de marque sert aux **bordures / aplats / badges** ; en **texte** sur fond clair on utilise le copper foncé `#9A5A14`.
3. **Densité maîtrisée** : padding compact (8–16 px), typographie lisible — adapté à un dashboard data.
4. **Tokens en 3 couches** : primitive → semantic → component. On ne code plus de hex en dur dans les écrans : on consomme des variables.

## 2. Couleurs

### Marque
| Token | Hex | Usage |
|---|---|---|
| `navy.900` | `#16283F` | Texte principal, header |
| `navy.800` | `#1F3553` | Dégradé header |
| `copper.500` | `#CD7925` | Bordures, aplats, liseré de carte, badges |
| `copper.700` | `#9A5A14` | **Copper en texte** (labels de section) — AA 5.4:1 |
| `gold.400` | `#F7A900` | Accent **sur fond foncé uniquement** (tag header) |

### Neutres
| Token | Hex | Usage |
|---|---|---|
| `stone.50/100` | `#FAFAF7` / `#F4F1EA` | Surfaces secondaires (sidebar, todo) |
| `stone.200` | `#E5DFD3` | Bordures chaudes |
| `gray.600` | `#64748B` | Texte secondaire / muted (AA 4.8:1) |
| `gray.400` | `#9CA3AF` | **Décoratif seulement** — interdit en texte |

### Statut / Risque (paires fill + text)
| Niveau | Fill / Badge | Texte (AA) | Fond teinté |
|---|---|---|---|
| HIGH | `#DC2626` | `#B91C1C` | `#FFF0EE` |
| MEDIUM | `#D97706` | `#B45309` | `#FFF7ED` |
| LOW / Done | `#16A34A` | `#15803D` | `#F0FFF4` |

> **Correctifs WCAG appliqués** vs. l'ancienne UI : `.section-label` copper 3.30:1 → 5.4:1 ; `.metric-sub` gris 2.5:1 → 4.8:1 ; textes risque/done passés aux variantes `-700`.

## 3. Typographie

| Rôle | Police | Taille | Poids |
|---|---|---|---|
| Display (H1, valeurs métriques) | **Barlow Condensed** | 28 px | 700 |
| Titres de section | Barlow Condensed | 18 px | 700 |
| Corps | **Barlow** | 14 px | 400 |
| Petit / caption | Barlow | 12 px | 400–600 |
| Label (uppercase) | Barlow | 10–11 px | 600, letter-spacing 2 px |

Échelle : `xs 11 · sm 12 · base 14 · md 16 · lg 18 · xl 22 · 2xl 28`. Interligne corps 1.5, display 1.1. Taille de corps minimale : **12 px**.

## 4. Espacement, rayon, ombre
- **Espacement** (base 4 px) : 4 · 8 · 12 · 16 · 20 · 24 · 32
- **Rayon** : sm 3 · base 6 · lg 8
- **Ombre carte** : `0 1px 3px rgba(22,40,63,0.06)`

## 5. Composants (classes CSS via `core/theme.py`)
`.main-header` · `.header-tag` · `.risk-badge` · `.metric-card` / `.metric-label` / `.metric-value` / `.metric-sub` · `.chk-done` / `.chk-warn` / `.chk-todo` · `.section-label` · `.file-ok` / `.file-miss`.

## 5b. États interactifs (`_interactions_css` dans `core/theme.py`)
Appliqués **uniquement aux éléments réellement cliquables** (pas aux cartes/lignes d'info statiques).

| État | Règle |
|---|---|
| **Focus** (clavier) | Anneau copper `2px` + `outline-offset` sur boutons, liens, inputs, selects, tabs, expanders, `[tabindex]`. Jamais supprimé (priorité WCAG **High**). `:focus-within` pour les inputs/selects baseweb. |
| **Hover** | Boutons : bordure + texte copper foncé + ombre ; bouton *primary* : remplissage copper. Tabs/expander/liens : texte copper foncé. Curseur `pointer`. |
| **Active** | Boutons : `translateY(1px)` (enfoncement). |
| **Disabled** | `opacity .5` + `cursor: not-allowed`, sans ombre. |
| **Motion** | Transitions `100–150 ms` encapsulées dans `@media (prefers-reduced-motion: no-preference)`. |

## 5c. Mode sombre (`theme.dark` dans `tokens.json` → `_dark_css` dans `core/theme.py`)
Conserve l'ADN Versigent (navy + copper). Activé par le toggle **🌙 Dark mode** de la sidebar (`key="dark_mode"`), lu en haut du script : `inject_theme(st, dark=...)`. Le dark **réassigne les variables `--vg-*`** (donc tous les composants token-driven basculent) puis override le chrome Streamlit (sidebar, inputs, selects, boutons, alertes, expanders, dataframes).

| Token | Light | Dark | Contraste dark |
|---|---|---|---|
| background | `#FFFFFF` | `#0E1B2E` | — |
| surface (carte) | `#FFFFFF` | `#16283F` | — |
| surface-alt | `#F4F1EA` | `#1B3050` | — |
| foreground | `#16283F` | `#EAF0F7` | 15:1 |
| muted | `#64748B` | `#9FB0C3` | 7.8:1 |
| accent (copper) | `#CD7925` | `#CD7925` | 5.2:1 |
| accent-text | `#9A5A14` | `#E89B4D` | 7.6:1 |
| risk HIGH/MED/LOW (texte) | `B91C1C/B45309/15803D` | `F87171/FBBF24/4ADE80` | ≥6:1 |

> Les bandeaux à dégradé navy (header, « Plan Review ») restent foncés dans les deux modes (texte blanc) — c'est intentionnel.

## 5d. Responsive / mobile (`_responsive_css` dans `core/theme.py`)
Streamlit n'est pas responsive par défaut (colonnes comprimées, `font-size` fixes, panneaux `flex` qui débordent). Layer ajouté :

- **Anti-débordement** : `overflow-x: hidden` sur le conteneur ; `-webkit-text-size-adjust`.
- **Breakpoint `≤ 640px`** : empilement de **toutes** les colonnes (`stHorizontalBlock`/`stColumn` → 100 %), header replié sur 2 lignes, gouttières réduites.
- **Type fluide** : score `clamp(40px,12vw,56px)`, titre vide `clamp(26px,7vw,36px)`, `.metric-value`/`.risk-badge` réduits.
- **Tactile** : boutons `min-height: 44px` + pleine largeur, onglets plus hauts (guideline UX « 44×44 »).
- **Tables** : `overflow-x: auto` plutôt que casser la mise en page.

## 5e. Dashboard guidé 4 étapes + graphiques (refonte UX)
L'app est un **parcours guidé** piloté par `st.session_state["step"]` (1→4), avec un **stepper**
en haut (`_stepper_css` / `render_stepper`) : ① Configurer · ② Tableau de bord · ③ Revue · ④ Export.
- **Étape 1** (`render_configure` + `_program_form`) : formulaire pleine page (sorti de la sidebar),
  groupé en `st.container(border=True)`, + import procédure (`render_procedure_preview`).
- **Étape 2** (`render_dashboard`) : jauge de risque, KPIs, barres de facteurs, donut + barres par
  phase, timeline Safe Launch, gates client.
- **Étape 3** (`render_review`) : table d'affectation (owner/échéance) + filtres + donut/barres live.
- **Étape 4** (`render_export`) : récap + aperçu PPT/Excel + téléchargements.

**Graphiques** : `core/charts.py` (Plotly, transparent, police Barlow, couleurs via
`core.theme.color(name, dark)`) — `risk_gauge`, `factor_bar`, `completion_donut`, `phase_bars`,
`timeline`. Rendus avec `st.plotly_chart(fig, theme=None, config={"displayModeBar": False})`.
La logique métier (`scoring_engine`, `checklist_loader`, `report_generator`, …) est **inchangée**.

## 5f. Allègement « app iOS » + désaturation orange
Suite à un retour utilisateur (« je vois de l'orange »), les **résidus orange** de la v1 ont été retirés
et l'app rapprochée d'un rendu iOS :
- **Masqué** : barre arc-en-ciel par défaut de Streamlit (`stDecoration`), toolbar.
- **Retiré** : liseré copper sous le header, bandeau « PRO », liseré copper en haut des `metric-card`,
  soulignement copper des `section-label`, ■ orange + pastille dorée des en-têtes de phase.
- **Cartes iOS** : `border-radius:16px`, bordure 1px discrète, ombre douce ; header à coins arrondis.
- **Contrôles hors sidebar** : barre supérieure (toggle sombre + « Nouveau »), `initial_sidebar_state="collapsed"`.
- **Graphiques désaturés** : barres de facteurs et de phases en **encre navy** (plus copper) ; le copper
  reste l'accent unique (stepper actif, boutons primaires). Jauge/donut gardent les couleurs de statut.
- **Mobile** : tagline header masquée < 640px, `automargin` Plotly pour éviter les libellés coupés.
Vérifié par captures **iPhone 13 (390 px)** via Playwright/Chromium (étapes 1 & 2).

## 5g. Barre d'onglets iOS (bas d'écran)
Navigation type application iOS via une **barre d'onglets fixe en bas** : Config · Tableau · Revue · Export.
- Construite avec de **vrais boutons Streamlit** (rerun websocket → la session/le plan sont **préservés**).
  ⚠️ Ne pas utiliser de liens `?step=` : un changement d'URL recharge la page et **réinitialise** `session_state`.
- La barre = le `stHorizontalBlock` qui contient le sentinelle `.vg-tabmark`, épinglé en bas via CSS `:has()`
  (`_tabbar_css` dans `core/theme.py`). Onglet actif surligné via `:nth-child({step})` injecté par étape.
- Onglets 2-4 **désactivés** tant qu'aucun plan n'est généré. Icônes emoji + label (2 lignes, `white-space:pre-line`).
- `render_tabbar(step, has_result)` dans `app.py`, appelée en fin de dispatch.

## 6. Comment l'utiliser dans le code

Dans `app.py`, remplacer le bloc CSS inline + le dict `RISK_COLORS` par :

```python
from core.theme import inject_theme, RISK_COLORS, RISK_TEXT, RISK_BG, NAVY, COPPER

st.set_page_config(...)
inject_theme(st)          # injecte :root + classes (remplace le <style> inline)
```

Tout le reste du markup HTML reste identique (mêmes noms de classes). Les graphiques Plotly utilisent `RISK_COLORS` (aplats) et `NAVY` / `COPPER` pour les accents.

## 7b. Exports PPT / Excel (`core/report_generator.py`)
Les exports dérivent désormais leurs couleurs et polices des **mêmes tokens** que l'app (plus de palette dupliquée).

- **Pont tokens** : `_trgb(path)` → `RGBColor` (python-pptx), `_thex(path)` → `'RRGGBB'` (openpyxl). Les constantes `NAVY/COPPER/GOLD/GREEN/RED/RISK_COLORS/GRAY/LIGHT_GRAY/DARK_GRAY` sont calculées depuis `tokens.json`.
- **Couleurs de risque** alignées : `C0281E→B91C1C`, `B85C00→B45309`, `217346→15803D` (variantes `-text`, lisibles en texte sur blanc **et** sous texte blanc en aplat). Gris `9CA3AF→64748B` (lisibilité).
- **Police** : `Calibri → Barlow` (`BODY_FONT`) partout, y compris la police par défaut du classeur Excel ; `DISPLAY_FONT="Barlow Condensed"` disponible pour les titres.
- **Vérifié** : génération des 7 types de programme → PPT + XLSX valides (signature `PK`), couleurs token présentes, anciennes couleurs absentes, zéro Calibri.

## 7. Reste à faire (passes suivantes)
- [x] Câbler `inject_theme()` dans `app.py` (fait)
- [x] Harmoniser les visualisations de données (HTML/CSS — pas de Plotly dans le projet)
- [x] Exports PPT/Excel alignés sur les tokens (couleurs + police Barlow) — voir §7b
- [x] États interactifs hover/focus/active/disabled — voir §5b
- [x] Mode sombre Versigent + toggle sidebar — voir §5c
- [x] Nettoyage des warnings lint (imports/f-strings/variables inutilisés) — pyflakes clean
- [x] Responsive / mobile (breakpoint ≤640px, type fluide, tactile 44px) — voir §5d
