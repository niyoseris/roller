"""
Web monitoring interface for Trend Collector Agent
Provides a simple web dashboard on port 5001
"""

import asyncio
import json
from datetime import datetime
from aiohttp import web
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WebMonitor:
    """Web-based monitoring dashboard"""
    
    def __init__(self, agent, port=5001):
        self.agent = agent
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'cycles_completed': 0,
            'articles_submitted': 0,
            'last_cycle_time': None,
            'last_trends_count': 0
        }
    
    def setup_routes(self):
        """Setup web routes"""
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/api/status', self.handle_status)
        self.app.router.add_get('/api/stats', self.handle_stats)
        self.app.router.add_get('/api/processed', self.handle_processed)
        self.app.router.add_get('/api/models', self.handle_models)
        self.app.router.add_post('/api/model/select', self.handle_model_select)
    
    async def handle_index(self, request):
        """Serve main dashboard page"""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trend Collector - Monitoring Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
        }
        h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-label {
            color: #888;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        .stat-value {
            color: #333;
            font-size: 2.5em;
            font-weight: bold;
        }
        .status {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }
        .status-active {
            background: #4ade80;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        .info-row:last-child {
            border-bottom: none;
        }
        .info-label {
            color: #666;
            font-weight: 500;
        }
        .info-value {
            color: #333;
            font-weight: 600;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 20px;
            transition: background 0.2s;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Agentic Trend Collector</h1>
            <p class="subtitle">Monitoring US trends across multiple platforms</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Cycles Completed</div>
                <div class="stat-value" id="cycles">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Articles Submitted</div>
                <div class="stat-value" id="articles">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Last Cycle Trends</div>
                <div class="stat-value" id="trends">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Processed URLs</div>
                <div class="stat-value" id="processed">-</div>
            </div>
        </div>
        
        <div class="status">
            <h2>
                <span class="status-indicator status-active"></span>
                System Status
            </h2>
            <div class="info-row">
                <span class="info-label">Started</span>
                <span class="info-value" id="started">-</span>
            </div>
            <div class="info-row">
                <span class="info-label">Last Cycle</span>
                <span class="info-value" id="lastCycle">-</span>
            </div>
            <div class="info-row">
                <span class="info-label">Next Cycle In</span>
                <span class="info-value" id="nextCycle">~60 minutes</span>
            </div>
            <div class="info-row">
                <span class="info-label">Request Delay</span>
                <span class="info-value">30 seconds</span>
            </div>
            <div class="info-row">
                <span class="info-label">LLM Model</span>
                <span class="info-value">
                    <select id="modelSelect" onchange="changeModel()" style="padding: 5px; border-radius: 4px; border: 1px solid #ddd;">
                        <option value="">Loading...</option>
                    </select>
                </span>
            </div>
            
            <button class="refresh-btn" onclick="loadStats()">🔄 Refresh Data</button>
        </div>
    </div>
    
    <script>
        let currentModel = '';
        
        async function loadModels() {
            try {
                const response = await fetch('/api/models');
                const data = await response.json();
                
                const select = document.getElementById('modelSelect');
                select.innerHTML = '';
                
                if (data.models && data.models.length > 0) {
                    data.models.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.name;
                        option.textContent = model.name;
                        if (model.name === data.current_model) {
                            option.selected = true;
                            currentModel = model.name;
                        }
                        select.appendChild(option);
                    });
                } else {
                    select.innerHTML = '<option value="">No models found</option>';
                }
            } catch (error) {
                console.error('Error loading models:', error);
                document.getElementById('modelSelect').innerHTML = '<option value="">Error loading</option>';
            }
        }
        
        async function changeModel() {
            const select = document.getElementById('modelSelect');
            const newModel = select.value;
            
            if (newModel === currentModel || !newModel) {
                return;
            }
            
            try {
                const response = await fetch('/api/model/select', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({model: newModel})
                });
                
                const data = await response.json();
                if (data.success) {
                    currentModel = newModel;
                    alert('Model changed to: ' + newModel);
                } else {
                    alert('Failed to change model: ' + data.error);
                    select.value = currentModel;
                }
            } catch (error) {
                console.error('Error changing model:', error);
                alert('Error changing model');
                select.value = currentModel;
            }
        }
        
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('cycles').textContent = data.cycles_completed;
                document.getElementById('articles').textContent = data.articles_submitted;
                document.getElementById('trends').textContent = data.last_trends_count;
                document.getElementById('processed').textContent = data.total_processed;
                document.getElementById('started').textContent = new Date(data.start_time).toLocaleString();
                document.getElementById('lastCycle').textContent = 
                    data.last_cycle_time ? new Date(data.last_cycle_time).toLocaleString() : 'Not yet';
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        // Load on page load
        loadStats();
        loadModels();
        
        // Auto-refresh every 30 seconds
        setInterval(loadStats, 30000);
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def handle_status(self, request):
        """API endpoint for status"""
        return web.json_response({
            'status': 'running',
            'uptime_seconds': (datetime.now() - datetime.fromisoformat(self.stats['start_time'])).total_seconds()
        })
    
    async def handle_stats(self, request):
        """API endpoint for statistics"""
        return web.json_response({
            **self.stats,
            'total_processed': self.agent.url_tracker.get_count()
        })
    
    async def handle_processed(self, request):
        """API endpoint for processed URLs"""
        return web.json_response({
            'count': self.agent.url_tracker.get_count(),
            'urls': list(self.agent.url_tracker.processed_urls)[:100]  # Return first 100
        })
    
    async def handle_models(self, request):
        """API endpoint for available Ollama models"""
        try:
            models = await self.agent.llm_analyzer.list_models()
            return web.json_response({
                'models': models,
                'current_model': self.agent.llm_analyzer.model_name
            })
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return web.json_response({
                'models': [],
                'current_model': self.agent.llm_analyzer.model_name,
                'error': str(e)
            })
    
    async def handle_model_select(self, request):
        """API endpoint to change the active model"""
        try:
            data = await request.json()
            new_model = data.get('model')
            
            if not new_model:
                return web.json_response({
                    'success': False,
                    'error': 'No model specified'
                })
            
            # Change the model
            self.agent.llm_analyzer.set_model(new_model)
            
            return web.json_response({
                'success': True,
                'model': new_model
            })
        except Exception as e:
            logger.error(f"Error changing model: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            })
    
    def update_stats(self, **kwargs):
        """Update statistics"""
        self.stats.update(kwargs)
    
    async def start(self):
        """Start the web server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()
        logger.info(f"Web monitor started on http://0.0.0.0:{self.port}")
