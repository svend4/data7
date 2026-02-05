"""
MMO AI Bridge - Flask Web Server with WebSocket Support
Provides REST API and real-time WebSocket updates for AI text → MMO visualization translation

Author: AI Research Assistant
Date: 2026-02-05
Version: 0.85
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
import time
import threading

# Add parent directory to path to import mmo_ai_bridge_v05
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from mmo_ai_bridge_v05 import (
        AIConceptDatabase,
        TextToVisualTranslator,
        MMOCharacter,
        CharacterClass,
        ActionType
    )
    HAS_MMO_BRIDGE = True
except ImportError:
    HAS_MMO_BRIDGE = False
    print("Warning: Could not import mmo_ai_bridge_v05. Using fallback mode.")

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize translator
if HAS_MMO_BRIDGE:
    translator = TextToVisualTranslator()
    concept_db = AIConceptDatabase()

# Store active simulations
active_simulations = {}


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')


@app.route('/api/translate', methods=['POST'])
def translate_ai_text():
    """
    Translate AI text to MMO characters

    Request JSON:
    {
        "text": "Training a Random Forest model..."
    }

    Response JSON:
    {
        "characters": [
            {
                "name": "Random Forest",
                "class": "Druid",
                "status": "training",
                "health": 95,
                "level": 2,
                "metrics": {"accuracy": 0.95, "trees": 100}
            }
        ],
        "scene_description": "..."
    }
    """
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field in request"}), 400

    ai_text = data['text']

    if not HAS_MMO_BRIDGE:
        # Fallback response if module not available
        return jsonify({
            "characters": [{
                "name": "AI Agent",
                "class": "Mage",
                "status": "training",
                "health": 90,
                "level": 1,
                "metrics": {"accuracy": 0.90}
            }],
            "scene_description": "1 AI agent (Mage) performing training"
        })

    try:
        # Use the translator from mmo_ai_bridge_v05
        characters, scene_description = translator.translate(ai_text)

        # Convert characters to JSON-serializable format
        characters_json = []
        for char in characters:
            characters_json.append({
                "name": char.name,
                "class": char.char_class.class_name,
                "status": char.status.value,
                "health": char.health,
                "max_health": char.max_health,
                "level": char.level,
                "mana": char.mana,
                "experience": char.experience,
                "metrics": char.metrics,
                "x": char.x,
                "y": char.y
            })

        return jsonify({
            "characters": characters_json,
            "scene_description": scene_description
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/concepts', methods=['GET'])
def get_concepts():
    """
    Get list of all supported AI concepts

    Response JSON:
    {
        "models": ["random forest", "bert", "cnn", ...],
        "actions": ["training", "predicting", ...],
        "classes": [
            {"name": "Warrior", "icon": "💪", "represents": "Linear models"}
        ]
    }
    """
    if not HAS_MMO_BRIDGE:
        return jsonify({
            "models": ["neural network", "random forest"],
            "actions": ["training", "predicting"],
            "classes": []
        })

    return jsonify({
        "models": list(concept_db.model_to_class.keys()),
        "actions": list(concept_db.action_to_animation.keys()),
        "classes": [
            {
                "name": cls.class_name,
                "icon": cls.icon,
                "color": cls.color,
                "represents": f"AI archetype: {cls.name}"
            }
            for cls in CharacterClass
        ]
    })


@app.route('/api/simulate/pipeline', methods=['POST'])
def simulate_pipeline():
    """
    Simulate a complete ML pipeline

    Request JSON:
    {
        "pipeline": ["data_collector", "preprocessor", "model", "validator"],
        "objective": "Train image classifier"
    }

    Response JSON:
    {
        "party": {
            "name": "ML Pipeline Party",
            "members": [...],
            "objective": "...",
            "phases": [...]
        }
    }
    """
    data = request.get_json()

    # Simplified simulation response
    return jsonify({
        "party": {
            "name": "ML Pipeline Party",
            "objective": data.get('objective', 'Complete ML task'),
            "members": [
                {"name": "Data Collector", "class": "Rogue", "status": "collecting"},
                {"name": "Preprocessor", "class": "Alchemist", "status": "preprocessing"},
                {"name": "Model", "class": "Mage", "status": "training"},
                {"name": "Validator", "class": "Paladin", "status": "validating"}
            ]
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "0.85",
        "mmo_bridge_available": HAS_MMO_BRIDGE
    })


# ============================================================================
# WebSocket Event Handlers
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connection_response', {
        "status": "connected",
        "message": "Welcome to MMO AI Bridge!",
        "version": "0.85"
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    # Clean up any active simulations for this client
    if request.sid in active_simulations:
        active_simulations[request.sid]['stop'] = True
        del active_simulations[request.sid]


@socketio.on('start_training_simulation')
def handle_training_simulation(data):
    """
    Start a real-time training simulation

    Data:
    {
        "model_name": "Random Forest",
        "epochs": 10,
        "speed": 1.0  # Multiplier for update speed
    }
    """
    model_name = data.get('model_name', 'Neural Network')
    epochs = data.get('epochs', 10)
    speed = data.get('speed', 1.0)

    # Create simulation control structure
    sim_id = request.sid
    active_simulations[sim_id] = {'stop': False}

    def simulate_training():
        """Simulate training process with real-time updates"""
        for epoch in range(1, epochs + 1):
            if active_simulations.get(sim_id, {}).get('stop', True):
                break

            # Simulate progress
            progress = epoch / epochs
            health = int(50 + (progress * 50))  # Health increases as training progresses
            accuracy = 0.5 + (progress * 0.45)  # Accuracy improves
            loss = 1.0 - (progress * 0.8)  # Loss decreases

            # Emit update to client
            socketio.emit('training_update', {
                "model_name": model_name,
                "epoch": epoch,
                "total_epochs": epochs,
                "progress": progress,
                "health": health,
                "metrics": {
                    "accuracy": round(accuracy, 3),
                    "loss": round(loss, 3)
                },
                "status": "training"
            }, room=sim_id)

            # Wait between epochs (adjustable by speed)
            time.sleep(0.5 / speed)

        # Training complete
        if not active_simulations.get(sim_id, {}).get('stop', True):
            socketio.emit('training_complete', {
                "model_name": model_name,
                "final_health": 95,
                "final_accuracy": 0.95,
                "message": f"{model_name} training completed successfully!"
            }, room=sim_id)

        # Clean up
        if sim_id in active_simulations:
            del active_simulations[sim_id]

    # Start simulation in background thread
    thread = threading.Thread(target=simulate_training)
    thread.daemon = True
    thread.start()

    emit('simulation_started', {
        "message": f"Starting {model_name} training simulation",
        "epochs": epochs
    })


@socketio.on('stop_simulation')
def handle_stop_simulation():
    """Stop active simulation for this client"""
    sim_id = request.sid
    if sim_id in active_simulations:
        active_simulations[sim_id]['stop'] = True
        emit('simulation_stopped', {
            "message": "Simulation stopped"
        })


@socketio.on('update_character')
def handle_character_update(data):
    """
    Broadcast character updates to all clients

    Data:
    {
        "character_name": "Random Forest",
        "health": 95,
        "status": "training",
        "metrics": {...}
    }
    """
    # Broadcast to all connected clients
    emit('character_updated', data, broadcast=True)


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🎮 MMO AI BRIDGE - Web Server v0.85 Starting")
    print("=" * 70)
    print(f"\nServer: http://localhost:5000")
    print(f"MMO Bridge Module: {'✅ Available' if HAS_MMO_BRIDGE else '⚠️  Not Available (Fallback Mode)'}")
    print("\n📡 WebSocket Support: ✅ Enabled")
    print("\nAPI Endpoints:")
    print("  POST /api/translate     - Translate AI text to MMO characters")
    print("  GET  /api/concepts      - Get supported AI concepts")
    print("  POST /api/simulate/pipeline - Simulate ML pipeline")
    print("  GET  /api/health        - Health check")
    print("\nWebSocket Events:")
    print("  connect                     - Client connection")
    print("  start_training_simulation   - Start real-time training")
    print("  stop_simulation            - Stop active simulation")
    print("  update_character           - Broadcast character updates")
    print("\nPress Ctrl+C to stop")
    print("=" * 70 + "\n")

    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
