# MMO RPG как визуальный мост - ЧАСТЬ 3

## Техническая архитектура и реализация

---

### 5.2.2 Smart Home: Геймификация домашних дел

**Визуализация умного дома как MMO мира**:

```
🏠 SMART HOME MMO - Floor Plan (Interactive Map)

┌─────────────────────────────────────────────────────────────┐
│                      MY SMART HOME                           │
│                      Level 15 Residence                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┬──────────────┬──────────────┐             │
│  │  🛏️ Bedroom  │  🚿 Bathroom │  👔 Closet   │             │
│  │              │              │              │             │
│  │ [😴 Sleep]   │ [💡 OFF]     │ [🚪 Closed]  │             │
│  │ Temp: 19°C   │              │              │             │
│  │              │              │              │             │
│  │ NPCs:        │ NPCs:        │ NPCs:        │             │
│  │ • Smart Bed  │ • Scale      │ • Smart      │             │
│  │ • Alarm      │ • Lights     │   Mirror     │             │
│  │ • Curtains   │              │              │             │
│  └──────────────┴──────────────┴──────────────┘             │
│                                                               │
│  ┌─────────────────────────────────────────────┐             │
│  │         🛋️ LIVING ROOM (Main Zone)          │             │
│  │                                               │             │
│  │  [📺 TV ON]     [🤖 Roomba: Cleaning 45%]   │             │
│  │  Netflix        ▓▓▓▓▓░░░░░                   │             │
│  │                                               │             │
│  │  [🔊 Speaker]   [💡 Lights: 65%]             │             │
│  │  Playing Jazz   Warm White                    │             │
│  │                                               │             │
│  │  Temp: 21°C ✓   Humidity: 45%                │             │
│  │                                               │             │
│  │  NPCs (4):                                    │             │
│  │  • Smart TV (Lvl 10) - Quest available!      │             │
│  │  • Alexa (Lvl 12) - Listening               │             │
│  │  • Roomba (Lvl 8) - ⚙️ Working              │             │
│  │  • Air Purifier (Lvl 6) - Active             │             │
│  └─────────────────────────────────────────────┘             │
│                                                               │
│  ┌──────────────────┬────────────────────────┐               │
│  │  🍳 Kitchen      │   🏡 Garden (Outside)  │               │
│  │                  │                        │               │
│  │ [☕ Coffee 07:00]│   [💧 Watering 30%]    │               │
│  │ Timer: 5 min     │   ▓▓▓░░░░░░           │               │
│  │                  │                        │               │
│  │ [🍽️ Dishwasher] │   Soil: 68% moisture  │               │
│  │ Status: Clean    │   Temp: 14°C          │               │
│  │                  │                        │               │
│  │ NPCs (4):        │   NPCs (3):            │               │
│  │ • Coffee Maker   │   • Irrigation         │               │
│  │ • Smart Oven     │   • Weather Station    │               │
│  │ • Fridge         │   • Robot Mower        │               │
│  │ • Dishwasher     │                        │               │
│  └──────────────────┴────────────────────────┘               │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  📋 ACTIVE QUESTS:                                           │
│  ⏳ [Roomba] Clean Living Room - 45% complete (13 min left) │
│  ⏳ [Garden] Water plants - 30% complete (7 min left)       │
│  ✅ [Coffee] Brew morning coffee - DONE! (+25 Energy)      │
│                                                               │
│  💡 AVAILABLE QUESTS:                                        │
│  ❗ [Smart TV] "Watch recommended show" (⭐⭐)              │
│  ⚡ [Kitchen] "Start cooking dinner" (⭐⭐⭐)              │
│  📅 [Bedroom] "Prepare for sleep" - unlocks at 22:00       │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│  🏆 ACHIEVEMENTS:                                            │
│  ⭐ Energy Saver - Saved €127 this month                    │
│  ⭐ Clean Streak - 7 days of daily cleaning                 │
│  🔒 Garden Master - Locked (water plants 30 days straight)  │
│                                                               │
│  📊 HOME STATS:                                              │
│  • Comfort Level: 85/100 ▓▓▓▓▓▓▓▓░░                       │
│  • Energy Efficiency: 92/100 ▓▓▓▓▓▓▓▓▓░                   │
│  • Cleanliness: 78/100 ▓▓▓▓▓▓▓░░░                         │
│  • Security: 100/100 ▓▓▓▓▓▓▓▓▓▓ 🔒                        │
└─────────────────────────────────────────────────────────────┘
```

**Геймификация с наградами**:

```python
class HomeTasksGameSystem:
    """
    Система геймификации домашних дел
    """

    def __init__(self):
        self.player_profile = {
            "name": "User",
            "level": 15,
            "xp": 12450,
            "xp_to_next_level": 15000,
            "title": "Homekeeper",
            "achievements": []
        }

        self.tasks = self._define_tasks()
        self.achievements = self._define_achievements()
        self.leaderboard = HomeLeaderboard()

    def _define_tasks(self):
        """
        Домашние задачи с XP наградами
        """
        return {
            # Ежедневные задачи
            "daily": {
                "Vacuum Living Room": {
                    "xp": 50,
                    "duration": "30 min",
                    "category": "cleaning",
                    "device": "Robot Vacuum",
                    "auto": True,  # Можно автоматизировать
                    "combo_with": ["Mop Floor"],  # Комбо бонус
                    "description": "Deploy Roomba to clean living room"
                },

                "Make Bed": {
                    "xp": 20,
                    "duration": "2 min",
                    "category": "tidying",
                    "auto": False,  # Требует ручной работы
                    "morning_bonus": "+10 XP if done before 08:00"
                },

                "Water Plants": {
                    "xp": 30,
                    "duration": "10 min",
                    "category": "garden",
                    "device": "Smart Irrigation",
                    "auto": True,
                    "streak_multiplier": "x1.1 per day (max x2.0)"
                },

                "Brew Morning Coffee": {
                    "xp": 15,
                    "duration": "5 min",
                    "category": "kitchen",
                    "device": "Coffee Machine",
                    "auto": True,
                    "buff": "+25 Energy for 3 hours"
                },

                "Run Dishwasher": {
                    "xp": 25,
                    "duration": "90 min",
                    "category": "kitchen",
                    "device": "Dishwasher",
                    "requirement": "Dishes > 8"
                }
            },

            # Еженедельные задачи
            "weekly": {
                "Deep Clean House": {
                    "xp": 200,
                    "duration": "2 hours",
                    "category": "cleaning",
                    "subtasks": [
                        "Vacuum all rooms",
                        "Mop floors",
                        "Clean bathrooms",
                        "Dust surfaces"
                    ],
                    "achievement": "Spotless Home"
                },

                "Mow Lawn": {
                    "xp": 100,
                    "duration": "45 min",
                    "category": "garden",
                    "device": "Robot Mower",
                    "auto": True,
                    "seasonal": "Spring-Fall only"
                },

                "Grocery Shopping": {
                    "xp": 75,
                    "duration": "60 min",
                    "category": "errands",
                    "smart_assist": "Fridge generates shopping list",
                    "bonus": "+25 XP if under budget"
                }
            },

            # Месячные задачи
            "monthly": {
                "Deep Clean Appliances": {
                    "xp": 300,
                    "duration": "3 hours",
                    "category": "maintenance",
                    "subtasks": [
                        "Descale coffee machine",
                        "Clean oven",
                        "Clean fridge coils",
                        "Replace air filters"
                    ]
                },

                "Energy Audit": {
                    "xp": 150,
                    "duration": "30 min",
                    "category": "optimization",
                    "auto": True,
                    "device": "Smart Meter",
                    "reward": "Report + suggestions to save €20-50/month"
                }
            }
        }

    def _define_achievements(self):
        """
        Achievements (как в Steam играх)
        """
        return {
            "Clean Freak": {
                "description": "Complete daily cleaning tasks for 30 days straight",
                "icon": "🧹",
                "rarity": "Rare",
                "xp_bonus": 500,
                "unlocks": "Golden Vacuum skin for Roomba"
            },

            "Energy Saver Master": {
                "description": "Reduce energy consumption by 30% in one month",
                "icon": "⚡",
                "rarity": "Epic",
                "xp_bonus": 1000,
                "unlocks": "Eco Mode+ (advanced automation)"
            },

            "Green Thumb": {
                "description": "Keep all plants alive for 90 days (no deaths)",
                "icon": "🌱",
                "rarity": "Legendary",
                "xp_bonus": 2000,
                "unlocks": "Plant Whisperer title, advanced garden analytics"
            },

            "Morning Warrior": {
                "description": "Complete morning routine before 07:30 for 14 days",
                "icon": "☀️",
                "rarity": "Uncommon",
                "xp_bonus": 300,
                "unlocks": "Optimized morning automation"
            },

            "Perfect Week": {
                "description": "Complete ALL daily + weekly tasks in one week",
                "icon": "⭐",
                "rarity": "Epic",
                "xp_bonus": 750,
                "unlocks": "Weekly Planner Pro"
            },

            "Smart Home Architect": {
                "description": "Set up 20+ automation routines",
                "icon": "🏗️",
                "rarity": "Rare",
                "xp_bonus": 600,
                "unlocks": "Advanced automation editor"
            }
        }

    def calculate_xp_with_bonuses(self, task: str, context: dict) -> int:
        """
        Расчет XP с бонусами
        """
        base_xp = self.tasks[context["frequency"]][task]["xp"]
        total_xp = base_xp

        # Бонус за стрик
        if "streak" in context:
            streak_multiplier = min(1.0 + (context["streak"] * 0.1), 2.0)
            total_xp *= streak_multiplier

        # Бонус за комбо
        if "combo" in context and context["combo"]:
            total_xp *= 1.25  # +25% за комбо

        # Бонус за раннее выполнение
        if "early_morning" in context and context["early_morning"]:
            total_xp += 10

        # Бонус за perfect execution
        if "perfect" in context and context["perfect"]:
            total_xp *= 1.5

        return int(total_xp)

    def create_weekly_leaderboard(self, family_members: list) -> dict:
        """
        Создание семейного лидерборда (соревнование)
        """
        return {
            "week": "2026-02-03 to 2026-02-09",
            "rankings": [
                {
                    "rank": 1,
                    "player": "Dad",
                    "xp": 1250,
                    "level": 18,
                    "title": "🏆 Homekeeper Champion",
                    "tasks_completed": 42,
                    "achievements_unlocked": ["Perfect Week", "Energy Saver"],
                    "badge": "👑"
                },
                {
                    "rank": 2,
                    "player": "Mom",
                    "xp": 1180,
                    "level": 17,
                    "title": "⭐ Organizer Expert",
                    "tasks_completed": 38,
                    "achievements_unlocked": ["Green Thumb", "Morning Warrior"],
                    "badge": "🌟"
                },
                {
                    "rank": 3,
                    "player": "Teen (16)",
                    "xp": 420,
                    "level": 9,
                    "title": "🌱 Rising Helper",
                    "tasks_completed": 15,
                    "achievements_unlocked": ["First Week"],
                    "improvement": "+45% from last week 📈"
                }
            ],
            "family_bonus": {
                "total_xp": 2850,
                "team_achievements": ["Family Effort (all members participated)"],
                "bonus_reward": "Pizza night voucher 🍕"
            }
        }
```

**Integration с реальными IoT устройствами**:

```python
class MMOToIoTBridge:
    """
    Мост между MMO интерфейсом и реальными IoT устройствами
    Двунаправленная синхронизация
    """

    def __init__(self):
        self.mmo_engine = MMOEngine()
        self.iot_hub = IoTHub()  # Home Assistant, MQTT, etc.

        # Подписка на события
        self.mmo_engine.on_quest_started += self.handle_quest_started
        self.iot_hub.on_device_state_changed += self.handle_device_state_changed

    def handle_quest_started(self, quest: dict):
        """
        Игрок начал квест в MMO → запуск реального устройства
        """
        quest_to_device = {
            "Clean Living Room": lambda: self._start_roomba("living_room"),
            "Brew Coffee": lambda: self._brew_coffee("espresso", cups=2),
            "Water Plants": lambda: self._start_irrigation(duration=10),
            "Adjust Temperature": lambda: self._set_temperature(quest["target_temp"]),
            "Turn On Lights": lambda: self._set_lights(room=quest["room"], brightness=quest["brightness"])
        }

        if quest["name"] in quest_to_device:
            # Выполнить реальное действие
            quest_to_device[quest["name"]]()

            # Обновить MMO UI
            self.mmo_engine.show_notification(
                f"🎮 → 🏠 Started: {quest['name']}",
                type="info"
            )
            self.mmo_engine.start_progress_bar(
                quest_id=quest["id"],
                duration=quest["duration"]
            )

    def _start_roomba(self, room: str):
        """
        MMO квест → Реальный Roomba
        """
        # Отправка команды через IoT hub (например, Home Assistant API)
        self.iot_hub.call_service(
            domain="vacuum",
            service="start",
            entity_id="vacuum.roomba",
            data={"room": room}
        )

        # Анимация в MMO
        roomba_npc = self.mmo_engine.get_npc("Robot Vacuum")
        self.mmo_engine.animate_npc(
            npc=roomba_npc,
            animation="cleaning",
            duration=1800  # 30 min
        )

    def _brew_coffee(self, type: str, cups: int):
        """
        MMO квест → Реальная кофемашина
        """
        self.iot_hub.call_service(
            domain="switch",
            service="turn_on",
            entity_id="switch.coffee_machine"
        )

        # Показать анимацию варки кофе в MMO
        self.mmo_engine.spawn_particle_effect(
            type="steam",
            position=self.mmo_engine.get_npc_position("Coffee Machine"),
            duration=180  # 3 min
        )

        # Таймер обратного отсчета
        self.mmo_engine.show_timer(
            text="☕ Brewing coffee...",
            duration=180,
            on_complete=lambda: self.mmo_engine.show_notification(
                "✅ Coffee ready! +25 Energy buff applied"
            )
        )

    def handle_device_state_changed(self, device: str, old_state: dict, new_state: dict):
        """
        Реальное устройство изменило состояние → обновление MMO
        """
        # Roomba закончил уборку
        if device == "vacuum.roomba" and new_state["state"] == "docked":
            self.mmo_engine.complete_quest("Clean Living Room")
            self.mmo_engine.award_xp(player=self.mmo_engine.current_player, xp=50)
            self.mmo_engine.show_reward(
                "✨ Living room is clean!",
                rewards=["+50 XP", "+5 Comfort", "Achievement progress: Clean Streak (6/7)"]
            )

            # Обновить статус NPC
            roomba_npc = self.mmo_engine.get_npc("Robot Vacuum")
            roomba_npc.set_status("🔋 Charging (35%)")
            roomba_npc.set_dialogue("*happy beeps* I did a good job!")

        # Температура достигла цели
        elif device == "climate.thermostat" and new_state["temperature"] == new_state["target_temp"]:
            self.mmo_engine.show_notification(
                f"🌡️ Temperature reached {new_state['temperature']}°C",
                type="success"
            )

        # Кофе готов
        elif device == "sensor.coffee_machine" and new_state["state"] == "ready":
            self.mmo_engine.complete_quest("Brew Morning Coffee")
            self.mmo_engine.apply_buff(
                player=self.mmo_engine.current_player,
                buff_name="Caffeinated",
                effect="+25 Energy",
                duration=10800  # 3 hours
            )

    def sync_mmo_with_reality(self):
        """
        Полная синхронизация состояния MMO с реальными устройствами
        Вызывается каждые 30 секунд
        """
        # Получить состояние всех устройств из IoT hub
        real_devices = self.iot_hub.get_all_states()

        for device_id, state in real_devices.items():
            # Найти соответствующий NPC в MMO
            npc = self.mmo_engine.find_npc_by_device_id(device_id)

            if npc:
                # Обновить статус NPC
                npc.update_from_real_state(state)

                # Примеры:
                # - Roomba battery → NPC health bar
                # - Thermostat temp → NPC status text
                # - Coffee machine state → NPC dialogue
```

---

## 6. Техническая архитектура

### 6.1 Полная архитектура системы

```
┌────────────────────────────────────────────────────────────────────┐
│                    AI-MMO VISUAL BRIDGE SYSTEM                     │
│                         (5-Layer Architecture)                     │
└────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════╗
║ LAYER 1: AI AGENTS (Источник текстовых данных)                    ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            ║
║  │   GPT-4/o1   │  │  Claude 3.5  │  │   Gemini     │            ║
║  │              │  │   Sonnet     │  │   Pro        │            ║
║  └──────────────┘  └──────────────┘  └──────────────┘            ║
║                                                                     ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            ║
║  │   LLaMA 3    │  │ Custom Fine- │  │  Specialist  │            ║
║  │              │  │ tuned Models │  │  Agents      │            ║
║  └──────────────┘  └──────────────┘  └──────────────┘            ║
║                                                                     ║
║  Input/Output: Text, JSON, structured data                        ║
║  Protocol: REST API, WebSocket, gRPC                              ║
╚═══════════════════════════════════════════════════════════════════╝
                              ↓ ↑
                      ┌──────────────────┐
                      │ Translation Layer │
                      │ Text ← → Symbols  │
                      └──────────────────┘
                              ↓ ↑
╔═══════════════════════════════════════════════════════════════════╗
║ LAYER 2: MMO VISUAL BRIDGE (Псевдозрение / Symbolic Vision)      ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ┌───────────────────────────────────────────────────────┐        ║
║  │            MMO Rendering Engine                       │        ║
║  │                                                         │        ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐│        ║
║  │  │   Entities   │  │   Actions    │  │   Effects   ││        ║
║  │  │  (Персонажи) │  │  (Анимации)  │  │(Спецэффекты)││        ║
║  │  │              │  │              │  │             ││        ║
║  │  │ • Characters │  │ • Movement   │  │ • Particles ││        ║
║  │  │ • NPCs       │  │ • Combat     │  │ • Lighting  ││        ║
║  │  │ • Objects    │  │ • Crafting   │  │ • Sound     ││        ║
║  │  └──────────────┘  └──────────────┘  └─────────────┘│        ║
║  │                                                         │        ║
║  │  Core Systems:                                          │        ║
║  │  • Spatial System: Grid/hex positioning, Z-layers      │        ║
║  │  • Time System: Real-time, turn-based, accelerated    │        ║
║  │  • Physics: 2D/3D collision, pathfinding (A*)         │        ║
║  │  • Event System: Pub/sub for AI ← → MMO communication │        ║
║  │                                                         │        ║
║  │  Rendering:                                             │        ║
║  │  • 2D sprites (for speed)                              │        ║
║  │  • 3D models (for detail)                              │        ║
║  │  • ASCII/Unicode (для терминалов)                     │        ║
║  └───────────────────────────────────────────────────────┘        ║
║                                                                     ║
║  Technologies: Unity, Unreal, Godot, or custom WebGL engine       ║
╚═══════════════════════════════════════════════════════════════════╝
                              ↓ ↑
╔═══════════════════════════════════════════════════════════════════╗
║ LAYER 3: DOMAIN-SPECIFIC ADAPTORS (Переводчики)                  ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ║
║  │  ML Pipeline    │  │  Web Dev        │  │  IoT/Smart Home │  ║
║  │  Visualizer     │  │  Visualizer     │  │  Controller     │  ║
║  │                 │  │                 │  │                 │  ║
║  │ • Data → NPC    │  │ • Code → World  │  │ • Device → NPC  │  ║
║  │ • Model → Boss  │  │ • API → Quest   │  │ • State → Anim  │  ║
║  │ • Training →    │  │ • Deploy →      │  │ • Action →      │  ║
║  │   Combat        │  │   Escort Quest  │  │   Quest         │  ║
║  └─────────────────┘  └─────────────────┘  └─────────────────┘  ║
║                                                                     ║
║  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ║
║  │  Professional   │  │  Info-Broker    │  │  Education &    │  ║
║  │  Simulator      │  │  Network        │  │  Training       │  ║
║  │                 │  │                 │  │                 │  ║
║  │ • Retail        │  │ • News Monitor  │  │ • Skill Tree    │  ║
║  │ • Manufacturing │  │ • Deal Hunter   │  │ • Tutorials     │  ║
║  │ • Healthcare    │  │ • Data Scraper  │  │ • Certification │  ║
║  └─────────────────┘  └─────────────────┘  └─────────────────┘  ║
║                                                                     ║
╚═══════════════════════════════════════════════════════════════════╝
                              ↓ ↑
╔═══════════════════════════════════════════════════════════════════╗
║ LAYER 4: INTEGRATION LAYER (Connectors)                          ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  • REST APIs (HTTP/HTTPS)                                         ║
║  • WebSocket (real-time bidirectional)                            ║
║  • MQTT (IoT devices)                                             ║
║  • Home Assistant API                                             ║
║  • ROS (Robot Operating System)                                   ║
║  • Industrial protocols (Modbus, OPC UA)                          ║
║                                                                     ║
╚═══════════════════════════════════════════════════════════════════╝
                              ↓ ↑
╔═══════════════════════════════════════════════════════════════════╗
║ LAYER 5: REAL-WORLD INTEGRATION (Physical Layer)                 ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            ║
║  │   Physical   │  │   Web APIs   │  │ IoT Devices  │            ║
║  │   Robots     │  │              │  │              │            ║
║  │              │  │ • GitHub     │  │ • Smart Home │            ║
║  │ • Industrial │  │ • AWS        │  │ • Sensors    │            ║
║  │ • Service    │  │ • Databases  │  │ • Actuators  │            ║
║  │ • Humanoid   │  │ • eCommerce  │  │              │            ║
║  └──────────────┘  └──────────────┘  └──────────────┘            ║
║                                                                     ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            ║
║  │   Human      │  │  Simulators  │  │   External   │            ║
║  │   Trainees   │  │              │  │   Systems    │            ║
║  │              │  │ • VR/AR      │  │              │            ║
║  │ • Employees  │  │ • Digital    │  │ • ERP        │            ║
║  │ • Students   │  │   Twins      │  │ • CRM        │            ║
║  │ • Customers  │  │              │  │ • MES        │            ║
║  └──────────────┘  └──────────────┘  └──────────────┘            ║
║                                                                     ║
╚═══════════════════════════════════════════════════════════════════╝
```

### 6.2 Core Components (Детально)

#### 6.2.1 MMO AI Bridge (Главный оркестратор)

```python
class MMOAIBridge:
    """
    Центральный компонент системы
    Соединяет AI агенты с MMO визуализацией
    """

    def __init__(self):
        # Компоненты перевода
        self.text_to_visual = TextToVisualTranslator()
        self.visual_to_text = VisualToTextTranslator()

        # MMO движок
        self.mmo_engine = MMOEngine(
            renderer="Unity",  # или Godot, Unreal, WebGL
            mode="3D"  # или "2D", "ASCII"
        )

        # Менеджер AI агентов
        self.ai_agents = AIAgentManager()

        # Event bus для коммуникации
        self.event_bus = EventBus()

        # Регистрация обработчиков событий
        self._register_event_handlers()

    def _register_event_handlers(self):
        """
        Регистрация обработчиков событий для двунаправленной связи
        """
        # AI → MMO
        self.event_bus.subscribe("ai.response", self.on_ai_response)
        self.event_bus.subscribe("ai.agent_created", self.on_agent_created)
        self.event_bus.subscribe("ai.task_started", self.on_task_started)
        self.event_bus.subscribe("ai.task_completed", self.on_task_completed)

        # MMO → AI
        self.event_bus.subscribe("mmo.player_action", self.on_player_action)
        self.event_bus.subscribe("mmo.npc_interaction", self.on_npc_interaction)
        self.event_bus.subscribe("mmo.quest_accepted", self.on_quest_accepted)
        self.event_bus.subscribe("mmo.quest_completed", self.on_quest_completed)

    def translate_ai_output_to_scene(self, ai_response: str) -> MMOScene:
        """
        AI текстовый вывод → Визуальная сцена MMO

        Пример:
        AI: "I'm training a Random Forest model with 100 trees on 10000 samples"

        MMO Scene:
        - Spawn Druid NPC (Random Forest)
        - Show animation "Summoning 100 tree minions"
        - Display progress bar "Training: 0% → 100%"
        - Show particle effects (learning happening)
        """
        # Парсинг AI ответа
        entities = self.text_to_visual.extract_entities(ai_response)
        actions = self.text_to_visual.extract_actions(ai_response)
        relationships = self.text_to_visual.extract_relationships(ai_response)
        metrics = self.text_to_visual.extract_metrics(ai_response)

        # Создание сцены
        scene = MMOScene()

        # Добавление персонажей (entities)
        for entity in entities:
            character = self._create_character_from_entity(entity)
            position = self._calculate_position(entity, relationships)
            scene.add_character(character, position)

        # Добавление действий (actions)
        for action in actions:
            animation = self._create_animation_from_action(action)
            scene.add_animation(animation)

        # Добавление метрик как UI элементов
        for metric in metrics:
            ui_element = self._create_ui_from_metric(metric)
            scene.add_ui_element(ui_element)

        return scene

    def _create_character_from_entity(self, entity: dict) -> MMOCharacter:
        """
        Создание персонажа MMO из AI сущности

        entity = {
            "type": "ml_model",
            "name": "Random Forest",
            "parameters": {"n_estimators": 100, "max_depth": 10},
            "status": "training"
        }
        """
        # Маппинг типа сущности на класс персонажа
        entity_to_class = {
            "ml_model.random_forest": "Druid",
            "ml_model.neural_network": "Archmage",
            "ml_model.linear_regression": "Warrior",
            "ml_model.svm": "Knight",
            "data_processor": "Alchemist",
            "data_collector": "Rogue",
            "validator": "Paladin"
        }

        char_class = entity_to_class.get(
            f"{entity['type']}.{entity['name'].lower().replace(' ', '_')}",
            "Generic NPC"
        )

        character = MMOCharacter(
            name=entity["name"],
            char_class=char_class,
            level=self._calculate_level(entity),
            stats=self._entity_params_to_stats(entity["parameters"])
        )

        # Визуальные атрибуты
        character.sprite = self._get_sprite_for_class(char_class)
        character.color = self._status_to_color(entity["status"])
        character.size = self._params_to_size(entity["parameters"])

        # Анимация в зависимости от статуса
        if entity["status"] == "training":
            character.set_animation("casting_spell")
        elif entity["status"] == "predicting":
            character.set_animation("attacking")
        elif entity["status"] == "idle":
            character.set_animation("idle")

        return character

    def translate_scene_to_ai_input(self, scene: MMOScene) -> str:
        """
        Визуальная сцена MMO → Текстовое описание для AI

        Обратный процесс - визуальные нейросети могут "видеть" сцену MMO
        и преобразовывать её в текст для LLM
        """
        description_parts = []

        # Описание окружения
        description_parts.append(f"Scene: {scene.name}")
        description_parts.append(f"Location: {scene.location}")
        description_parts.append(f"Time: {scene.time}")

        # Описание персонажей и их позиций
        description_parts.append("\nCharacters present:")
        for char in scene.characters:
            desc = (
                f"- {char.name} (Level {char.level} {char.class_name}) "
                f"at position ({char.x}, {char.y}), "
                f"status: {char.status}, "
                f"health: {char.health}/{char.max_health}"
            )
            description_parts.append(desc)

        # Описание активных действий
        if scene.animations:
            description_parts.append("\nOngoing actions:")
            for anim in scene.animations:
                desc = (
                    f"- {anim.actor.name} is {anim.action_type} "
                    f"{f'towards {anim.target.name}' if anim.target else ''}"
                    f"(progress: {anim.progress}%)"
                )
                description_parts.append(desc)

        # Описание отношений между объектами
        description_parts.append("\nSpatial relationships:")
        for rel in scene.relationships:
            desc = f"- {rel.subject.name} is {rel.relation} {rel.object.name}"
            description_parts.append(desc)

        # Метрики и статистика
        if scene.metrics:
            description_parts.append("\nMetrics:")
            for metric_name, value in scene.metrics.items():
                description_parts.append(f"- {metric_name}: {value}")

        return "\n".join(description_parts)

    def run_bidirectional_demo(self):
        """
        Демонстрация двунаправленной коммуникации
        """
        print("=== AI → MMO Demo ===\n")

        # AI генерирует текст
        ai_output = """
        I'm creating a machine learning pipeline:
        1. Data collector is gathering 10000 samples from the database
        2. Preprocessor is cleaning the data (removing nulls, outliers)
        3. Feature engineer is creating 50 features
        4. Random Forest model (100 trees) is training on the data
        5. Validator is checking the model accuracy: 92%
        """

        print(f"AI Output:\n{ai_output}\n")

        # Преобразование в MMO сцену
        scene = self.translate_ai_output_to_scene(ai_output)
        print(f"MMO Scene created with {len(scene.characters)} characters")
        print(f"Characters: {[c.name for c in scene.characters]}\n")

        # Рендеринг сцены (ASCII для демо)
        rendered = self.mmo_engine.render_scene_ascii(scene)
        print("MMO Visual Representation:")
        print(rendered)

        print("\n=== MMO → AI Demo ===\n")

        # Визуальная сцена преобразуется обратно в текст
        scene_description = self.translate_scene_to_ai_input(scene)
        print(f"Scene Description for AI:\n{scene_description}\n")

        # AI анализирует сцену
        ai_analysis = self.ai_agents.analyze_scene(scene_description)
        print(f"AI Analysis:\n{ai_analysis}")
```

