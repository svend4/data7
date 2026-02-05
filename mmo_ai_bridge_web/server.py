"""
MMO AI Bridge - Flask Web Server with WebSocket Support & Database
Provides REST API and real-time WebSocket updates for AI text → MMO visualization translation
Includes persistent storage for character history and training sessions

Author: AI Research Assistant
Date: 2026-02-05
Version: 1.0 - PRODUCTION RELEASE
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
import time
import threading
import json
import csv
from io import StringIO
from datetime import datetime

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

# Import database module
try:
    from database import get_database
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    print("Warning: Could not import database module. Running without persistence.")

app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize components
if HAS_MMO_BRIDGE:
    translator = TextToVisualTranslator()
    concept_db = AIConceptDatabase()

if HAS_DATABASE:
    db = get_database()

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
            char_data = {
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
            }

            # Save to database if available
            if HAS_DATABASE:
                try:
                    char_id = db.create_character(
                        name=char.name,
                        char_class=char.char_class.class_name,
                        level=char.level,
                        health=char.health,
                        metrics=char.metrics
                    )
                    db.update_character(
                        char_id,
                        mana=char.mana,
                        experience=char.experience,
                        position_x=char.x,
                        position_y=char.y,
                        status=char.status.value
                    )
                    char_data['db_id'] = char_id
                except Exception as db_error:
                    print(f"Database error: {db_error}")
                    # Continue without database save

            characters_json.append(char_data)

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
    db_status = "available" if HAS_DATABASE else "unavailable"
    db_size = db.get_database_size() if HAS_DATABASE else 0

    return jsonify({
        "status": "healthy",
        "version": "1.1",
        "mmo_bridge_available": HAS_MMO_BRIDGE,
        "database_available": HAS_DATABASE,
        "database_status": db_status,
        "database_size_bytes": db_size
    })


# ============================================================================
# Database API Endpoints (NEW in v0.95)
# ============================================================================

@app.route('/api/characters', methods=['GET'])
def get_characters_list():
    """Get list of all characters"""
    if not HAS_DATABASE:
        return jsonify({"error": "Database not available"}), 503

    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        characters = db.get_all_characters(limit=limit, offset=offset)

        # Parse JSON metrics for each character
        for char in characters:
            if char.get('metrics_json'):
                try:
                    char['metrics'] = json.loads(char['metrics_json'])
                except:
                    char['metrics'] = {}
                del char['metrics_json']

        return jsonify({
            "characters": characters,
            "count": len(characters),
            "limit": limit,
            "offset": offset
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/characters/<int:char_id>', methods=['GET'])
def get_character_details(char_id):
    """Get detailed information about a specific character"""
    if not HAS_DATABASE:
        return jsonify({"error": "Database not available"}), 503

    try:
        char_stats = db.get_character_stats(char_id)
        if not char_stats:
            return jsonify({"error": "Character not found"}), 404

        # Parse JSON metrics
        if char_stats.get('metrics_json'):
            try:
                char_stats['metrics'] = json.loads(char_stats['metrics_json'])
            except:
                char_stats['metrics'] = {}
            del char_stats['metrics_json']

        return jsonify(char_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/characters/<int:char_id>/history', methods=['GET'])
def get_character_history(char_id):
    """Get training history for a character"""
    if not HAS_DATABASE:
        return jsonify({"error": "Database not available"}), 503

    try:
        limit = int(request.args.get('limit', 10))
        sessions = db.get_character_sessions(char_id, limit=limit)

        return jsonify({
            "character_id": char_id,
            "sessions": sessions,
            "count": len(sessions)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions', methods=['GET'])
def get_recent_sessions():
    """Get recent training sessions"""
    if not HAS_DATABASE:
        return jsonify({"error": "Database not available"}), 503

    try:
        limit = int(request.args.get('limit', 20))
        sessions = db.get_recent_sessions(limit=limit)

        return jsonify({
            "sessions": sessions,
            "count": len(sessions)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get detailed information about a training session"""
    if not HAS_DATABASE:
        return jsonify({"error": "Database not available"}), 503

    try:
        session = db.get_training_session(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404

        # Get epoch-by-epoch metrics
        metrics = db.get_session_metrics(session_id)

        return jsonify({
            "session": session,
            "metrics": metrics
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get global statistics"""
    if not HAS_DATABASE:
        return jsonify({"error": "Database not available"}), 503

    try:
        stats = db.get_global_statistics()

        # Get historical data if requested
        days = int(request.args.get('days', 0))
        if days > 0:
            history = db.get_statistics_history(days=days)
            stats['history'] = history

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/export/json', methods=['GET'])
def export_json():
    """Export all data as JSON"""
    if not HAS_DATABASE:
        return jsonify({"error": "Database not available"}), 503

    try:
        data = db.export_to_dict()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export characters as CSV"""
    if not HAS_DATABASE:
        return "Database not available", 503

    try:
        characters = db.get_all_characters(limit=1000)

        # Create CSV
        output = StringIO()
        if characters:
            fieldnames = ['id', 'name', 'class', 'level', 'health', 'max_health',
                         'mana', 'experience', 'status', 'created_at', 'total_training_time']
            writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for char in characters:
                writer.writerow(char)

        response = output.getvalue()
        output.close()

        return response, 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=mmo_ai_bridge_characters_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        }
    except Exception as e:
        return str(e), 500


@app.route('/api/export/character/<int:char_id>', methods=['GET'])
def export_character(char_id):
    """Export complete character history as JSON"""
    if not HAS_DATABASE:
        return jsonify({"error": "Database not available"}), 503

    try:
        data = db.export_character_history(char_id)
        if not data:
            return jsonify({"error": "Character not found"}), 404

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/batch/translate', methods=['POST'])
def batch_translate():
    """
    Translate multiple AI texts in batch

    Request JSON:
    {
        "texts": ["Training Random Forest...", "Using BERT for NLP..."]
    }
    """
    if not HAS_MMO_BRIDGE:
        return jsonify({"error": "MMO Bridge not available"}), 503

    data = request.get_json()
    if not data or 'texts' not in data:
        return jsonify({"error": "Missing 'texts' field"}), 400

    texts = data['texts']
    if not isinstance(texts, list):
        return jsonify({"error": "'texts' must be a list"}), 400

    try:
        results = []
        for text in texts:
            characters, scene_description = translator.translate(text)

            # Convert to JSON
            characters_json = []
            for char in characters:
                char_data = {
                    "name": char.name,
                    "class": char.char_class.class_name,
                    "status": char.status.value,
                    "health": char.health,
                    "level": char.level,
                    "metrics": char.metrics
                }

                # Save to database
                if HAS_DATABASE:
                    try:
                        char_id = db.create_character(
                            name=char.name,
                            char_class=char.char_class.class_name,
                            level=char.level,
                            health=char.health,
                            metrics=char.metrics
                        )
                        char_data['db_id'] = char_id
                    except Exception as db_error:
                        print(f"Database error: {db_error}")

                characters_json.append(char_data)

            results.append({
                "text": text,
                "characters": characters_json,
                "scene_description": scene_description
            })

        return jsonify({
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# Session Recording API (v1.1)
# ============================================================================

@app.route('/api/recordings', methods=['POST'])
def save_recording():
    """Save a session recording"""
    try:
        data = request.json
        session_name = data.get('session_name', f'Recording_{int(time.time())}')
        events = data.get('events', [])
        description = data.get('description')
        duration_seconds = data.get('duration_seconds', 0)

        if not events:
            return jsonify({"error": "No events provided"}), 400

        recording_id = db.save_session_recording(
            session_name=session_name,
            events=events,
            description=description,
            duration_seconds=duration_seconds
        )

        return jsonify({
            "success": True,
            "recording_id": recording_id,
            "event_count": len(events)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recordings', methods=['GET'])
def list_recordings():
    """List all session recordings"""
    try:
        limit = request.args.get('limit', 50, type=int)
        recordings = db.list_session_recordings(limit=limit)

        return jsonify({
            "recordings": recordings,
            "count": len(recordings)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recordings/<int:recording_id>', methods=['GET'])
def get_recording(recording_id):
    """Get a specific session recording with all events"""
    try:
        recording = db.get_session_recording(recording_id)

        if not recording:
            return jsonify({"error": "Recording not found"}), 404

        return jsonify(recording)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recordings/<int:recording_id>', methods=['DELETE'])
def delete_recording(recording_id):
    """Delete a session recording"""
    try:
        success = db.delete_session_recording(recording_id)

        if success:
            return jsonify({"success": True, "message": "Recording deleted"})
        else:
            return jsonify({"error": "Recording not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# WebSocket Event Handlers
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connection_response', {
        "status": "connected",
        "message": "Welcome to MMO AI Bridge v1.1!",
        "version": "1.1"
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
        "speed": 1.0,  # Multiplier for update speed
        "character_id": 123  # Optional: link to existing character
    }
    """
    model_name = data.get('model_name', 'Neural Network')
    epochs = data.get('epochs', 10)
    speed = data.get('speed', 1.0)
    character_id = data.get('character_id', None)

    # Create simulation control structure
    sim_id = request.sid
    start_time = time.time()

    # Create training session in database
    session_id = None
    if HAS_DATABASE:
        try:
            session_id = db.create_training_session(
                character_id=character_id,
                model_name=model_name,
                total_epochs=epochs,
                initial_health=50
            )
        except Exception as db_error:
            print(f"Database error creating session: {db_error}")

    active_simulations[sim_id] = {
        'stop': False,
        'session_id': session_id,
        'start_time': start_time
    }

    def simulate_training():
        """Simulate training process with real-time updates"""
        completed_epochs = 0
        final_accuracy = 0.95
        final_loss = 0.05

        for epoch in range(1, epochs + 1):
            if active_simulations.get(sim_id, {}).get('stop', True):
                break

            # Simulate progress
            progress = epoch / epochs
            health = int(50 + (progress * 50))  # Health increases as training progresses
            accuracy = 0.5 + (progress * 0.45)  # Accuracy improves
            loss = 1.0 - (progress * 0.8)  # Loss decreases

            completed_epochs = epoch
            final_accuracy = round(accuracy, 3)
            final_loss = round(loss, 3)

            # Save metrics to database
            if HAS_DATABASE and session_id:
                try:
                    db.add_training_metric(
                        session_id=session_id,
                        epoch=epoch,
                        accuracy=final_accuracy,
                        loss=final_loss,
                        health=health
                    )
                    db.update_training_session(
                        session_id,
                        completed_epochs=epoch
                    )
                except Exception as db_error:
                    print(f"Database error saving metric: {db_error}")

            # Emit update to client
            socketio.emit('training_update', {
                "model_name": model_name,
                "epoch": epoch,
                "total_epochs": epochs,
                "progress": progress,
                "health": health,
                "metrics": {
                    "accuracy": final_accuracy,
                    "loss": final_loss
                },
                "status": "training"
            }, room=sim_id)

            # Wait between epochs (adjustable by speed)
            time.sleep(0.5 / speed)

        # Calculate duration
        duration = int(time.time() - start_time)

        # Training complete
        was_stopped = active_simulations.get(sim_id, {}).get('stop', True)
        if not was_stopped:
            # Complete the session in database
            if HAS_DATABASE and session_id:
                try:
                    db.complete_training_session(
                        session_id=session_id,
                        final_accuracy=final_accuracy,
                        final_loss=final_loss,
                        final_health=95,
                        duration_seconds=duration
                    )
                    # Update daily statistics
                    db.update_daily_statistics()
                except Exception as db_error:
                    print(f"Database error completing session: {db_error}")

            socketio.emit('training_complete', {
                "model_name": model_name,
                "final_health": 95,
                "final_accuracy": final_accuracy,
                "duration": duration,
                "message": f"{model_name} training completed successfully!"
            }, room=sim_id)
        else:
            # Mark as stopped in database
            if HAS_DATABASE and session_id:
                try:
                    db.update_training_session(
                        session_id,
                        status='stopped',
                        duration_seconds=duration
                    )
                except Exception as db_error:
                    print(f"Database error stopping session: {db_error}")

        # Clean up
        if sim_id in active_simulations:
            del active_simulations[sim_id]

    # Start simulation in background thread
    thread = threading.Thread(target=simulate_training)
    thread.daemon = True
    thread.start()

    emit('simulation_started', {
        "message": f"Starting {model_name} training simulation",
        "epochs": epochs,
        "session_id": session_id
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
    print("🎮 MMO AI BRIDGE v1.1 - CORE ENHANCEMENT UPDATE")
    print("=" * 70)
    print(f"\n🌐 Server: http://localhost:5000")
    print(f"🎯 Statistics Dashboard: http://localhost:5000/stats.html")
    print(f"\n🔧 MMO Bridge Module: {'✅ Available' if HAS_MMO_BRIDGE else '⚠️  Not Available (Fallback Mode)'}")
    print(f"💾 Database: {'✅ Available' if HAS_DATABASE else '⚠️  Not Available'}")
    print("📡 WebSocket Support: ✅ Enabled")
    print("\n🆕 v1.1 Features:")
    print("  ✅ 169 AI concepts (50 → 169)")
    print("  ✅ Session recording & replay")
    print("  ✅ GIF export functionality")
    print("  ✅ Multi-model comparison UI foundation")
    print("\n📍 REST API Endpoints (20 total):")
    print("  Translation:")
    print("    POST /api/translate           - Translate AI text to MMO characters")
    print("    POST /api/batch/translate     - Batch translate multiple texts")
    print("  Characters:")
    print("    GET  /api/characters          - List all characters")
    print("    GET  /api/characters/<id>     - Get character details")
    print("    GET  /api/characters/<id>/history - Get training history")
    print("  Training Sessions:")
    print("    GET  /api/sessions            - Recent training sessions")
    print("    GET  /api/sessions/<id>       - Session details with metrics")
    print("  Statistics:")
    print("    GET  /api/statistics          - Global statistics")
    print("  Export:")
    print("    GET  /api/export/json         - Export all data as JSON")
    print("    GET  /api/export/csv          - Export characters as CSV")
    print("    GET  /api/export/character/<id> - Export character history")
    print("  Recordings (v1.1):")
    print("    POST /api/recordings          - Save session recording")
    print("    GET  /api/recordings          - List all recordings")
    print("    GET  /api/recordings/<id>     - Get recording details")
    print("    DELETE /api/recordings/<id>   - Delete recording")
    print("  Other:")
    print("    GET  /api/concepts            - Get supported AI concepts")
    print("    POST /api/simulate/pipeline   - Simulate ML pipeline")
    print("    GET  /api/health              - Health check")
    print("\n⚡ WebSocket Events:")
    print("  connect                       - Client connection")
    print("  start_training_simulation     - Start real-time training")
    print("  stop_simulation               - Stop active simulation")
    print("  update_character              - Broadcast character updates")
    print("\n📊 Features:")
    print("  ✅ Persistent Storage (SQLite + 6 tables)")
    print("  ✅ Real-time Training Simulation")
    print("  ✅ Advanced Animations (20+)")
    print("  ✅ Statistics Dashboard")
    print("  ✅ Data Export (CSV/JSON/PNG/GIF)")
    print("  ✅ Batch Processing")
    print("  ✅ Session Recording & Replay")
    print("  ✅ Multi-Model Comparison UI")
    print("  ✅ 169 AI Concepts (11 Character Classes)")
    print("\n🎉 Status: v1.1 READY")
    print("\nPress Ctrl+C to stop")
    print("=" * 70 + "\n")

    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
