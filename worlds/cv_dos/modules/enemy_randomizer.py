import struct
import random
from ..in_game_data import enemy_table, boss_list, global_item_table

base_enemy_address = 0x2078CAC
ENEMY_SIZE = 0x24

class EnemyData:
    """Represents complete enemy data structure"""
    OFFSET_COMMON_DROP = 8
    OFFSET_RARE_DROP = 10
    OFFSET_EXPERIENCE = 18
    OFFSET_SOUL_CHANCE = 20
    OFFSET_HP = 0  # Beispiel
    OFFSET_ATTACK = 2  # Beispiel
    OFFSET_DEFENSE = 4  # Beispiel
    OFFSET_MP = 6  # Beispiel

def randomize_all_enemies(world, rom):
    """
    Randomisiere ALLE Enemy-Parameter komplett
    """
    
    for enemy_name in enemy_table:
        # Bosses auslassen
        if enemy_name in boss_list:
            continue
        
        enemy_index = enemy_table.index(enemy_name)
        base_address = base_enemy_address + (enemy_index * ENEMY_SIZE)
        
        # === 1. STATS RANDOMISIEREN ===
        randomize_enemy_stats(world, rom, base_address)
        
        # === 2. DROPS RANDOMISIEREN ===
        randomize_enemy_drops(world, rom, base_address)
        
        # === 3. SOUL CHANCE RANDOMISIEREN ===
        randomize_soul_chance(world, rom, base_address)

def randomize_enemy_stats(world, rom, base_address):
    """Randomisiere HP, ATK, DEF, MP"""
    
    # HP lesen (2 Bytes bei Offset 0)
    hp = read_u16(rom, base_address + 0)
    # Neue HP: ±20% mit Min/Max Grenzen
    new_hp = int(hp * world.random.uniform(0.8, 1.2))
    new_hp = max(1, min(0xFFFF, new_hp))
    rom.write_to_file(base_address + 0, "arm9", struct.pack("H", new_hp))
    
    # ATK lesen (2 Bytes bei Offset 2)
    atk = read_u16(rom, base_address + 2)
    new_atk = int(atk * world.random.uniform(0.8, 1.2))
    new_atk = max(1, min(0xFFFF, new_atk))
    rom.write_to_file(base_address + 2, "arm9", struct.pack("H", new_atk))
    
    # DEF lesen (2 Bytes bei Offset 4)
    defense = read_u16(rom, base_address + 4)
    new_def = int(defense * world.random.uniform(0.8, 1.2))
    new_def = max(0, min(0xFFFF, new_def))
    rom.write_to_file(base_address + 4, "arm9", struct.pack("H", new_def))
    
    # MP lesen (2 Bytes bei Offset 6)
    mp = read_u16(rom, base_address + 6)
    new_mp = int(mp * world.random.uniform(0.7, 1.3))
    new_mp = max(0, min(0xFFFF, new_mp))
    rom.write_to_file(base_address + 6, "arm9", struct.pack("H", new_mp))

def randomize_enemy_drops(world, rom, base_address):
    """Randomisiere Common und Rare Drops"""
    
    drop_pool = [
        "Potion", "High Potion", "Super Potion",
        "Mind Up", "High Mind Up", "Mana Prism",
        "Anti-Venom", "Uncurse Potion"
    ]
    
    # Common Drop (Byte bei Offset 8)
    if world.random.randint(0, 99) < 45:
        common_item = world.random.choice(drop_pool)
        common_drop_id = global_item_table.index(common_item) + 1
    else:
        common_drop_id = 0
    
    rom.write_to_file(base_address + 8, "arm9", bytearray([common_drop_id]))
    
    # Rare Drop (Byte bei Offset 10)
    if world.random.randint(0, 99) < 29:
        rare_item = world.random.choice(drop_pool)
        rare_drop_id = global_item_table.index(rare_item) + 1
    else:
        rare_drop_id = 0
    
    rom.write_to_file(base_address + 10, "arm9", bytearray([rare_drop_id]))

def randomize_soul_chance(world, rom, base_address):
    """Randomisiere die Wahrscheinlichkeit, dass der Feind eine Seele droppt"""
    
    # Soul Chance lesen (1 Byte bei Offset 20)
    soul_chance = int.from_bytes(rom.read_from_file(base_address + 20, "arm9", 1))
    
    if soul_chance > 0:  # Nur wenn Feind Souls droppt
        # ±30% Variation
        new_chance = int(soul_chance * world.random.uniform(0.7, 1.3))
        new_chance = max(1, min(0xFF, new_chance))
        rom.write_to_file(base_address + 20, "arm9", bytearray([new_chance]))

def randomize_enemy_experience(world, rom, base_address):
    """Randomisiere EXP Rewards"""
    
    # EXP lesen (2 Bytes bei Offset 18)
    exp = read_u16(rom, base_address + 18)
    
    # ±25% Variation
    new_exp = int(exp * world.random.uniform(0.75, 1.25))
    new_exp = max(1, min(0xFFFF, new_exp))
    
    rom.write_to_file(base_address + 18, "arm9", struct.pack("H", new_exp))

def read_u16(rom, offset):
    """Hilfsfunktion zum Lesen eines 16-Bit Wertes"""
    data = rom.read_direct(offset, 2)
    return struct.unpack("<H", data)[0]
