src/

├── app/
│   ├── context.py
│   ├── paths.py
│   ├── config.py
│   └── startup.py
│
├── models/
│   ├── document.py
│   ├── search_filters.py
│   └── settings.py
│
├── services/
│   ├── document_repository.py
│   ├── search_service.py
│   ├── preview_service.py
│   ├── process_service.py
│   ├── theme_service.py
│   ├── database_service.py
│   └── katex_service.py
│
├── controllers/
│   ├── search_controller.py
│   ├── database_controller.py
│   └── document_controller.py
│
├── workers/
│   └── database_worker.py
│
├── views/
│   ├── main_window.py
│   │
│   ├── tabs/
│   │   ├── search_tab.py
│   │   └── settings_tab.py
│   │
│   ├── widgets/
│   │   ├── search_bar.py
│   │   ├── results_list.py
│   │   ├── pdf_viewer.py
│   │   ├── metadata_view.py
│   │   ├── filters_panel.py
│   │   └── console_widget.py
│   │
│   └── dialogs/
│
├── external/
│
└── main.py

## Filtres de recherche des documents PDF

Dans l'onglet « Documents », le bouton « Filtres » ouvre les sélections de
types et de champs recherchés. « Seul » sélectionne un élément exclusivement ;
« Tous », « Aucun » et « Réinitialiser les filtres » permettent de modifier
rapidement les sélections. Le point sur le bouton indique un filtre
personnalisé et son info-bulle résume les éléments actifs.

Les sélections sont enregistrées automatiquement dans la configuration
utilisateur. Une catégorie réglée sur « Tous » inclut aussi les nouveaux
éléments ; dans une sélection personnalisée, les nouveaux éléments restent
décochés et les éléments temporairement absents restent mémorisés.

## Dépendances externes

Les exécutables suivants doivent être installés et accessibles via le `PATH` :

| Outil | Utilisation |
|-------|-------------|
| ImageMagick (`magick`) | Conversion d'images et de GIF |
| FFmpeg (`ffmpeg`) | Encodage et traitement des vidéos |