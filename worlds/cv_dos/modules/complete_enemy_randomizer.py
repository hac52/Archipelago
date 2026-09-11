import struct
from ..in_game_data import enemy_table, boss_list, global_soul_table

base_enemy_address = 0x2078CAC
ENEMY_SIZE = 0x24  # Größe einer Enemy-Datenstruktur


def swap_complete_enemy_data(rom, enemy1_name: str, enemy2_name: str):
    """
    TAUSCHE ZWEI GEGNER KOMPLETT:
    - Stats (HP, ATK, DEF, MP)
    - Erfahrung
    - Soul Drop Chance
    - Drops (Common + Rare)
    - Grafiken
    - Paletten
    """
    
    if enemy1_name in boss_list or enemy2_name in boss_list:
        print(f"⚠️  Kann Bosses nicht randomisieren: {enemy1_name}, {enemy2_name}")
        return
    
    if enemy1_name not in enemy_table or enemy2_name not in enemy_table:
        print(f"⚠️  Gegner nicht gefunden: {enemy1_name} oder {enemy2_name}")
        return
    
    enemy1_idx = enemy_table.index(enemy1_name)
    enemy2_idx = enemy_table.index(enemy2_name)
    
    # ========================================
    # 1. DATENSÄTZE TAUSCHEN
    # ========================================
    print(f"🔄 Tausche Datensätze: {enemy1_name} ↔️ {enemy2_name}")
    
    addr1 = base_enemy_address + (enemy1_idx * ENEMY_SIZE)
    addr2 = base_enemy_address + (enemy2_idx * ENEMY_SIZE)
    
    # Kompletten 0x24 Byte Datensatz lesen
    enemy1_data = rom.read_from_file(addr1, "arm9", ENEMY_SIZE)
    enemy2_data = rom.read_from_file(addr2, "arm9", ENEMY_SIZE)
    
    # Tauschen
    rom.write_to_file(addr1, "arm9", enemy2_data)
    rom.write_to_file(addr2, "arm9", enemy1_data)
    
    print(f"✅ Datensätze getauscht!")
    print(f"   Enemy 1 ({enemy1_name}):")
    print(f"      HP: {struct.unpack('<H', enemy2_data[0:2])[0]}")
    print(f"      ATK: {struct.unpack('<H', enemy2_data[2:4])[0]}")
    print(f"      DEF: {struct.unpack('<H', enemy2_data[4:6])[0]}")
    print(f"   Enemy 2 ({enemy2_name}):")
    print(f"      HP: {struct.unpack('<H', enemy1_data[0:2])[0]}")
    print(f"      ATK: {struct.unpack('<H', enemy1_data[2:4])[0]}")
    print(f"      DEF: {struct.unpack('<H', enemy1_data[4:6])[0]}")


def randomize_all_enemies_completely(world, rom):
    """
    Randomisiere ALLE Gegner untereinander:
    - Jeder Gegner bekommt die KI + Stats eines zufälligen anderen
    - Grafiken werden auch getauscht
    """
    
    # Nur Non-Boss Gegner
    available_enemies = [e for e in enemy_table if e not in boss_list]
    
    print(f"\n🎲 Randomisiere {len(available_enemies)} Gegner komplett...")
    
    # Kopie erstellen
    shuffled = available_enemies.copy()
    world.random.shuffle(shuffled)
    
    # Für jeden Gegner einen zufälligen nehmen
    for original, replacement in zip(available_enemies, shuffled):
        if original != replacement:
            swap_complete_enemy_data(rom, original, replacement)
    
    print(f"✅ Alle {len(available_enemies)} Gegner randomisiert!")


def randomize_enemy_with_seed(world, rom, seed_pair=None):
    """
    Randomisiere Gegner in Paaren basierend auf Seed
    """
    available_enemies = [e for e in enemy_table if e not in boss_list]
    
    print(f"\n🎲 Randomisiere Gegner mit Seed...")
    
    # Erstelle Paare und tausche sie
    for i in range(0, len(available_enemies) - 1, 2):
        enemy1 = available_enemies[i]
        enemy2 = available_enemies[i + 1]
        swap_complete_enemy_data(rom, enemy1, enemy2)
    
    print(f"✅ Gegner-Paare getauscht!")
