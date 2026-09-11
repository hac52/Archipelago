import struct
from dataclasses import dataclass
from ..in_game_data import enemy_table, boss_list


@dataclass
class EnemySpriteData:
    """Speichert alle Grafik-Informationen eines Feindes"""
    name: str
    sprite_address: int      # RAM-Adresse des Sprites
    palette_address: int     # Palette-Adresse
    height: int              # Sprite-Höhe in Pixels
    width: int = 16          # Sprite-Breite in Pixels
    mirror: bool = True      # Horizontal spiegeln?
    swap_colors: bool = True # Farben invertieren?
    needs_palette: bool = True


# Beispiel Enemy-Grafiken (musst du alle auffinden!)
ENEMY_SPRITE_TABLE = {
    "Zombie": EnemySpriteData("Zombie", 0x163F680, 0x1E8D74, 37, 0x0B),
    "Skeleton": EnemySpriteData("Skeleton", 0x16F00C0, 0x1E9724, 40, 16),
    "Bat": EnemySpriteData("Bat", 0x16E952A, 0x1EA60C, 16, 8),
    "Ghost": EnemySpriteData("Ghost", 0x14F8D00, 0x1E9724, 8, 8),
    "Axe Armor": EnemySpriteData("Axe Armor", 0x10888F0, 0xFFFFFFFF, 26, 16, False, False, False),
    "Skeleton Ape": EnemySpriteData("Skeleton Ape", 0x152CF00, 0x1E94F8, 11, 8, False),
    "Witch": EnemySpriteData("Witch", 0x1384000, 0x1E7F10, 48),
    "Slime": EnemySpriteData("Slime", 0x1488200, 0x1E7A18, 16),
    # ... mehr hinzufügen
}


def swap_enemy_graphics(rom, enemy1_name: str, enemy2_name: str):
    """Tausche die Grafiken von zwei Feinden"""
    
    if enemy1_name not in ENEMY_SPRITE_TABLE or enemy2_name not in ENEMY_SPRITE_TABLE:
        print(f"⚠️ Sprite nicht in Tabelle: {enemy1_name} oder {enemy2_name}")
        return
    
    enemy1 = ENEMY_SPRITE_TABLE[enemy1_name]
    enemy2 = ENEMY_SPRITE_TABLE[enemy2_name]
    
    # Größe der Sprite-Daten berechnen (Height * Width)
    sprite1_size = enemy1.height * enemy1.width
    sprite2_size = enemy2.height * enemy2.width
    
    # Sprites auslesen
    sprite1_data = rom.read_direct(enemy1.sprite_address, sprite1_size)
    sprite2_data = rom.read_direct(enemy2.sprite_address, sprite2_size)
    
    # Sprites tauschen
    rom.write_direct(enemy1.sprite_address, sprite2_data[:sprite1_size])
    rom.write_direct(enemy2.sprite_address, sprite1_data[:sprite2_size])
    
    print(f"✅ {enemy1_name} ↔️ {enemy2_name} Grafiken getauscht")


def swap_enemy_palette(rom, enemy1_name: str, enemy2_name: str):
    """Tausche nur die Paletten von zwei Feinden"""
    
    if enemy1_name not in ENEMY_SPRITE_TABLE or enemy2_name not in ENEMY_SPRITE_TABLE:
        return
    
    enemy1 = ENEMY_SPRITE_TABLE[enemy1_name]
    enemy2 = ENEMY_SPRITE_TABLE[enemy2_name]
    
    # Paletten auslesen (16 Farben = 0x20 Bytes)
    palette1 = rom.read_direct(enemy1.palette_address, 0x20)
    palette2 = rom.read_direct(enemy2.palette_address, 0x20)
    
    # Paletten tauschen
    rom.write_direct(enemy1.palette_address, palette2)
    rom.write_direct(enemy2.palette_address, palette1)
    
    print(f"✅ {enemy1_name} ↔️ {enemy2_name} Paletten getauscht")


def randomize_all_enemy_graphics(world, rom):
    """
    Randomisiere alle Enemy-Grafiken komplett
    """
    from ..in_game_data import enemy_table
    
    # Filtered Liste (keine Bosses)
    available_enemies = [e for e in enemy_table if e not in boss_list and e in ENEMY_SPRITE_TABLE]
    
    # Kopie erstellen für Shuffling
    shuffled_enemies = available_enemies.copy()
    world.random.shuffle(shuffled_enemies)
    
    # Für jeden Feind einen zufälligen anderen nehmen
    for original_enemy, random_enemy in zip(available_enemies, shuffled_enemies):
        if original_enemy != random_enemy:
            swap_enemy_graphics(rom, original_enemy, random_enemy)


def randomize_enemy_graphics_with_palette(world, rom):
    """
    Randomisiere Grafiken UND Paletten separat
    (interessantere Effekte)
    """
    available_enemies = [e for e in enemy_table if e not in boss_list and e in ENEMY_SPRITE_TABLE]
    
    # Sprite und Palette separat shufflen
    sprites = available_enemies.copy()
    palettes = available_enemies.copy()
    
    world.random.shuffle(sprites)
    world.random.shuffle(palettes)
    
    # Tausche Sprites
    for i, original in enumerate(available_enemies):
        if original != sprites[i]:
            swap_enemy_graphics(rom, original, sprites[i])
    
    # Tausche Paletten
    for i, original in enumerate(available_enemies):
        if original != palettes[i]:
            swap_enemy_palette(rom, original, palettes[i])
