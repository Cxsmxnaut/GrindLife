import json
import os
import random
import time

# --- Global Game Variables ---
SAVE_FILE = 'grindlife_mega_save.json'
PLAYER = {}
GAME_RUNNING = True # Control the main game loop

# --- Game Data Dictionaries (Expandable!) ---

# Jobs and their requirements/rewards
JOBS = {
    'Unemployed Loser 😭': {'min_age': 0, 'min_intel': 0, 'min_char': 0, 'earnings': (0, 0), 'happiness_cost': 0, 'health_cost': 0, 'energy_cost': 0, 'xp_gain': 0, 'skill_reqs': [], 'next_tier_req': {'intel': 40, 'char': 30, 'xp': 50}},
    'Lemonade Stand Mogul 🍋': {'min_age': 7, 'min_intel': 10, 'min_char': 10, 'earnings': (5, 15), 'happiness_cost': 2, 'health_cost': 1, 'energy_cost': 5, 'xp_gain': 5, 'skill_reqs': [], 'next_tier_req': None},
    'Fast Food Flipper 🍔': {'min_age': 16, 'min_intel': 20, 'min_char': 30, 'earnings': (50, 100), 'happiness_cost': 10, 'health_cost': 5, 'energy_cost': 15, 'xp_gain': 10, 'skill_reqs': [], 'next_tier_req': {'intel': 50, 'char': 50, 'xp': 100}},
    'Retail Renegade 🛍️': {'min_age': 18, 'min_intel': 40, 'min_char': 50, 'earnings': (150, 300), 'happiness_cost': 12, 'health_cost': 7, 'energy_cost': 20, 'xp_gain': 15, 'skill_reqs': ['Customer Service'], 'next_tier_req': {'intel': 60, 'char': 60, 'xp': 250}},
    'Coding Whiz 💻': {'min_age': 20, 'min_intel': 70, 'min_char': 40, 'earnings': (400, 800), 'happiness_cost': 15, 'health_cost': 8, 'energy_cost': 25, 'xp_gain': 25, 'skill_reqs': ['Programming'], 'next_tier_req': {'intel': 85, 'char': 50, 'xp': 500}},
    'Creative Director 🎨': {'min_age': 25, 'min_intel': 75, 'min_char': 80, 'earnings': (700, 1500), 'happiness_cost': 18, 'health_cost': 10, 'energy_cost': 30, 'xp_gain': 35, 'skill_reqs': ['Art', 'Leadership'], 'next_tier_req': {'intel': 90, 'char': 90, 'xp': 750}},
    'Medical Professional 🩺': {'min_age': 25, 'min_intel': 85, 'min_char': 70, 'earnings': (1000, 2500), 'happiness_cost': 20, 'health_cost': 15, 'energy_cost': 40, 'xp_gain': 45, 'skill_reqs': ['Medicine'], 'next_tier_req': None}, # Top tier for this path
    'Tech CEO 🤑': {'min_age': 30, 'min_intel': 95, 'min_char': 90, 'earnings': (2000, 5000), 'happiness_cost': 25, 'health_cost': 15, 'energy_cost': 50, 'xp_gain': 60, 'skill_reqs': ['Programming', 'Leadership', 'Business'], 'next_tier_req': None}, # Top tier
}

# Education levels and their requirements/benefits
EDUCATION_LEVELS = {
    'None': {'min_age': 0, 'intel_req': 0, 'bonus_intel': 0, 'bonus_charisma': 0, 'xp_gain': 0},
    'Elementary School 🎒': {'min_age': 5, 'intel_req': 0, 'bonus_intel': 5, 'bonus_charisma': 2, 'xp_gain': 20},
    'Middle School 📚': {'min_age': 11, 'intel_req': 20, 'bonus_intel': 10, 'bonus_charisma': 5, 'xp_gain': 40},
    'High School Diploma 🎓': {'min_age': 15, 'intel_req': 40, 'bonus_intel': 15, 'bonus_charisma': 8, 'xp_gain': 75},
    'College Degree 🏫': {'min_age': 18, 'intel_req': 70, 'bonus_intel': 25, 'bonus_charisma': 15, 'xp_gain': 150},
    'Graduate Degree 🧠': {'min_age': 22, 'intel_req': 85, 'bonus_intel': 35, 'bonus_charisma': 20, 'xp_gain': 300},
}

# Skills that can be learned
SKILLS = {
    'Programming': {'intel_req': 50, 'cost': 100, 'xp_gain': 50},
    'Customer Service': {'char_req': 40, 'cost': 50, 'xp_gain': 30},
    'Leadership': {'char_req': 60, 'cost': 200, 'xp_gain': 100},
    'Art': {'intel_req': 40, 'cost': 75, 'xp_gain': 40},
    'Medicine': {'intel_req': 70, 'cost': 300, 'xp_gain': 120},
    'Business': {'intel_req': 60, 'char_req': 60, 'cost': 150, 'xp_gain': 80},
}

# Hobbies and their benefits
HOBBIES = {
    'Reading 📖': {'happiness_gain': 10, 'intel_gain': 5, 'energy_cost': 5, 'money_cost': 5},
    'Gaming 🎮': {'happiness_gain': 15, 'intel_gain': 2, 'energy_cost': 10, 'money_cost': 10},
    'Hiking 🏞️': {'happiness_gain': 12, 'health_gain': 8, 'energy_cost': 15, 'money_cost': 0},
    'Cooking 🍳': {'happiness_gain': 8, 'health_gain': 5, 'intel_gain': 3, 'energy_cost': 10, 'money_cost': 15},
    'Gardening 🌱': {'happiness_gain': 10, 'health_gain': 5, 'energy_cost': 10, 'money_cost': 10},
    'Playing Music 🎸': {'happiness_gain': 15, 'charisma_gain': 5, 'energy_cost': 10, 'money_cost': 20},
}

# Housing options
HOUSING = {
    'Cardboard Box 🗑️': {'cost': 0, 'monthly_upkeep': 0, 'happiness_mod': -20},
    'Shared Dorm Room 🚪': {'cost': 0, 'monthly_upkeep': 100, 'happiness_mod': -5},
    'Small Apartment 🏢': {'cost': 50000, 'monthly_upkeep': 500, 'happiness_mod': 0},
    'Cozy House 🏡': {'cost': 200000, 'monthly_upkeep': 1500, 'happiness_mod': 15},
    'Luxury Penthouse 💎': {'cost': 1000000, 'monthly_upkeep': 5000, 'happiness_mod': 30},
}

# Vehicle options
VEHICLES = {
    'None 🚶': {'cost': 0, 'monthly_upkeep': 0, 'speed_mod': 0},
    'Rusty Bike 🚲': {'cost': 50, 'monthly_upkeep': 5, 'speed_mod': 5},
    'Used Sedan 🚗': {'cost': 5000, 'monthly_upkeep': 50, 'speed_mod': 15},
    'Sports Car 🏎️': {'cost': 50000, 'monthly_upkeep': 500, 'speed_mod': 30},
    'Private Jet ✈️': {'cost': 5000000, 'monthly_upkeep': 50000, 'speed_mod': 100},
}

# Shop items (consumables, skill books, fun items)
SHOP_ITEMS = {
    'Energy Drink ⚡': {'type': 'consumable', 'cost': 10, 'energy_gain': 20, 'happiness_mod': -2},
    'Healthy Snack 🍎': {'type': 'consumable', 'cost': 15, 'health_gain': 10, 'happiness_mod': 5},
    'Self-Help Book 📚': {'type': 'skill_book', 'cost': 50, 'skill_learned': 'Business', 'intel_gain': 5},
    'Art Supplies 🎨': {'type': 'skill_book', 'cost': 75, 'skill_learned': 'Art', 'happiness_gain': 5},
    'Movie Ticket 🍿': {'type': 'fun', 'cost': 20, 'happiness_gain': 15, 'energy_cost': 10},
    'Concert Ticket 🎤': {'type': 'fun', 'cost': 75, 'happiness_gain': 30, 'energy_cost': 20},
}

# Investment types
INVESTMENT_TYPES = {
    'Savings Account 🏦': {'min_money': 100, 'return_rate': 0.01, 'risk': 'low'}, # 1% annual return
    'Fictional Stocks 📈': {'min_money': 500, 'return_rate': 0.05, 'risk': 'medium'}, # 5% annual return, higher volatility
    'MemeCoin Crypto 🐶': {'min_money': 1000, 'return_rate': 0.15, 'risk': 'high'}, # 15% annual return, very high volatility
}

# Travel destinations
TRAVEL_DESTINATIONS = {
    'Local Park 🌳': {'cost': 0, 'happiness_gain': 10, 'health_gain': 5, 'energy_cost': 5},
    'City Museum 🏛️': {'cost': 30, 'happiness_gain': 15, 'intel_gain': 8, 'energy_cost': 10},
    'Tropical Beach 🏖️': {'cost': 500, 'happiness_gain': 40, 'health_gain': 15, 'energy_cost': 30},
    'Mountain Retreat ⛰️': {'cost': 700, 'happiness_gain': 35, 'health_gain': 20, 'energy_cost': 35},
    'Interstellar Cruise 🚀': {'cost': 100000, 'happiness_gain': 100, 'intel_gain': 20, 'energy_cost': 50},
}

# NPC names for relationships
NPC_NAMES = ["Alex", "Taylor", "Jordan", "Sam", "Casey", "Morgan", "Chris", "Jamie", "Pat"]

# Random events that can happen
RANDOM_EVENTS = [
    ("Good Day! ☀️", "You found a lucky penny!", {'money': 5, 'happiness': 2}, 0),
    ("Oops! 💥", "You tripped and scraped your knee.", {'health': -5, 'happiness': -3}, 0),
    ("Kind Gesture 🥰", "A stranger complimented your outfit!", {'happiness': 5, 'charisma': 1}, 0),
    ("Brain Boost! 💡", "You randomly learned a cool fact online.", {'intelligence': 3}, 0),
    ("Slight Cold 🤧", "You caught a minor cold, feeling a bit down.", {'health': -8, 'happiness': -5}, 0),
    ("Unexpected Gift! 🎁", "An old relative sent you some unexpected cash!", {'money': 50, 'happiness': 10}, 10), # Min age 10
    ("Community Project! 🌱", "You helped out with a local cleanup, feeling good about it.", {'happiness': 7, 'charisma': 2}, 12),
    ("Lost Item 😟", "You misplaced something important, causing a little stress.", {'happiness': -5, 'money': -10}, 15),
    ("New Interest! 🎨", "You discovered a new hobby that sparks your interest.", {'happiness': 5, 'intelligence': 2}, 10),
    ("Minor Setback 🚧", "A small plan didn't work out as expected.", {'happiness': -3}, 5),
    ("Promotion Opportunity! 📈", "Your boss noticed your hard work!", {'job_promo_chance': True}, 18), # Special flag for job logic
    ("Health Scare 🏥", "You had a minor health issue, but it passed.", {'health': -15, 'happiness': -10}, 30),
]

# --- Helper Functions ---
def _clamp(value, min_value, max_value):
    """Clamps a value between a minimum and maximum."""
    return max(min_value, min(value, max_value))

def _display_message_box(title, message):
    """Displays a custom message box instead of alert/confirm."""
    print("\n" + "=" * (len(title) + 6))
    print(f"||  {title}  ||")
    print("=" * (len(title) + 6))
    print(f"{message}\n")
    input("(Press Enter to continue...)") # User has to acknowledge
    print("-" * (len(title) + 6))

def save_game():
    """Saves the current player data to a JSON file."""
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(PLAYER, f, indent=4)
        _display_message_box("Game Saved! ✨", "Your journey continues! Don't forget to grind! 💾")
    except IOError as e:
        _display_message_box("ERROR! 🚨", f"Error saving game: {e}. Check file permissions! 😔")

def load_game():
    """Loads player data from a JSON file if it exists."""
    global PLAYER
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                PLAYER = json.load(f)
            # Ensure new stats are initialized for old saves
            PLAYER.setdefault('energy', 100)
            PLAYER.setdefault('debt', 0)
            PLAYER.setdefault('net_worth', 0)
            PLAYER.setdefault('skills', [])
            PLAYER.setdefault('inventory', {})
            PLAYER.setdefault('assets', {'housing': 'Cardboard Box 🗑️', 'vehicle': 'None 🚶'})
            PLAYER.setdefault('achievements', [])
            PLAYER.setdefault('xp', PLAYER.get('xp', 0)) # Ensure XP exists
            PLAYER.setdefault('rizz', PLAYER.get('rizz', 50)) # Ensure Rizz exists
            _display_message_box("Welcome Back! 🚀", f"Picking up where {PLAYER['name']} left off. Let's get this bread! �")
            return True
        except json.JSONDecodeError:
            _display_message_box("CORRUPTED SAVE! 🚫", "Corrupted save file detected. Starting a new game. 😢")
            return False
        except IOError as e:
            _display_message_box("ERROR! 🚨", f"Error loading game: {e}. Starting a new game. 😔")
            return False
    return False

def new_game():
    """Initializes a new player profile."""
    global PLAYER
    print("✨ Welcome to GrindLife™! Time to manifest your best life! ✨")
    name = input("What's your character's iconic name gonna be? 🤔 ").strip()
    while not name:
        name = input("A name is kinda important, fam! What is it? 🤔 ").strip()

    PLAYER = {
        'name': name,
        'age': 0, # Start at birth!
        'happiness': 70,
        'intelligence': 50,
        'charisma': 50,
        'health': 80,
        'energy': 100, # Max daily energy
        'xp': 0, # Experience points
        'rizz': 50, # Social charm
        'money': 100,
        'job': 'Unemployed Loser 😭',
        'education_level': 'None',
        'relationships': {}, # e.g., {'Mom': {'status': 'Family', 'bond': 80}, 'Friend A': {'status': 'Friend', 'bond': 60}}
        'skills': [],
        'inventory': {},
        'assets': {'housing': 'Cardboard Box 🗑️', 'vehicle': 'None 🚶'},
        'achievements': [],
        'debt': 0,
        'investments': {}, # {'Savings Account 🏦': 1000}
        'net_worth': 0 # Calculated on the fly
    }
    _display_message_box("New Life Started! 🍼", f"Welcome, {PLAYER['name']}! You're officially a certified freshie. Let the grind begin! 🌟")
    save_game()

def display_stats():
    """Shows all the player's current stats."""
    _calculate_net_worth() # Update net worth before displaying
    print("\n--- 📈 Your Current Vibe 📉 ---")
    print(f"👤 Name: {PLAYER['name']}")
    print(f"🎂 Age: {PLAYER['age']}")
    print(f"😊 Happiness: {_clamp(PLAYER['happiness'], 0, 100)}/100")
    print(f"🧠 Intelligence: {_clamp(PLAYER['intelligence'], 0, 100)}/100")
    print(f"💬 Charisma: {_clamp(PLAYER['charisma'], 0, 100)}/100")
    print(f"❤️ Health: {_clamp(PLAYER['health'], 0, 100)}/100")
    print(f"⚡ Energy: {_clamp(PLAYER['energy'], 0, 100)}/100 (daily actions)")
    print(f"🌟 XP: {PLAYER['xp']}")
    print(f"😏 Rizz: {PLAYER['rizz']}")
    print(f"💰 Money: ${PLAYER['money']:,}")
    print(f"💸 Debt: ${PLAYER['debt']:,}")
    print(f"💎 Net Worth: ${PLAYER['net_worth']:,}")
    print(f"💼 Job: {PLAYER['job']}")
    print(f"🎓 Education: {PLAYER['education_level']}")
    print(f"🏠 Housing: {PLAYER['assets']['housing']}")
    print(f"🚗 Vehicle: {PLAYER['assets']['vehicle']}")
    if PLAYER['skills']:
        print(f"🛠️ Skills: {', '.join(PLAYER['skills'])}")
    else:
        print("🛠️ Skills: Still building, fam!")
    if PLAYER['relationships']:
        print("🤝 Relationships:")
        for person, data in PLAYER['relationships'].items():
            print(f"    - {person} ({data['status']}): Bond {data['bond']}/100")
    else:
        print("🤝 Relationships: Solo dolo for now. 🤷‍♀️")
    if PLAYER['achievements']:
        print(f"🏆 Achievements: {', '.join(PLAYER['achievements'])}")
    else:
        print("🏆 Achievements: None yet! Get that clout! ✨")
    print("---------------------------------------")

def _adjust_stat(stat_name, amount, min_val=0, max_val=100):
    """Adjusts a player stat and clamps it within min/max values."""
    if stat_name == 'money' or stat_name == 'debt':
        PLAYER[stat_name] = max(0, PLAYER[stat_name] + amount)
    else:
        PLAYER[stat_name] = _clamp(PLAYER[stat_name] + amount, min_val, max_val)

def _calculate_net_worth():
    """Calculates player's net worth based on money, assets, and debt."""
    assets_value = PLAYER['money']
    current_housing = HOUSING.get(PLAYER['assets']['housing'])
    if current_housing:
        assets_value += current_housing['cost']
    current_vehicle = VEHICLES.get(PLAYER['assets']['vehicle'])
    if current_vehicle:
        assets_value += current_vehicle['cost']
    
    # Add investment values
    for inv_type, amount in PLAYER['investments'].items():
        assets_value += amount

    PLAYER['net_worth'] = assets_value - PLAYER['debt']

def _check_age_phase():
    """Returns the current life phase based on age."""
    age = PLAYER['age']
    if age < 5: return 'childhood'
    if age < 13: return 'elementary'
    if age < 18: return 'teenager'
    if age < 25: return 'young_adult'
    if age < 60: return 'adult'
    return 'senior'

def _spend_energy(amount):
    """Checks if player has enough energy and spends it."""
    if PLAYER['energy'] < amount:
        _display_message_box("Low Energy! 😴", "You're too tired, fam! Take a rest or grab an Energy Drink. ⚡")
        return False
    _adjust_stat('energy', -amount)
    return True

def _add_achievement(achievement_name):
    """Adds an achievement if not already earned."""
    if achievement_name not in PLAYER['achievements']:
        PLAYER['achievements'].append(achievement_name)
        _display_message_box("Achievement Unlocked! 🏆", f"You just earned: '{achievement_name}'! Get that clout! ✨")

# --- Core Game Mechanics ---
def apply_random_event():
    """Triggers a random event that impacts player stats or provides a choice."""
    if random.random() < 0.25: # 25% chance of a random event each turn
        available_events = [e for e in RANDOM_EVENTS if PLAYER['age'] >= e[3]]
        if not available_events: return

        event_title, event_message, stat_changes, _ = random.choice(available_events)
        _display_message_box(f"⚡ Random Event: {event_title} ⚡", event_message)

        for stat, change in stat_changes.items():
            if stat == 'job_promo_chance':
                _try_job_promotion() # Handle special job promotion event
                continue
            _adjust_stat(stat, change)
            print(f"  > {stat.capitalize()}: {'+' if change >= 0 else ''}{change}")
        time.sleep(1) # Pause to let player read the event

def _try_job_promotion():
    """Attempts to promote the player if conditions are met."""
    current_job_name = PLAYER['job']
    current_job_data = JOBS.get(current_job_name)

    if not current_job_data or not current_job_data.get('next_tier_req'):
        print("  > No higher tier job available for your current role. You're maxed out... for now. 🚀")
        return

    next_req = current_job_data['next_tier_req']
    if (PLAYER['intelligence'] >= next_req.get('intel', 0) and
        PLAYER['charisma'] >= next_req.get('char', 0) and
        PLAYER['xp'] >= next_req.get('xp', 0) and
        all(skill in PLAYER['skills'] for skill in next_req.get('skills', []))):

        # Find the next job in JOBS dictionary that matches the criteria
        promotable_jobs = []
        for job_name, job_data in JOBS.items():
            if job_name != current_job_name and job_data.get('min_age', 0) <= PLAYER['age']:
                # Simple check for jobs that are 'better' than current, could be more complex
                if job_data.get('earnings', (0,0))[0] > current_job_data.get('earnings', (0,0))[0]:
                    promotable_jobs.append((job_name, job_data))

        if promotable_jobs:
            # Pick one that meets actual requirements, not just 'next_tier_req'
            # For simplicity, let's just assume 'next_tier_req' implies the next step in a linear path
            # A more robust system would map jobs to specific tiers/paths
            next_job_found = False
            for potential_next_job_name, potential_next_job_data in JOBS.items():
                if potential_next_job_name == current_job_name:
                    # Find the 'next' job based on an assumed order or explicit links
                    # This requires a more structured JOBS dictionary or an explicit 'promotion_path'
                    # For now, let's just pick one that is generally 'better'
                    pass # This logic needs refinement to correctly map to a 'next' job

            # A simplified approach: If conditions are met, just assume a 'promotion' to a job higher up in the general earnings list
            # This is a placeholder for a more complex job tree.
            possible_promotions = [j_name for j_name, j_data in JOBS.items() if j_data['earnings'][0] > current_job_data['earnings'][0] and j_data['min_age'] <= PLAYER['age'] and PLAYER['intelligence'] >= j_data.get('min_intel',0) and PLAYER['charisma'] >= j_data.get('min_char',0)]
            if possible_promotions:
                new_job = random.choice(possible_promotions) # Simplistic promotion
                if new_job != PLAYER['job']:
                    PLAYER['job'] = new_job
                    _adjust_stat('happiness', 15)
                    _adjust_stat('xp', 50)
                    _display_message_box("PROMOTION ALERT! 🎉", f"You've been promoted to {PLAYER['job']}! Get that bag! 🚀")
                    return
    print("  > No promotion this time, fam. Keep grinding! 💪")


def check_game_over():
    """Checks for game over conditions."""
    global GAME_RUNNING
    if PLAYER['health'] <= 0:
        _display_message_box("Game Over! 💀", f"Your health hit rock bottom at age {PLAYER['age']}. You lived to be {PLAYER['age']} years old. RIP. 💔")
        GAME_RUNNING = False
        return True
    if PLAYER['happiness'] <= 0:
        _display_message_box("Game Over! 😩", f"You're completely miserable at age {PLAYER['age']}. Your spirit left the chat. 👻")
        GAME_RUNNING = False
        return True
    return False

def advance_time_and_stats():
    """Applies monthly expenses/income and resets energy for a new turn."""
    # Monthly upkeep for housing and vehicle
    housing_upkeep = HOUSING.get(PLAYER['assets']['housing'], {'monthly_upkeep': 0})['monthly_upkeep']
    vehicle_upkeep = VEHICLES.get(PLAYER['assets']['vehicle'], {'monthly_upkeep': 0})['monthly_upkeep']
    total_upkeep = housing_upkeep + vehicle_upkeep + random.randint(10, 50) # General living costs
    
    _adjust_stat('money', -total_upkeep)
    _adjust_stat('debt', total_upkeep * 0.1) # Small chance to incur debt if money is negative

    # Investment returns (annual, so apply scaled down per turn for simplicity)
    for inv_type, amount in PLAYER['investments'].items():
        rate = INVESTMENT_TYPES.get(inv_type, {'return_rate': 0})['return_rate']
        if random.random() < 0.7: # Simulate some volatility, not guaranteed every month
            _adjust_stat('money', int(amount * rate / 12)) # Approximate monthly return

    # Reset energy for the new turn
    PLAYER['energy'] = 100
    
    # Random stat decay
    _adjust_stat('happiness', -random.randint(1, 3))
    _adjust_stat('health', -random.randint(1, 2))


# --- Command Functions ---
def do_study():
    """Player studies to improve intelligence and potentially education."""
    if not _spend_energy(random.randint(10, 20)): return
    if PLAYER['age'] < 5:
        _display_message_box("Too Young! 👶", "You're too young to study, kiddo! Just play and be cute! 🧸")
        return
    if PLAYER['age'] > 60 and PLAYER['education_level'] == 'Graduate Degree 🧠':
        _display_message_box("Wisdom Unlocked! 🧘‍♀️", "You've got all the wisdom you need, time to relax! No more textbooks for you!")
        return

    intel_gain = random.randint(3, 8)
    happiness_cost = random.randint(5, 10)
    health_cost = random.randint(1, 3)
    money_cost = random.randint(10, 30)

    _adjust_stat('intelligence', intel_gain)
    _adjust_stat('happiness', -happiness_cost)
    _adjust_stat('health', -health_cost)
    _adjust_stat('money', -money_cost)

    _display_message_box("Brain Gains! 🧠", f"You hit the books hard! Your brain feels bigger!\n"
                         f"  > Intelligence +{intel_gain}\n"
                         f"  > Happiness -{happiness_cost} (studying can be tough!)\n"
                         f"  > Health -{health_cost} (all-nighters, maybe?)\n"
                         f"  > Money -{money_cost} (for those brain fuel snacks!)")

    # Education progression
    current_edu_level_data = EDUCATION_LEVELS.get(PLAYER['education_level'])
    next_edu_level_name = None
    if PLAYER['education_level'] == 'None' and PLAYER['age'] >= EDUCATION_LEVELS['Elementary School 🎒']['min_age']:
        next_edu_level_name = 'Elementary School 🎒'
    elif PLAYER['education_level'] == 'Elementary School 🎒' and PLAYER['age'] >= EDUCATION_LEVELS['Middle School 📚']['min_age']:
        next_edu_level_name = 'Middle School 📚'
    elif PLAYER['education_level'] == 'Middle School 📚' and PLAYER['age'] >= EDUCATION_LEVELS['High School Diploma 🎓']['min_age']:
        next_edu_level_name = 'High School Diploma 🎓'
    elif PLAYER['education_level'] == 'High School Diploma 🎓' and PLAYER['age'] >= EDUCATION_LEVELS['College Degree 🏫']['min_age'] and PLAYER['intelligence'] >= EDUCATION_LEVELS['College Degree 🏫']['intel_req']:
        next_edu_level_name = 'College Degree 🏫'
    elif PLAYER['education_level'] == 'College Degree 🏫' and PLAYER['age'] >= EDUCATION_LEVELS['Graduate Degree 🧠']['min_age'] and PLAYER['intelligence'] >= EDUCATION_LEVELS['Graduate Degree 🧠']['intel_req']:
        next_edu_level_name = 'Graduate Degree 🧠'

    if next_edu_level_name and PLAYER['education_level'] != next_edu_level_name:
        PLAYER['education_level'] = next_edu_level_name
        edu_bonus = EDUCATION_LEVELS[next_edu_level_name]
        _adjust_stat('intelligence', edu_bonus['bonus_intel'])
        _adjust_stat('charisma', edu_bonus['bonus_charisma'])
        _adjust_stat('xp', edu_bonus['xp_gain'])
        _display_message_box("Graduation! 🎓", f"Congrats! You've advanced to {PLAYER['education_level']}! Keep that brain sharp! ✨")
        if PLAYER['education_level'] == 'High School Diploma 🎓': _add_achievement("High School Grad")
        if PLAYER['education_level'] == 'College Degree 🏫': _add_achievement("College Grad")
        if PLAYER['education_level'] == 'Graduate Degree 🧠': _add_achievement("Big Brain Energy")


def do_work():
    """Player works to earn money, potentially impacting health and happiness, and affecting job progression."""
    if not _spend_energy(JOBS.get(PLAYER['job'], {'energy_cost': 20})['energy_cost']): return

    if PLAYER['age'] < JOBS['Fast Food Flipper 🍔']['min_age']:
        _display_message_box("Too Young! 🚫", "You're too young to legally work, buddy! Stick to playing for now. 👶")
        return
    if PLAYER['health'] < 30:
        _display_message_box("Too Unwell! 🤕", "Your health is too low to work effectively right now. Rest up! 😴")
        return

    job_data = JOBS.get(PLAYER['job'])
    if not job_data or job_data['earnings'] == (0, 0):
        _display_message_box("No Job! 🤷‍♀️", "You don't have a proper job, fam! Use 'job search' to find one!")
        return

    earnings = random.randint(job_data['earnings'][0], job_data['earnings'][1])
    happiness_cost = job_data['happiness_cost']
    health_cost = job_data['health_cost']
    xp_gain = job_data['xp_gain']

    _adjust_stat('money', earnings)
    _adjust_stat('happiness', -happiness_cost)
    _adjust_stat('health', -health_cost)
    _adjust_stat('xp', xp_gain)

    _display_message_box("Work Done! 💼", f"You put in a good shift as a {PLAYER['job']}!\n"
                         f"  > Earned: ${earnings:,} 💰\n"
                         f"  > Happiness: -{happiness_cost}\n"
                         f"  > Health: -{health_cost}\n"
                         f"  > XP: +{xp_gain}")

    # Job progression check after working
    current_job_data = JOBS.get(PLAYER['job'])
    if current_job_data and current_job_data.get('next_tier_req'):
        next_req = current_job_data['next_tier_req']
        if (PLAYER['intelligence'] >= next_req.get('intel', 0) and
            PLAYER['charisma'] >= next_req.get('char', 0) and
            PLAYER['xp'] >= next_req.get('xp', 0) and
            all(skill in PLAYER['skills'] for skill in next_req.get('skills', []))):
            
            # Find the actual next job by iterating through JOBS and checking if it's the logical next step
            # This is a simplified linear progression for now.
            promotion_options = []
            for job_name, data in JOBS.items():
                if data.get('min_age', 0) <= PLAYER['age'] and data.get('earnings')[0] > current_job_data['earnings'][0]:
                    if data.get('min_intel', 0) <= PLAYER['intelligence'] and \
                       data.get('min_char', 0) <= PLAYER['charisma'] and \
                       data.get('xp_gain', 0) > current_job_data.get('xp_gain', 0): # Simple heuristic for 'better' job
                        promotion_options.append(job_name)

            if promotion_options:
                new_job = random.choice(promotion_options) # Pick a random 'better' job
                if new_job != PLAYER['job']:
                    PLAYER['job'] = new_job
                    _adjust_stat('happiness', 15)
                    _adjust_stat('xp', 50)
                    _display_message_box("PROMOTION ALERT! 🎉", f"You've been promoted to {PLAYER['job']}! Get that bag! 🚀")
                    if PLAYER['job'] == 'Tech CEO 🤑': _add_achievement("GrindLife Boss")
            else:
                print("  > No promotion opportunities right now, fam. Keep grinding! 💪")
        else:
            print("  > Not quite ready for the next level yet. Keep building those stats! 📈")
    else:
        print("  > You're at the top of your current career path! Time to explore new horizons? 🤔")

def do_job_search():
    """Allows player to search for and apply to jobs."""
    if PLAYER['age'] < 16:
        _display_message_box("Too Young! 🚫", "You're too young to search for jobs, buddy! Enjoy your childhood. 👶")
        return

    print("\n--- 💼 Job Board 💼 ---")
    available_jobs = []
    for job_name, data in JOBS.items():
        if job_name == 'Unemployed Loser 😭': continue
        if PLAYER['age'] >= data['min_age'] and \
           PLAYER['intelligence'] >= data['min_intel'] and \
           PLAYER['charisma'] >= data['min_char'] and \
           PLAYER['xp'] >= data.get('xp_gain', 0) and \
           all(skill in PLAYER['skills'] for skill in data['skill_reqs']):
            
            # Check if this job is 'better' than current, or if current is unemployed
            if PLAYER['job'] == 'Unemployed Loser 😭' or (data['earnings'][0] > JOBS.get(PLAYER['job'], {'earnings':(0,0)})['earnings'][0]):
                available_jobs.append(job_name)
                print(f"- {job_name} (Req: Intel {data['min_intel']}, Charisma {data['min_char']}, XP {data.get('xp_gain', 0)}, Skills: {', '.join(data['skill_reqs']) if data['skill_reqs'] else 'None'})")

    if not available_jobs:
        _display_message_box("No Openings! 😩", "No jobs available for you right now, fam. Level up your stats! 📈")
        return

    choice = input("Which job you tryna apply for? (type full name or 'cancel') 🤔 ").strip().title()
    if choice.lower() == 'cancel':
        print("Okay, no job hunt today. 🚶‍♀️")
        return

    if choice in available_jobs:
        PLAYER['job'] = choice
        _adjust_stat('happiness', 10)
        _display_message_box("New Job! 🎉", f"Congrats! You just landed the gig as a {PLAYER['job']}! Time to secure the bag! 💼")
    else:
        _display_message_box("Job Not Found! 🧐", "That job ain't on the board or you're not qualified, fam. Check your spelling or stats! 🤷‍♀️")


def do_socialize():
    """Player socializes to improve charisma and happiness, and build relationships."""
    if not _spend_energy(random.randint(10, 20)): return
    if PLAYER['age'] < 5:
        _display_message_box("Tiny Talk! 👶", "You're socializing by gurgling at toys right now! Keep at it, champ! 🧸")
        return

    char_gain = random.randint(3, 8)
    happiness_gain = random.randint(5, 15)
    money_cost = random.randint(5, 20) # Going out costs money

    _adjust_stat('charisma', char_gain)
    _adjust_stat('happiness', happiness_gain)
    _adjust_stat('money', -money_cost)

    _display_message_box("Good Vibes! 😊", f"You hung out with friends/family! Good vibes all around!\n"
                         f"  > Charisma +{char_gain}\n"
                         f"  > Happiness +{happiness_gain}\n"
                         f"  > Money -{money_cost} (for coffee, movies, etc.)")

    # Relationship building
    if random.random() < 0.4: # Chance to interact with an NPC
        npc_name = random.choice(NPC_NAMES)
        if npc_name not in PLAYER['relationships']:
            # New relationship
            PLAYER['relationships'][npc_name] = {'status': 'Acquaintance', 'bond': 20}
            _display_message_box("New Connection! 🤝", f"You just met {npc_name}! A new acquaintance has entered your life! 🎉")
        else:
            # Strengthen existing relationship
            bond_gain = random.randint(5, 15)
            PLAYER['relationships'][npc_name]['bond'] = _clamp(PLAYER['relationships'][npc_name]['bond'] + bond_gain, 0, 100)
            if PLAYER['relationships'][npc_name]['bond'] >= 70 and PLAYER['relationships'][npc_name]['status'] == 'Acquaintance':
                PLAYER['relationships'][npc_name]['status'] = 'Friend'
                _display_message_box("Friendship Leveled Up! 💖", f"{npc_name} is now your good friend! Squad goals! 👯")
                _add_achievement("True Friend")
            else:
                print(f"  > You strengthened your bond with {npc_name}! Bond: {PLAYER['relationships'][npc_name]['bond']}/100 💪")

def do_exercise():
    """Player exercises to improve health and happiness."""
    if not _spend_energy(random.randint(10, 25)): return
    if PLAYER['age'] < 5:
        _display_message_box("Tiny Workout! 👶", "You're exercising by crawling around! Keep those tiny muscles strong! 🍼")
        return
    if PLAYER['health'] < 20:
        _display_message_box("Too Unwell! ⚠️", "You're too unwell to exercise! Prioritize rest and recovery. 🏥")
        return

    health_gain = random.randint(5, 12)
    happiness_gain = random.randint(3, 8)
    money_cost = random.randint(0, 10) # Maybe gym fees or equipment

    _adjust_stat('health', health_gain)
    _adjust_stat('happiness', happiness_gain)
    _adjust_stat('money', -money_cost)

    _display_message_box("Gains! 💪", f"You got your sweat on! Feeling stronger and healthier!\n"
                         f"  > Health +{health_gain}\n"
                         f"  > Happiness +{happiness_gain} (endorphins, baby!)\n"
                         f"  > Money -{money_cost} (for that sweet gym membership!)")
    if PLAYER['health'] >= 90: _add_achievement("Health Nut")

def do_shop():
    """Lets the player buy items from the shop."""
    print("\n--- 🛍️ GrindLife Marketplace 🛍️ ---")
    print("Available items:")
    for item_name, data in SHOP_ITEMS.items():
        print(f"  - {item_name} (Cost: ${data['cost']:,})")
        if data['type'] == 'consumable':
            print(f"    Effect: Energy +{data.get('energy_gain',0)}, Health +{data.get('health_gain',0)}, Happiness {data.get('happiness_mod',0):+}")
        elif data['type'] == 'skill_book':
            print(f"    Effect: Learn '{data['skill_learned']}', Intel +{data.get('intel_gain',0)}")
        elif data['type'] == 'fun':
            print(f"    Effect: Happiness +{data.get('happiness_gain',0)}, Energy -{data.get('energy_cost',0)}")
    print("-----------------------------------")

    choice = input("What are you copping today, fam? (type full name or 'cancel') 🤔 ").strip().title()
    if choice.lower() == 'cancel':
        print("Aight, maybe next time! 👋")
        return

    item_data = SHOP_ITEMS.get(choice)
    if not item_data:
        _display_message_box("Not Found! 🤷‍♀️", "That item ain't on the shelves, fam. Check your spelling! 🧐")
        return

    if PLAYER['money'] < item_data['cost']:
        _display_message_box("Broke Alert! 💸", f"You're too broke to buy the {choice}. Get your money up! 💰")
        return

    # Process purchase
    PLAYER['money'] -= item_data['cost']
    if item_data['type'] == 'consumable':
        _adjust_stat('energy', item_data.get('energy_gain', 0))
        _adjust_stat('health', item_data.get('health_gain', 0))
        _adjust_stat('happiness', item_data.get('happiness_mod', 0))
        _display_message_box("Purchased! ✅", f"You used the {choice}! Feeling the effects! ⚡")
    elif item_data['type'] == 'skill_book':
        skill = item_data['skill_learned']
        if skill not in PLAYER['skills']:
            PLAYER['skills'].append(skill)
            _adjust_stat('intelligence', item_data.get('intel_gain', 0))
            _display_message_box("New Skill Unlocked! 🛠️", f"You learned '{skill}' from the {choice}! Your brain is expanding! 🧠")
            if skill == 'Programming': _add_achievement("Code Master")
        else:
            _display_message_box("Already Got It! 😅", f"You already know '{skill}', fam! Find a new book! 📚")
    elif item_data['type'] == 'fun':
        _adjust_stat('happiness', item_data.get('happiness_gain', 0))
        _adjust_stat('energy', -item_data.get('energy_cost', 0))
        _display_message_box("Good Times! 🎉", f"Enjoyed the {choice}! Good vibes acquired! 😄")

    save_game()

def do_housing():
    """Allows player to buy/upgrade housing."""
    print("\n--- 🏠 Housing Market 🏠 ---")
    print("Available Homes:")
    for house_type, data in HOUSING.items():
        print(f"  - {house_type} (Cost: ${data['cost']:,}) - Monthly Upkeep: ${data['monthly_upkeep']:,} - Happiness Mod: {data['happiness_mod']:+}")
    print("----------------------------")

    current_house = PLAYER['assets']['housing']
    print(f"Your current home: {current_house}")

    choice = input("Which crib you tryna move into? (type full name or 'cancel') 🤔 ").strip().title()
    if choice.lower() == 'cancel':
        print("Staying put for now. 🤷‍♀️")
        return

    if choice not in HOUSING:
        _display_message_box("Not Found! 🏡", "That crib ain't on the market, fam. Check your spelling! 🧐")
        return

    new_house_data = HOUSING[choice]
    if PLAYER['money'] < new_house_data['cost']:
        _display_message_box("Broke Alert! 💸", f"You can't afford the {choice}. Get your money up! 💰")
        return

    if new_house_data['cost'] > HOUSING[current_house]['cost']: # Only allow upgrading, not downgrading via this command
        PLAYER['money'] -= new_house_data['cost']
        PLAYER['assets']['housing'] = choice
        _adjust_stat('happiness', new_house_data['happiness_mod'])
        _display_message_box("New Home! 🎉", f"You just copped the {choice}! Living that dream! 🏡")
        if choice == 'Luxury Penthouse 💎': _add_achievement("Luxury Living")
        save_game()
    else:
        _display_message_box("No Upgrade! 😅", "You can't move into a lesser crib or the same one this way, fam! Go big or go home (literally!). 📈")


def do_vehicle():
    """Allows player to buy/upgrade vehicles."""
    print("\n--- 🚗 Vehicle Dealership 🚗 ---")
    print("Available Rides:")
    for vehicle_type, data in VEHICLES.items():
        print(f"  - {vehicle_type} (Cost: ${data['cost']:,}) - Monthly Upkeep: ${data['monthly_upkeep']:,}")
    print("--------------------------------")

    current_vehicle = PLAYER['assets']['vehicle']
    print(f"Your current ride: {current_vehicle}")

    choice = input("Which ride you tryna cop? (type full name or 'cancel') 🤔 ").strip().title()
    if choice.lower() == 'cancel':
        print("Walking it is. 🚶")
        return

    if choice not in VEHICLES:
        _display_message_box("Not Found! 🏎️", "That whip ain't on the lot, fam. Check your spelling! 🧐")
        return

    new_vehicle_data = VEHICLES[choice]
    if PLAYER['money'] < new_vehicle_data['cost']:
        _display_message_box("Broke Alert! 💸", f"You can't afford the {choice}. Get your money up! 💰")
        return

    if new_vehicle_data['cost'] > VEHICLES[current_vehicle]['cost']: # Only allow upgrading
        PLAYER['money'] -= new_vehicle_data['cost']
        PLAYER['assets']['vehicle'] = choice
        _display_message_box("New Ride! 🚗", f"You just copped the {choice}! Zoom zoom! 💨")
        if choice == 'Private Jet ✈️': _add_achievement("High Flyer")
        save_game()
    else:
        _display_message_box("No Upgrade! 😅", "You can't buy a lesser ride or the same one this way, fam! Gotta level up! 📈")

def do_invest():
    """Allows player to make investments."""
    print("\n--- 🏦 Investment Opportunities 📈 ---")
    for inv_type, data in INVESTMENT_TYPES.items():
        print(f"  - {inv_type} (Min: ${data['min_money']:,}) - Avg. Return: {data['return_rate'] * 100:.0f}% - Risk: {data['risk'].capitalize()}")
    print("-------------------------------------")
    if PLAYER['investments']:
        print("Your current investments:")
        for inv_type, amount in PLAYER['investments'].items():
            print(f"  - {inv_type}: ${amount:,}")
    else:
        print("You got no investments yet. Get that passive income! 😴")

    choice_type = input("What type of investment are you looking into? (e.g., 'Savings Account', 'Fictional Stocks', 'MemeCoin Crypto' or 'cancel') 🤔 ").strip().title()
    if choice_type.lower() == 'cancel':
        print("No investments today. 🤷‍♀️")
        return
    
    if choice_type not in INVESTMENT_TYPES:
        _display_message_box("Invalid Type! 🚫", "That's not a recognized investment type, fam. 🧐")
        return
    
    investment_data = INVESTMENT_TYPES[choice_type]
    
    try:
        amount = int(input(f"How much you tryna invest in {choice_type}? (Min: ${investment_data['min_money']:,}, or 'cancel') 🤔 "))
        if amount <= 0: raise ValueError
    except ValueError:
        print("Invalid amount, fam. Must be a positive number. 🔢")
        return

    if amount < investment_data['min_money']:
        _display_message_box("Too Small! 💸", f"You gotta invest at least ${investment_data['min_money']:,} in {choice_type}. 📈")
        return
    if PLAYER['money'] < amount:
        _display_message_box("Broke Alert! 🚨", f"You don't have ${amount:,} to invest, fam. 💰")
        return

    PLAYER['money'] -= amount
    PLAYER['investments'][choice_type] = PLAYER['investments'].get(choice_type, 0) + amount
    _display_message_box("Investment Made! 💰", f"You invested ${amount:,} in {choice_type}! Let that money make money! 🤑")
    _add_achievement("Investor Extraordinaire")
    save_game()

def do_travel():
    """Allows player to travel to destinations."""
    if not _spend_energy(random.randint(20, 50)): return
    print("\n--- ✈️ Travel Destinations 🌴 ---")
    for dest, data in TRAVEL_DESTINATIONS.items():
        print(f"  - {dest} (Cost: ${data['cost']:,}) - Happiness +{data['happiness_gain']} - Health +{data['health_gain']}")
    print("-------------------------------")

    choice = input("Where you tryna jet off to, fam? (type full name or 'cancel') 🤔 ").strip().title()
    if choice.lower() == 'cancel':
        print("Staying local today. 🚶‍♀️")
        return

    destination_data = TRAVEL_DESTINATIONS.get(choice)
    if not destination_data:
        _display_message_box("Unknown Destination! 🗺️", "That place ain't on the map, fam. 🧐")
        return

    if PLAYER['money'] < destination_data['cost']:
        _display_message_box("Broke Alert! 💸", f"You can't afford a trip to {choice}. Get that travel money! 💰")
        return
    
    PLAYER['money'] -= destination_data['cost']
    _adjust_stat('happiness', destination_data['happiness_gain'])
    _adjust_stat('health', destination_data['health_gain'])
    _adjust_stat('intelligence', destination_data.get('intel_gain', 0)) # Some travel might boost intel too

    _display_message_box("Vacation Mode! 🏖️", f"You just traveled to {choice}! Feeling refreshed and vibing! ☀️")
    if choice == 'Interstellar Cruise 🚀': _add_achievement("Space Tourist")
    save_game()

def do_hobby():
    """Allows player to engage in a hobby."""
    if not _spend_energy(random.randint(10, 30)): return
    print("\n--- 🎨 Hobby Hub 🧩 ---")
    for hobby, data in HOBBIES.items():
        print(f"  - {hobby} (Cost: ${data['money_cost']:,}) - Happiness +{data['happiness_gain']} - Intel +{data.get('intel_gain',0)} - Health +{data.get('health_gain',0)}")
    print("----------------------")

    choice = input("Which hobby are you feeling today? (type full name or 'cancel') 🤔 ").strip().title()
    if choice.lower() == 'cancel':
        print("No hobby vibes today. 😴")
        return

    hobby_data = HOBBIES.get(choice)
    if not hobby_data:
        _display_message_box("Unknown Hobby! 🤷‍♀️", "That's not a recognized hobby, fam. 🧐")
        return

    if PLAYER['money'] < hobby_data['money_cost']:
        _display_message_box("Broke Alert! 💸", f"You can't afford to do {choice}. Get your funds up! 💰")
        return
    
    PLAYER['money'] -= hobby_data['money_cost']
    _adjust_stat('happiness', hobby_data['happiness_gain'])
    _adjust_stat('intelligence', hobby_data.get('intel_gain', 0))
    _adjust_stat('health', hobby_data.get('health_gain', 0))
    _adjust_stat('charisma', hobby_data.get('charisma_gain', 0))

    _display_message_box("Hobby Time! 🎉", f"You spent some quality time {choice}! Feeling good! 😄")
    if PLAYER['happiness'] >= 95: _add_achievement("Vibe King/Queen")
    save_game()

def do_relationships():
    """Manages interactions with NPCs."""
    if not _spend_energy(random.randint(5, 15)): return
    if not PLAYER['relationships']:
        _display_message_box("No Connections! 😔", "You haven't made any relationships yet! Use 'socialize' to meet people. 🤝")
        return

    print("\n--- 🤝 Your Connections 💖 ---")
    for person, data in PLAYER['relationships'].items():
        print(f"  - {person} ({data['status']}): Bond {data['bond']}/100")
    print("---------------------------------")

    choice_person = input("Who do you wanna interact with? (type name or 'cancel') 🤔 ").strip().title()
    if choice_person.lower() == 'cancel':
        print("Okay, maybe later. 🚶‍♀️")
        return

    if choice_person not in PLAYER['relationships']:
        _display_message_box("Not Found! 🤷‍♀️", "That person isn't in your contacts, fam. Check your spelling! 🧐")
        return

    _display_message_box(f"Interacting with {choice_person}", "What's the vibe?\n1. Chat 💬\n2. Give Gift 🎁 (cost: $20)\n3. Ask for Advice 🧠")
    action_choice = input("Your move? 🤔 ").strip()

    relationship_data = PLAYER['relationships'][choice_person]
    bond_change = 0
    happiness_change = 0
    money_change = 0

    if action_choice == '1': # Chat
        bond_change = random.randint(3, 8)
        happiness_change = random.randint(2, 5)
        _display_message_box("Chatting! 💬", f"You had a good convo with {choice_person}! Vibe check: positive! ✨")
    elif action_choice == '2': # Give Gift
        if PLAYER['money'] < 20:
            _display_message_box("Broke! 💸", "You can't afford a gift right now, fam. 😩")
            return
        money_change = -20
        bond_change = random.randint(10, 25)
        happiness_change = random.randint(5, 10)
        _display_message_box("Gift Giving! 🎁", f"You gave {choice_person} a gift! They loved it! 🥰")
    elif action_choice == '3': # Ask for Advice
        intel_gain = random.randint(5, 15) if relationship_data['bond'] >= 50 else random.randint(1, 5)
        _adjust_stat('intelligence', intel_gain)
        happiness_change = random.randint(0, 5)
        _display_message_box("Seeking Wisdom! 🧠", f"{choice_person} gave you some solid advice! Intellect boost! 💡")
    else:
        _display_message_box("Invalid Choice! 🤷‍♀️", "That wasn't an option, fam. Try again. 🧐")
        return

    relationship_data['bond'] = _clamp(relationship_data['bond'] + bond_change, 0, 100)
    _adjust_stat('happiness', happiness_change)
    _adjust_stat('money', money_change)

    print(f"  > {choice_person}'s bond: {relationship_data['bond']}/100")
    if relationship_data['bond'] >= 80 and relationship_data['status'] == 'Friend':
        relationship_data['status'] = 'Best Friend'
        _display_message_box("Bestie Status! 💖", f"{choice_person} is now your BEST FRIEND! You loyal! ✨")
        _add_achievement("Ultimate Bestie")
    save_game()


def show_achievements():
    """Displays player's earned achievements."""
    print("\n--- 🏆 Your Clout List (Achievements) 🏆 ---")
    if PLAYER['achievements']:
        for achievement in PLAYER['achievements']:
            print(f"- {achievement}")
    else:
        print("No achievements unlocked yet! Get to grinding, fam! 💪")
    print("------------------------------------------")

def show_inventory():
    """Displays player's inventory (currently unused but planned for future item types)."""
    print("\n--- 🎒 Your Backpack 🎒 ---")
    if PLAYER['inventory']:
        for item, quantity in PLAYER['inventory'].items():
            print(f"- {item}: {quantity}")
    else:
        print("Your backpack is empty, fam. Fill it up! 🛍️")
    print("---------------------------")

def show_net_worth():
    """Displays player's calculated net worth."""
    _calculate_net_worth()
    _display_message_box("Your Financial Flex! 🤑", f"Your current Net Worth: ${PLAYER['net_worth']:,} 💎")


def show_help():
    """Displays a list of all available commands."""
    print("\n--- 📚 GrindLife™ Commands (Know Your Hustle) 📚 ---")
    print("  stats     → Show all your player stats. 📈")
    print("  age       → Increase age by 1 year, see life changes. 🎂")
    print("  study     → Go to school/learn to improve intelligence. 🧠")
    print("  work      → Earn money from your job, get XP. 💼")
    print("  job search→ Look for new job opportunities. 🔎")
    print("  socialize → Hang out, improve charisma and happiness, build bonds. 😊")
    print("  exercise  → Work out, boost health and happiness. 💪")
    print("  shop      → Buy consumables, skill books, and fun items. 🛍️")
    print("  housing   → Buy or upgrade your home. 🏠")
    print("  vehicle   → Buy or upgrade your ride. 🚗")
    print("  invest    → Put your money to work (fictional investments!). 📈")
    print("  travel    → Explore new places, gain happiness/stats. ✈️")
    print("  hobby     → Engage in leisure activities. 🎨")
    print("  relate    → Interact with your friends and family. 💖")
    print("  achieve   → See your unlocked achievements. 🏆")
    print("  inventory → Check your items (future feature!). 🎒")
    print("  net worth → See your financial standing. 💎")
    print("  help      → You're literally using it right now, but here it is! 🤯")
    print("  exit      → Save your game and quit. Don't be a stranger! 👋")
    print("-------------------------------------------------")

# --- Main Game Loop ---
def game_loop():
    """The main loop for the game."""
    global GAME_RUNNING
    if not load_game():
        new_game()

    while GAME_RUNNING:
        _calculate_net_worth() # Recalculate net worth each turn
        print(f"\n--- 🎮 GrindLife™ - Age: {PLAYER['age']} | Money: ${PLAYER['money']:,} | Happiness: {PLAYER['happiness']}% | Energy: {PLAYER['energy']}% ---")
        command = input(f"What's the move, {PLAYER['name']}? (type 'help' for commands) 👉 ").lower().strip()
        print("--------------------------------------------------------------------------------------")

        # Command mapping
        if command == 'age':
            do_age()
            if not GAME_RUNNING: break # Check if game over after aging
            advance_time_and_stats()
        elif command == 'study':
            do_study()
        elif command == 'work':
            do_work()
        elif command == 'job search':
            do_job_search()
        elif command == 'socialize':
            do_socialize()
        elif command == 'exercise':
            do_exercise()
        elif command == 'shop':
            do_shop()
        elif command == 'housing':
            do_housing()
        elif command == 'vehicle':
            do_vehicle()
        elif command == 'invest':
            do_invest()
        elif command == 'travel':
            do_travel()
        elif command == 'hobby':
            do_hobby()
        elif command == 'relate':
            do_relationships()
        elif command == 'achieve':
            show_achievements()
        elif command == 'inventory':
            show_inventory()
        elif command == 'net worth':
            show_net_worth()
        elif command == 'stats':
            display_stats()
        elif command == 'help':
            show_help()
        elif command == 'exit':
            save_game()
            _display_message_box("Peace Out! 👋", "Thanks for grinding! See you next time! ✌️")
            GAME_RUNNING = False
            break
        else:
            _display_message_box("Huh? 🚫", "That command ain't it, chief. Try 'help' for the real moves. 🤷‍♀️")

        apply_random_event() # Apply random event after each command
        if check_game_over(): # Check game over conditions
            break
        
        time.sleep(1) # Small delay for better readability and "turn-based" feel

# --- Run the Game ---
if __name__ == "__main__":
    game_loop()