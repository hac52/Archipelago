# Enemy Randomizer Module Documentation

## Overview

Diese Module bieten vollständige Enemy-Randomisierung für Castlevania: Dawn of Sorrow:

- **complete_enemy_randomizer.py** - Tauscht komplette Enemy-Datensätze (Stats, KI, Drops)
- **enemy_randomizer.py** - Randomisiert Individual Enemy-Stats und Drops
- **enemy_graphics_randomizer.py** - Randomisiert Enemy-Grafiken und Paletten

## Features

### Complete Enemy Randomizer

✅ Tauscht zwei Gegner KOMPLETT:
- Stats (HP, ATK, DEF, MP)
- KI und Moveset (durch Datensatztausch)
- Experience Rewards
- Soul Drop Chance
- Item Drops (Common + Rare)

#### Funktionen:

```python
# Zwei spezifische Gegner tauschen
swap_complete_enemy_data(rom, "Zombie", "Bat")

# ALLE Gegner randomisieren
randomize_all_enemies_completely(world, rom)

# Gegner in Paaren tauschen
randomize_enemy_with_seed(world, rom)
```

### Enemy Randomizer

✅ Randomisiert individuelle Enemy-Parameter:
- Stats (HP ±20%, ATK ±20%, DEF ±20%, MP ±30%)
- Drops (Common/Rare Items)
- Soul Chance (±30%)
- Experience (±25%)

#### Funktionen:

```python
# Alle Gegner-Stats randomisieren
randomize_all_enemies(world, rom)
```

### Graphics Randomizer

✅ Randomisiert Enemy-Grafiken:
- Sprite Graphics (vollständige Grafiken tauschen)
- Paletten (Farbpaletten tauschen)
- Separate oder kombinierte Randomisierung

#### Funktionen:

```python
# Grafiken zweier Gegner tauschen
swap_enemy_graphics(rom, "Zombie", "Skeleton")

# Paletten tauschen
swap_enemy_palette(rom, "Zombie", "Skeleton")

# Alle Grafiken randomisieren
randomize_all_enemy_graphics(world, rom)

# Grafiken und Paletten separat randomisieren
randomize_enemy_graphics_with_palette(world, rom)
```

## Integration in Rom.py

In der `patch_rom()` Funktion vor `write_synthesis()`:

```python
if world.options.randomize_enemies == 1:  # Full Swap
    from .modules.complete_enemy_randomizer import randomize_all_enemies_completely
    randomize_all_enemies_completely(world, rom)

if world.options.randomize_enemy_stats:
    from .modules.enemy_randomizer import randomize_all_enemies
    randomize_all_enemies(world, rom)

if world.options.randomize_enemy_graphics:
    from .modules.enemy_graphics_randomizer import randomize_all_enemy_graphics
    randomize_all_enemy_graphics(world, rom)
```

## Enemy Data Structure (0x24 Bytes)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| +0x00 | 2 | HP | Hit Points |
| +0x02 | 2 | ATK | Attack Power |
| +0x04 | 2 | DEF | Defense |
| +0x06 | 2 | MP | Magic Points |
| +0x08 | 1 | Common Drop | Common item drop ID |
| +0x0A | 1 | Rare Drop | Rare item drop ID |
| +0x12 | 2 | Experience | EXP reward |
| +0x14 | 1 | Soul Chance | Soul drop probability |
| +0x16+ | ? | AI/Moveset | Enemy Behavior |

## Sprite Table Setup

Um Grafiken zu randomisieren, müssen Sprite-Adressen bekannt sein:

```python
ENEMY_SPRITE_TABLE = {
    "Enemy Name": EnemySpriteData(
        name="Enemy Name",
        sprite_address=0x163F680,     # RAM-Adresse
        palette_address=0x1E8D74,     # Palette-Adresse
        height=37,                     # Höhe in Pixels
        width=11,                      # Breite (default: 16)
        mirror=True,                   # Horizontal spiegeln?
        swap_colors=True,              # Farben invertieren?
        needs_palette=True             # Hat gültige Palette?
    ),
    # ...
}
```

## Important Notes

⚠️ **Bosses werden NICHT randomisiert** - Sie sind durch `boss_list` geschützt

⚠️ **Sprite-Adressen müssen korrekt sein** - Falsche Adressen können zu Crashes führen

⚠️ **Palette-Adressen** - `0xFFFFFFFF` bedeutet: keine gültige Palette

✅ **Kompatibilität** - Module funktionieren unabhängig und können kombiniert werden

## Example Usage

```python
# Komplette Randomisierung:
if world.options.randomize_enemies:
    # Import
    from .modules.complete_enemy_randomizer import randomize_all_enemies_completely
    from .modules.enemy_graphics_randomizer import randomize_all_enemy_graphics
    
    # Alles randomisieren
    randomize_all_enemies_completely(world, rom)
    randomize_all_enemy_graphics(world, rom)
    
    print("✅ Alle Gegner komplett randomisiert!")
```
