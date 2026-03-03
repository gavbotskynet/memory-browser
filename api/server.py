#!/usr/bin/env python3
"""
Memory Browser API - using built-in http.server
"""

import sys
sys.path.insert(0, '/home/digi/.openclaw/workspace/adam-memory')
from memory import (
    get_recent_memories, get_memory_by_id, search_memories, get_memories_by_tag,
    get_important_memories, get_all_tags,
    get_session, get_session_topics, get_session_memories, get_recent_sessions,
    add_memory, update_memory, delete_memory,
    stats as get_stats, get_consolidation_stats
)
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 3456

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]
        
        # API routes
        if path == '/api/stats':
            self.send_json(get_stats())
        elif path == '/api/consolidation':
            self.send_json(get_consolidation_stats())
        elif path == '/api/memories':
            limit = int(self.get_param('limit', 50))
            self.send_json(get_recent_memories(limit))
        elif path == '/api/tags':
            self.send_json(get_all_tags())
        elif path == '/api/sessions':
            limit = int(self.get_param('limit', 20))
            self.send_json(get_recent_sessions(limit))
        elif path.startswith('/api/memories/search'):
            q = self.get_param('q', '')
            limit = int(self.get_param('limit', 20))
            self.send_json(search_memories(q, limit))
        elif path.startswith('/api/memories/important'):
            limit = int(self.get_param('limit', 20))
            self.send_json(get_important_memories(limit))
        elif path.startswith('/api/memories/tag/'):
            tag = path.split('/')[-1]
            limit = int(self.get_param('limit', 20))
            self.send_json(get_memories_by_tag(tag, limit))
        elif path.startswith('/api/memories/') and path.split('/')[-1].isdigit():
            memory_id = int(path.split('/')[-1])
            self.send_json(get_memory_by_id(memory_id))
        elif path.startswith('/api/sessions/'):
            session_key = path.split('/')[-1]
            session = get_session(session_key)
            topics = get_session_topics(session_key)
            memories = get_session_memories(session_key)
            self.send_json({'session': session, 'topics': topics, 'memories': memories})
        
        # Frontend
        elif path == '/' or path == '/index.html':
            self.serve_file('public/index.html', 'text/html')
        elif path == '/manifest.json':
            self.serve_file('public/manifest.json', 'application/json')
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = self.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        data = json.loads(body) if body else {}
        
        if path == '/api/memories':
            memory_id = add_memory(
                content=data.get('content', ''),
                tags=data.get('tags'),
                importance=data.get('importance', 2)
            )
            self.send_json({'id': memory_id})
        else:
            self.send_error(404)
    
    def do_PUT(self):
        path = self.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        data = json.loads(body) if body else {}
        
        if path.startswith('/api/memories/') and path.split('/')[-1].isdigit():
            memory_id = int(path.split('/')[-1])
            update_memory(memory_id, **data)
            self.send_json({'success': True})
        else:
            self.send_error(404)
    
    def do_DELETE(self):
        path = self.path
        if path.startswith('/api/memories/') and path.split('/')[-1].isdigit():
            memory_id = int(path.split('/')[-1])
            delete_memory(memory_id)
            self.send_json({'success': True})
        else:
            self.send_error(404)
    
    def get_param(self, key, default=''):
        if '?' in self.path:
            params = self.path.split('?')[1].split('&')
            for p in params:
                if p.startswith(f'{key}='):
                    return p.split('=')[1]
        return default
    
    def send_json(self, data):
        # Clean up memories for JSON
        if isinstance(data, list):
            for m in data:
                if m.get('tags') and isinstance(m['tags'], str):
                    m['tags'] = json.loads(m['tags'])
        
        response = json.dumps(data, default=str)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def serve_file(self, filepath, content_type):
        full_path = f'/home/digi/.openclaw/workspace/memory-browser/{filepath}'
        if os.path.exists(full_path):
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            with open(full_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        print(f"{args[0]} {args[1]}")

if __name__ == '__main__':
    server = HTTPServer(('', PORT), Handler)
    print(f"Memory Browser running on http://localhost:{PORT}")
    server.serve_forever()
