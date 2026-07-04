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

## Dépendances externes

Les exécutables suivants doivent être installés et accessibles via le `PATH` :

| Outil | Utilisation |
|-------|-------------|
| ImageMagick (`magick`) | Conversion d'images et de GIF |
| FFmpeg (`ffmpeg`) | Encodage et traitement des vidéos |