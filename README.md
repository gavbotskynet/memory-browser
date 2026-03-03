# Adam's Memory Browser

A PWA for browsing Adam's memory database.

## Features

- View all memories (Recent, Important, All)
- Search memories
- View sessions
- Real-time stats
- PWA-installable

## Running

```bash
python3 api/server.py
```

Then open: `http://localhost:3456`

## API

- `GET /api/stats` - Memory statistics
- `GET /api/memories` - List memories
- `GET /api/memories/important` - Important memories
- `GET /api/memories/search?q=query` - Search
- `GET /api/memories/tag/{tag}` - By tag
- `GET /api/sessions` - List sessions
- `GET /api/sessions/{key}` - Session details
- `POST /api/memories` - Add memory
- `PUT /api/memories/{id}` - Update memory
- `DELETE /api/memories/{id}` - Delete memory

## Tech

- Backend: Python (no dependencies, built-in http.server)
- Frontend: Vanilla HTML/CSS/JS
- Data: SQLite (Adam's memory system)
