Le mode d'audit en lecture seule m'interdit de créer un fichier : le compte rendu sera donné dans la conversation. Je commence par inventorier les énoncés et le référentiel.   

Searched for files matching `**/data/latex/enonces/**/*.tex`, 168 matches

Searched for files matching `**/data/latex/catalogues/*`, 2 matches

Searched for files matching `**/data/latex/codes_labels/*.{tex,txt}`, 5 matches

Searched for files matching `**/data/latex/codes_labels/*`, 5 matches

Read 

Searched for files matching `**/texmaths-BO_2026*`, 1 match

Searched for files matching `**/code_index*.json`, no matches

Searched for files matching `**/data/latex/activites/**/*.tex`, 5 matches

Read , lines 1 to 400

Read , lines 400 to 900

Read , lines 900 to 1300

Read , lines 1300 to 1691

Searched for regex `.` (`**/data/latex/enonces/definitions/**`), 201 results

Searched for regex `.` (`**/data/latex/enonces/{theoremes,proprietes}/**`), 116 results

Read 

Searched for regex `.` (`**/data/latex/enonces/{methodes,regles}/**`), 108 results

Searched for regex `milieu|médiane d'un|parallélogramme|translation|vecteur|Chasles|volume|pyramide|cône|cylindre|prisme|boule|sphère|probabilit|ratio|coefficient|quartile|inéquation|inégalité|absolue|inverse|rationnel|cercle circonscrit|droite des milieux|trapèze|cosinus|corde|distance|abscisse|échelle|vitesse|arrondi|encadr|tableur|algorithm|contraposée|contre-exemple|pair|impair|booléen|boucle|variable` (`**/data/latex/enonces/**`), 33 results

Searched for regex `chiffre|dixième|centième|rang|ordre de grandeur|durée|heure|masse|convers|unité|segment|demi-droite|droite \\|ensemble|entier|décimal|hasard|issue|moyenne|diagramme|tableau|graphique|ordonnée|origine|agrandi|réduction|aire|hauteur|angle` (`**/data/latex/enonces/**`), 119 results

Je n'ai pas créé de fichier `.md`. Le mode d'audit m'interdit toute écriture dans le dépôt, donc le compte rendu est ci-dessous. Vous pouvez le copier dans un fichier, ou me relancer dans un mode qui autorise l'écriture si vous voulez que je le crée.

## 0. Périmètre et sources

- **Analysé :** les 168 `.tex` de `enonces`, lus en entier. Ils se répartissent en 92 définitions, 4 théorèmes, 40 propriétés, 20 méthodes et 12 règles.
- **Préambules :** aucun fichier ne contient de `\startdatakeys`. Le niveau est donc déduit du contenu (interprétation) et reste incertain pour certains fichiers.
- **Référentiel :** `texmaths-BO_2026.sty`, lu en entier.
  - Il contient les `\newobj`, `\newpro` et `\newaut` des cycles 3 et 4. Son en-tête cite « le BO n° 16 du 17 avril 2025 ».
  - Je n'ai pas compté les objectifs.
  - `code_index.json` est absent. Je ne cite donc pas de codes `C4…` : je cite les intitulés exacts.
- **Limites du référentiel :**
  - C'est un index d'objectifs transcrit pour le projet, pas le texte intégral des programmes.
  - Il ne liste pas tous les savoirs et savoir-faire. Les définitions, propriétés ou méthodes que je propose au-delà d'un objectif sont marquées **(b)**, interprétation.
  - Les propositions **(a)** s'appuient sur un objectif explicite.
- **Hors périmètre :** `activites/`, `flash/` et `exercices/` ne sont pas audités. Je ne dis donc rien sur la présence d'activités. Les automatismes (`aut`) ne sont pas traités comme attendus du cours. Les prolongements (`pro`) sont signalés à part.
- **Exhaustivité :** l'audit des énoncés est complet sur les 168 fichiers. L'appariement avec les objectifs est fait au niveau des sous-thèmes. Il n'est pas exhaustif objectif par objectif pour les procédures.

## A. Bilan général

Diagnostic par sous-thème. « Existants » désigne les fichiers de `enonces/` que j'ai jugés pertinents (interprétation).

| Niveau | Sous-thème | Diagnostic | Existants / manques principaux |
|---|---|---|---|
| 6e | Entiers et décimaux | PARTIELLEMENT COUVERT | `nombre_decimal`, `zeros_inutiles`, `pourcentage`, `multiplier_par_01_001`, `multiplication_decimaux`. Manquent : valeur des chiffres, comparer, ranger, arrondir, repérer, ordres de grandeur. |
| 6e | Fractions | PARTIELLEMENT COUVERT | `fraction`, `egalite_de_fractions`, `quotient_dividende_diviseur`. Manquent : comparer, encadrer, fraction d'une quantité, addition à dénominateurs différents. |
| 6e | Grandeurs et mesures | PARTIELLEMENT COUVERT | Longueurs, aires et volumes : définitions de base seulement. Manquent : conversions, périmètre du carré et du rectangle, durées. |
| 6e | Géométrie plane | PARTIELLEMENT COUVERT | Médiatrice, bissectrice et symétrie axiale sont présentes. Manquent : milieu, distance, corde, disque, angles particuliers, cercle circonscrit, propriétés des triangles. |
| 6e | Proportionnalité | PARTIELLEMENT COUVERT | `proportionnelles`, `proportionnalite` (tableau seul). Manquent : linéarité, retour à l'unité, échelle. |
| 6e | Probabilités | ABSENT | Aucun énoncé. |
| 5e | Relatifs | PARTIELLEMENT COUVERT | Opposé, comparaison et addition sont traités. Manquent : valeur absolue, suppression des parenthèses, addition de plusieurs relatifs. |
| 5e | Fractions | PARTIELLEMENT COUVERT | `addition_fractions_meme_denominateur`. Manquent : comparaison, dénominateurs quelconques, soustraction. |
| 5e | Puissances | PARTIELLEMENT COUVERT | `carre_d_un_nombre` seulement. Manquent : cube, carrés parfaits. |
| 5e | Calcul littéral | PARTIELLEMENT COUVERT | Évaluer, tester, équation de base. Manquent : contre-exemple, factorisation, nature d'une expression. |
| 5e | Espace | ABSENT | Aucun solide, patron, perspective ni volume (hors `litre` et `metre_cube`). |
| 5e | Parallélogrammes | ABSENT | Rien. |
| 5e | Triangles | PARTIELLEMENT COUVERT | Somme des angles, hauteur. Manquent : médiane, aire d'un triangle quelconque, concours des hauteurs. |
| 5e | Statistiques | PARTIELLEMENT COUVERT | Effectifs, fréquences et moyenne sont présents. Manquent : méthodes de représentation. |
| 5e | Probabilités | ABSENT | Rien. |
| 5e | Fonctions | PARTIELLEMENT COUVERT | Aucun énoncé sur « en fonction de » ni sur le tableau de valeurs. |
| 4e | Relatifs (×, ÷) | ABSENT | Aucune règle des signes. |
| 4e | Rationnels | PARTIELLEMENT COUVERT | `calcul_fractionnaire` est **tronqué** (voir ci-dessous). Manquent : inverse, division, simplification. |
| 4e | Puissances | PARTIELLEMENT COUVERT | Définition seulement. Manquent : produits de puissances. |
| 4e | Racine carrée | PARTIELLEMENT COUVERT | Définition seulement. Manque : encadrement. |
| 4e | Calcul littéral | PARTIELLEMENT COUVERT | Équations du premier degré absentes. |
| 4e | Translations | ABSENT | Rien. |
| 4e | Triangles | PARTIELLEMENT COUVERT | Pythagore et sa réciproque sont présents. Manquent : contraposée, droite des milieux, cercle circonscrit du triangle rectangle. |
| 4e | Solides | ABSENT | Pyramide et cône : rien. |
| 4e | Statistiques | PARTIELLEMENT COUVERT | Médiane : définition seulement, sans méthode de calcul. |
| 4e | Probabilités | ABSENT | Rien. |
| 4e | Proportionnalité | ABSENT | Ratio, 4e proportionnelle, coefficient multiplicateur : rien. |
| 3e | Puissances | PARTIELLEMENT COUVERT | Exposant négatif et notation scientifique : définitions seulement. |
| 3e | Racine carrée | PARTIELLEMENT COUVERT | `equation_carre_constant` : cas $a<0$ et $a=0$ non traités. |
| 3e | Calcul littéral | PARTIELLEMENT COUVERT | Il manque $(a+b)^2$, $(a-b)^2$, la factorisation et les inéquations. |
| 3e | Triangles | PARTIELLEMENT COUVERT | Thalès est incomplet. Trigonométrie : définition et formules présentes. |
| 3e | Vecteurs | ABSENT | Rien. |
| 3e | Boule et sphère | ABSENT | Rien. |
| 3e | Statistiques et probabilités | ABSENT | Quartiles, boîte à moustaches, $P(A\cup B)$ : rien. |
| 3e | Fonctions | PARTIELLEMENT COUVERT | Définitions de base. Manquent : coefficients, fonction carré. |

**Points faibles transversaux :**
- Les énoncés sont surtout concentrés sur 6e et 5e. Cela reste à confirmer par l'audit des niveaux.
- Probabilités, espace, vecteurs et translations, et proportionnalité de 4e sont absents.
- Aucun énoncé de la pensée informatique.

**Points forts :**
- Vocabulaire des statistiques.
- Calcul numérique de base (relatifs, priorités).
- Définitions géométriques élémentaires.

### Anomalies dans les énoncés existants (faits observés)

- `calcul_fractionnaire.tex` : la ligne `\dfrac ab\div\dfrac cd` n'a pas de second membre. L'énoncé est **incomplet**.
- `notation_scientifique.tex` : l'énoncé écrit `1<a\leq10`. Interprétation : la convention usuelle est $1\le a<10$. À vérifier.
- `symetrie_centrale.tex` : « A est le milieu de [AA'] » alors qu'il s'agit de B et B'. L'énoncé est incohérent.
- `construction_point_symetrie_centrale.tex` : le titre parle du centre O, mais le texte utilise « cercle de centre A », « place le point A » et [AB]. Les notations sont incohérentes.
- `criteres_de_divisibilite.tex` : « nombres dont la somme est multiple de 3 ». Il manque « des chiffres ».
- `thales.tex` : l'énoncé est formulé en « triangles semblables ». Il ne donne pas l'égalité de rapports $\frac{AM}{AB}=\frac{AN}{AC}=\frac{MN}{BC}$. Il ne distingue ni les deux configurations ni la contraposée.
- `reciproque_thales.tex` : une seule égalité de rapports, sans la condition d'alignement ni d'ordre des points.
- `decompostion_facteurs_premiers.tex` : « Si un nombre est entier naturel » (0 et 1 posent problème). Interprétation : l'unicité n'est pas mentionnée.
- `division_euclidienne.tex` : manque la condition « reste < diviseur ».
- `aire_triangle_rectangle.tex` : seul le triangle rectangle est traité. L'objectif 5e « Calculer l'aire d'un triangle » demande le cas général.
- `pythagore.tex` : coquille (« autre côtés », « hypotenuse »). Autres coquilles : `carre.tex` (« carre »), `compas.tex` (« longeurs »).
- Doublons possibles : `diviseur`/`diviseur_2`, `multiple`/`multiple_2`, `fraction_irreductible`/`_2`, `nombres_opposes`/`_2`, `perimetre_cercle`/`perimetre_d_un_cercle`, `a_times_x_equal_b` (propriété et méthode). Ce sont peut-être des versions par niveau. À vérifier.
- Énoncés sans attendu identifiable dans le référentiel : `homothetie`, `triangles_semblables` (définition et propriété), les trois cas d'égalité des triangles, `triangles_egaux`, `inegalite_triangulaire`. Diagnostic **À VÉRIFIER** : je n'ai pas le texte des programmes pour trancher.

## B. Énoncés manquants à ajouter

Légende :
- Types : Déf, Prop, Thm, Règle, Méth.
- Priorités : **I** = indispensable, **S** = souhaitable, **F** = facultatif.
- **(a)** = objectif explicite du référentiel ; **(b)** = interprétation.

### Transversal (tous niveaux)

- Règle **I (b)** : notations $(AB)$, $[AB]$, $[AB)$, $AB$, $\widehat{ABC}$ (seule la notation d'angle existe).
- Règle **I (a)** : codage des figures (angle droit, égalité de longueurs et d'angles). Source : 6e « Connaître le lexique et le codage… » (automatisme, donc (b)).
- Déf **S (b)** : segment, droite, demi-droite.
- Règle **S (b)** : notations $\perp$ et $\parallel$.
- Méth **I (b)** : rédiger une démonstration (hypothèses, propriété, conclusion).
- Déf **I (a)** : contraposée, avec l'exemple de Pythagore.
- Déf **I (a)** : contre-exemple.
- Déf **S (b)** : conjecture.
- Méth **F (a)** : utiliser un tableur.

### 6e – Nombres

- Déf **I (a)** : valeur d'un chiffre selon son rang ; unités de numération jusqu'au millième.
- Déf **I (b)** : partie entière, partie décimale.
- Déf **S (a)** : fraction décimale (nombre décimal existe mais sans définition préalable).
- Prop **I (a)** : écritures d'un décimal (virgule, fraction, nombre mixte, pourcentage).
- Méth **I (a)** : comparer deux décimaux.
- Méth **I (a)** : ranger une liste de décimaux.
- Méth **I (a)** : encadrer et intercaler.
- Règle **S (a)** : symboles $=,<,>$.
- Méth **I (a)** : arrondir à l'unité, au dixième, au centième.
- Méth **I (a)** : placer et repérer un décimal sur une demi-droite graduée.
- Méth **I (a)** : contrôler un résultat par ordre de grandeur.
- Règle **I (a)** : multiplier et diviser par 10, 100, 1 000 (seul 0,1 et 0,01 existent).
- Méth **I (a)** : division euclidienne d'un entier par un entier inférieur à 100 (posée).
- Prop **S (a)** : multiplier par 0,001 ; lien avec la division par 1 000.
- Méth **I (a)** : diviser un décimal par un entier (compléter la méthode actuelle).
- Méth **S (a)** : multiplication posée d'un décimal.
- Méth **I (a)** : fraction d'une quantité.
- Méth **I (a)** : comparer et encadrer des fractions.
- Prop **I (a)** : fraction peut être entier, décimal ou non décimal.
- Méth **I (a)** : égalités de fractions, simplification.
- Méth **I (a)** : ordonner des fractions et nombres mixtes.
- Prop **I (a)** : addition et soustraction de fractions de même dénominateur (la soustraction manque).
- Prop **I (a)** : addition et soustraction de fractions à dénominateurs différents (6e).
- Déf **S (a)** : nombre mixte.
- Prop **S (a)** : écrire une fraction comme somme d'un entier et d'une fraction inférieure à 1.
- Déf **S (a)** : proportion exprimée en pourcentage.
- Méth **I (a)** : calculer une proportion, appliquer un pourcentage.
- Méth **F (a)** : modèles pré-algébriques (schéma en barres).

### 6e – Grandeurs et mesures

- Prop **I (a)** : relations entre les unités de longueur et préfixes kilo à milli.
- Méth **I (a)** : conversions de longueurs.
- Prop **I (a)** : périmètre du carré et du rectangle.
- Méth **S (a)** : périmètre de figures composées.
- Prop **S (a)** : périmètre du disque avec le rayon ($2\pi r$).
- Prop **I (a)** : aire du carré (`aire_rectangle` existe seule).
- Prop **I (a)** : relations entre unités d'aire ($1\,m^2=100\,dm^2$).
- Méth **I (a)** : conversions d'aires.
- Méth **S (a)** : comparer des aires par découpage et recollement.
- Méth **S (a)** : aire de figures composées.
- Déf **I (a)** : cm$^3$ ; Prop **S (b)** : lien L, dm$^3$, mL.
- Prop **I (a)** : unités de durée et leurs relations.
- Méth **I (a)** : conversions de durées.
- Méth **I (a)** : calculs sur horaires et durées.
- Déf **F (b)** : durées en base 60.

### 6e – Géométrie

- Déf **I (a)** : distance entre deux points.
- Déf **I (a)** : milieu d'un segment.
- Déf **I (a)** : corde, disque (le cercle est défini).
- Déf **S (a)** : cercle et disque comme ensembles de points.
- Méth **I (a)** : construire la médiatrice avec règle graduée et équerre.
- Prop **I (a)** : les médiatrices d'un triangle sont concourantes.
- Déf **I (a)** : cercle circonscrit ; Méth **I (a)** : le construire.
- Déf **I (a)** : angles droit, plat, plein, nul, aigu, obtus.
- Déf **I (a)** : angles adjacents, supplémentaires, opposés par le sommet.
- Méth **I (a)** : mesurer un angle au rapporteur.
- Méth **I (a)** : construire un angle de mesure donnée.
- Méth **I (a)** : construire la bissectrice.
- Prop **I (a)** : angles du triangle isocèle, équilatéral, rectangle.
- Méth **I (a)** : calculer un angle avec la somme des angles d'un triangle.
- Méth **I (a)** : construire un triangle (trois côtés ; deux côtés et un angle ; un côté et deux angles).
- Déf **I (a)** : trapèze, trapèze rectangle (CM, repris en 6e par reconnaissance).
- Déf **S (b)** : pentagone, hexagone.
- Prop **I (a)** : propriétés du carré, du rectangle, du losange (côtés, angles, diagonales).
- Déf **I (a)** : symétrique d'un point par rapport à une droite.
- Méth **S (a)** : tracer le symétrique d'une figure par pliage ou sur quadrillage.
- Méth **S (b)** : tracer une perpendiculaire à l'équerre.

### 6e – Proportionnalité

- Déf **I (a)** : coefficient de proportionnalité.
- Méth **I (a)** : linéarité multiplicative et additive.
- Méth **I (a)** : retour à l'unité.
- Déf **I (a)** : échelle ; Méth **I (a)** : calculer avec une échelle.
- Méth **S (a)** : représenter par un tableau ou par des notations symboliques.
- Déf **S (a)** : « fois plus / fois moins ».

### 6e – Données et probabilités

- Méth **S (a)** : construire un tableau, filtrer selon un critère.
- Prop **I (a)** : une probabilité est comprise entre 0 et 1.
- Déf **I (a)** : équiprobabilité ; Méth **I (a)** : calculer une probabilité.
- Méth **S (a)** : comparer résultats d'une répétition et probabilité calculée.

### 6e – Pensée informatique

- Déf **S (a)** : instruction et séquence d'instructions.
- Déf **F (a)** : répétition d'une séquence.

### 5e – Nombres et calculs

- Déf **I (a)** : valeur absolue (« distance à zéro » est employée sans définition).
- Déf **I (a)** : positif, strictement positif, négatif, strictement négatif (zéro absent de la définition actuelle).
- Méth **I (a)** : repérer et placer un relatif sur une droite graduée.
- Méth **S (a)** : ranger des relatifs en ordre croissant et décroissant.
- Méth **I (a)** : addition de plusieurs relatifs.
- Règle **I (a)** : suppression des parenthèses précédées de $+$ ou de $-$.
- Règle **I (a)** : enchaîner additions et soustractions de relatifs.
- Règle **S (a)** : quand les parenthèses sont indispensables.
- Prop **S (b)** : somme de deux opposés égale 0.
- Méth **I (a)** : diviser par un décimal.
- Méth **S (a)** : traduire un programme de calcul en expression.
- Déf **S (b)** : somme et produit comme nature d'une expression (déjà vus en 6e, repris en 5e).
- Méth **I (a)** : comparer des fractions.
- Méth **I (a)** : addition et soustraction à dénominateurs quelconques (réduction au même dénominateur).
- Prop **I (a)** : soustraction de fractions de même dénominateur.
- Déf **I (a)** : cube d'un nombre ; notation $a^3$.
- Prop **I (a)** : carrés parfaits de 0 à 12 ; cube de 10.
- Méth **S (a)** : écrire un nombre sous forme de puissance 2 ou 3.
- Règle **I (a)** : priorité des puissances dans un calcul (`priorites_de_calculs` n'en parle pas).
- Prop **I (a)** : $k(a-b)=ka-kb$ ; Méth **I (a)** : factoriser.
- Méth **I (a)** : reconnaître une somme ou un produit.
- Méth **S (a)** : réduire $ax+b$.
- Règle **S (b)** : $1\times x=x$, $x+x=2x$, $x\times x=x^2$, $3x+2x=5x$.
- Méth **S (a)** : produire une formule (double, carré, aire, périmètre).
- Méth **S (a)** : démontrer une propriété par calcul littéral.
- Déf **I (a)** : donner à la lettre le statut d'inconnue.
- Méth **I (a)** : modéliser et résoudre $ax=c$ et $x+b=c$ (opérations inverses).
- Prop **F (a)** : démonstration de la somme des angles d'un triangle.
- Prolongements : notation $\mathbb N,\mathbb Z,\mathbb D,\mathbb Q$ (en 3e).

### 5e – Espace et géométrie

- Déf **I (a)** : cube, pavé droit, prisme droit, cylindre de révolution.
- Déf **I (b)** : patron d'un solide.
- Règle **I (a)** : perspective cavalière.
- Prop **I (a)** : volume du cube, du pavé droit, du prisme droit, du cylindre.
- Prop **I (a)** : conversions de volumes et de capacités.
- Méth **I (a)** : lire les coordonnées et placer un point dans un repère orthogonal.
- Méth **S (a)** : lire une abscisse ; Déf **S (b)** : origine et axes d'un repère.
- Prop **I (a)** : propriétés du demi-tour (longueurs, angles, alignement, parallélisme conservés).
- Déf **S (b)** : centre de symétrie.
- Déf **I (a)** : angles alternes-internes et correspondants (vocabulaire, les propriétés existent).
- Déf **S (b)** : angles complémentaires.
- Méth **I (a)** : tracer des triangles à partir de données partielles.
- Déf **I (a)** : médiane d'un triangle ; Méth **I (a)** : la tracer ; Prop **I (a)** : elle partage le triangle en deux aires égales.
- Prop **I (a)** : les hauteurs sont concourantes ; Méth **I (a)** : tracer une hauteur.
- Prop **I (a)** : médiatrices et cercle circonscrit dans les triangles particuliers.
- Prop **I (a)** : aire d'un triangle quelconque ($\frac{b\times h}{2}$).
- Déf **I (a)** : parallélogramme.
- Prop **I (a)** : côtés opposés parallèles et égaux ; diagonales se coupent en leur milieu.
- Prop **I (a)** : propriétés caractéristiques (réciproques).
- Méth **I (a)** : construire un parallélogramme ; justifier sa nature.
- Prop **I (a)** : propriétés caractéristiques du rectangle, du losange, du carré.
- Prop **I (a)** : aire du parallélogramme.
- Méth **I (a)** : conversions de longueurs et d'aires dans un problème.
- Déf **S (b)** : trapèze.
- Prolongements : formule d'Euler (signalé séparément).

### 5e – Données, proportionnalité, fonctions

- Méth **I (a)** : recueillir et organiser des données.
- Méth **I (a)** : représenter (tableau, diagramme en barres, circulaire, graphique cartésien).
- Méth **S (a)** : choisir une représentation adaptée.
- Règle **S (a)** : exprimer une fréquence en fraction, décimal ou pourcentage.
- Déf **I (a)** : expérience aléatoire, issue, événement.
- Déf **I (a)** : probabilité et équiprobabilité.
- Méth **S (a)** : échelle de probabilité ; tableau d'effectifs et de fréquences.
- Méth **I (a)** : calculer et appliquer un pourcentage.
- Méth **I (a)** : reconnaître la proportionnalité (tableau, graphique, nuage de points).
- Méth **S (a)** : représenter par tableau ou graphique.
- Déf **I (a)** : « en fonction de ».
- Méth **I (a)** : produire et lire un tableau de valeurs.
- Méth **S (a)** : tracer un nuage de points ; lire une courbe.
- Méth **S (a)** : produire une formule simple de dépendance.
- Pensée informatique **S (a)** : entrées et sorties, expression informatique, boucle inconditionnelle.

### 4e – Nombres et calculs

- Règle **I (a)** : multiplication de deux relatifs (règle des signes).
- Règle **I (a)** : division de deux relatifs.
- Règle **S (a)** : enchaînement d'opérations avec des relatifs.
- Méth **S (a)** : vocabulaire d'un programme de calcul.
- Méth **I (a)** : simplifier une fraction.
- Déf **I (a)** : nombre rationnel.
- Prop **I (a)** : opposé d'un rationnel.
- Prop **I (a)** : produit de rationnels (`calcul_fractionnaire` à compléter).
- Méth **I (a)** : fraction d'une fraction, d'un nombre, d'une quantité.
- Déf **I (a)** : inverse d'un nombre et notation.
- Méth **I (a)** : inverse d'une fraction.
- Prop **I (a)** : diviser par une fraction revient à multiplier par son inverse.
- Méth **S (a)** : expressions à plusieurs opérations avec fractions.
- Déf **S (b)** : $a^0$ et $a^1$ (absents de la définition).
- Prop **I (a)** : $a^m\times a^n=a^{m+n}$.
- Prop **I (a)** : $a^n\times b^n=(a\times b)^n$.
- Méth **I (a)** : encadrer $\sqrt a$ entre deux entiers consécutifs.
- Prop **S (b)** : $\sqrt{a^2}=a$.
- Déf **S (b)** : carrés parfaits (rappel).
- Prop **I (a)** : développer et factoriser avec la distributivité simple.
- Méth **S (a)** : démonstrations par calcul algébrique.
- Méth **I (a)** : résoudre $ax+b=c$.
- Méth **I (a)** : mettre en équation et résoudre $ax+b=cx+d$.
- Prolongement : $\sqrt 2$ n'est pas décimal.

### 4e – Espace et géométrie

- Déf **I (a)** : pyramide, cône de révolution.
- Prop **I (a)** : volume d'une pyramide et d'un cône.
- Déf **I (a)** : translation ; Prop **I (a)** : conservation.
- Prop **I (a)** : lien translation et parallélogramme, et angles.
- Prop **I (a)** : trois théorèmes de la droite des milieux.
- Thm **I (a)** : contraposée de Pythagore.
- Méth **I (b)** : calculer une longueur avec Pythagore.
- Méth **I (b)** : démontrer qu'un triangle est rectangle ou non.
- Prop **I (a)** : triangle rectangle et cercle circonscrit (propriété et réciproque).
- Prop **I (a)** : centre du cercle circonscrit à un triangle rectangle.
- Méth **S (a)** : construire un rectangle sans équerre.
- Prolongements : théorème de Varignon.

### 4e – Données et probabilités

- Méth **I (b)** : déterminer une médiane (ordonner ; effectif pair ou impair).
- Prop **S (a)** : effet d'une valeur extrême sur médiane et moyenne.
- Méth **S (a)** : comparer deux séries.
- Méth **I (a)** : moyenne pondérée dans un tableau et un diagramme (la définition existe).
- Déf **I (a)** : vocabulaire ensembliste d'une expérience aléatoire ; événement.
- Déf **I (a)** : complémentaire, réunion, intersection, événement impossible.
- Prop **I (a)** : $P(\bar A)=1-P(A)$.
- Méth **I (a)** : expérience à deux épreuves (tableau ou arbre).
- Prop **S (a)** : fluctuation des fréquences.

### 4e – Proportionnalité et fonctions

- Déf **I (a)** : grandeur quotient, ratio.
- Méth **I (a)** : comparer par un rapport ou un ratio.
- Prop **I (a)** : égalité de rapports (produit en croix).
- Méth **I (a)** : quatrième proportionnelle.
- Méth **I (a)** : calculs avec des pourcentages.
- Déf **I (a)** : coefficient multiplicateur.
- Prop **I (a)** : augmentation et diminution de $t\,\%$ via le coefficient.
- Méth **I (a)** : partage proportionnel.
- Méth **S (a)** : appliquer un programme de calcul ; le remonter.
- Méth **S (a)** : produire une formule littérale ; la représenter.
- Pensée informatique **S (a)** : conditions, variable.

### 3e – Nombres et calculs

- Méth **I (a)** : mettre une fraction sous forme irréductible (décomposition ou diviseurs communs).
- Méth **I (a)** : décomposer en facteurs premiers.
- Prop **S (b)** : unicité de la décomposition.
- Déf **S (b)** : liste des nombres premiers inférieurs à 100.
- Prop **I (a)** : $a^m\times a^n$, $\frac{a^m}{a^n}$, $(a^m)^n$, $(ab)^n$.
- Prop **S (b)** : $a^0=1$.
- Méth **I (a)** : écrire en notation scientifique.
- Méth **I (a)** : calculs avec la notation scientifique.
- Déf **S (b)** : préfixes (kilo, méga, micro, nano).
- Prop **I (a)** : $x^2=a$ : trois cas ($a>0$, $a=0$, $a<0$).
- Méth **S (a)** : résolution graphique de $x^2=a$.
- Prop **F (b)** : $\sqrt a\times\sqrt b$ (hors index).
- Prop **I (a)** : identités remarquables $(a+b)^2$ et $(a-b)^2$.
- Méth **I (a)** : développer et factoriser avec les trois identités.
- Méth **I (a)** : factoriser par un facteur commun.
- Méth **I (a)** : factoriser avec la double distributivité.
- Méth **S (a)** : simplifier des produits ou des rapports à facteurs communs.
- Prop **S (b)** : $-(a-b)=-a+b$.
- Déf **I (a)** : inéquation du premier degré ; Prop **I (a)** : multiplier ou diviser par un négatif.
- Méth **I (a)** : résoudre analytiquement et graphiquement $ax\ge b$.
- Méth **I (a)** : résoudre une équation produit nul.
- Méth **F (a)** : analyse-synthèse.
- Prolongement : identité de Sophie Germain.

### 3e – Espace et géométrie

- Déf **I (a)** : boule, sphère, grands cercles.
- Prop **I (a)** : sections de pavé, de cylindre et de boule.
- Prop **I (a)** : volume d'une boule.
- Thm **I (a)** : Thalès avec rapports, dans les deux configurations.
- Thm **I (a)** : contraposée de Thalès.
- Méth **I (a)** : calculer une longueur avec Thalès.
- Méth **I (a)** : prouver un parallélisme avec la réciproque.
- Prop **I (a)** : sinus, cosinus, tangente en triangle rectangle (`calcul_trigonometrie_2` existe).
- Méth **I (a)** : calculer une longueur avec la trigonométrie.
- Méth **I (a)** : calculer un angle avec les touches réciproques.
- Prop **F (b)** : $\cos^2+\sin^2=1$.
- Déf **I (a)** : translation (définition ponctuelle avec parallélogramme).
- Déf **I (a)** : vecteur, vecteurs égaux, nul, opposé.
- Déf **I (a)** : somme de deux vecteurs.
- Prop **I (a)** : relation de Chasles.
- Prop **S (b)** : lien vecteurs et parallélogramme.

### 3e – Données, proportionnalité, fonctions

- Déf **I (a)** : effectifs cumulés croissants.
- Déf **I (a)** : quartiles ; Méth **I (a)** : les déterminer.
- Déf **I (a)** : boîte à moustaches ; Méth **I (a)** : la construire.
- Prop **I (a)** : $P(A\cup B)+P(A\cap B)=P(A)+P(B)$.
- Déf **S (a)** : expériences indépendantes ; Méth **S (a)** : les simuler.
- Prop **S (a)** : stabilisation des fréquences.
- Méth **I (a)** : traduire une variation en pourcentage.
- Prop **S (a)** : représentation graphique d'une proportionnalité et Thalès.
- Déf **I (a)** : coefficient d'une fonction linéaire ; Méth **I (a)** : déterminer $f$ à partir d'une valeur.
- Méth **I (a)** : lire image et antécédent sur un graphique.
- Déf **I (a)** : coefficient directeur, ordonnée à l'origine.
- Méth **I (a)** : déterminer graphiquement $a$ et $b$.
- Méth **S (b)** : déterminer $f(x)=ax+b$ à partir de deux points.
- Déf **I (a)** : fonction carré ; Méth **I (a)** : la représenter.
- Méth **S (a)** : résoudre graphiquement équations et inéquations linéaires.
- Pensée informatique **S (a)** : variables, conditions composées, boucle conditionnelle, structuration.

## D. Lacunes, par gravité

1. **Notions absentes du cours :** probabilités (tous niveaux), solides et volumes (5e, 4e, 3e), parallélogrammes (5e), translations et vecteurs (4e, 3e), boule et sphère, règle des signes (4e), proportionnalité 4e, statistiques 3e, pensée informatique.
2. **Énoncés incomplets ou erronés :** `calcul_fractionnaire`, `thales`, `reciproque_thales`, `symetrie_centrale`, `construction_point_symetrie_centrale`, `notation_scientifique` (à vérifier), `criteres_de_divisibilite`, `aire_triangle_rectangle`, `division_euclidienne`.
3. **Énoncés sans attendu identifiable :** `homothetie`, `triangles_semblables`, cas d'égalité des triangles (**À VÉRIFIER**).
4. **Doublons à clarifier :** voir la liste ci-dessus.

## E. Recommandations

- **Ajouts indispensables :** toutes les entrées marquées **I** en B. Priorité d'ordre : probabilités, solides, parallélogrammes, translation et vecteurs, règle des signes.
- **Compléments souhaitables :** toutes les entrées **S**, et la correction des énoncés listés en D.2.
- **Améliorations facultatives :** entrées **F**, prolongements historiques, harmonisation des doublons.

## F. Conclusion

L'audit des énoncés est complet sur les 168 fichiers, mais l'appariement avec le programme se fait par sous-thème. Les propositions **(b)** et les cas **À VÉRIFIER** demandent le texte intégral des programmes. Les activités ne sont pas auditées : cela demanderait une passe dédiée sur `activites/`.