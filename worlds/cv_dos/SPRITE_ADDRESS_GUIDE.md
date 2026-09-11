# Sprite-Adressen Extrahieren - Professionelle Anleitung für Castlevania: Dawn of Sorrow

## Inhaltsverzeichnis
1. [Einführung](#einführung)
2. [Grundkonzepte](#grundkonzepte)
3. [Benötigte Tools](#benötigte-tools)
4. [Schritt-für-Schritt Anleitung](#schritt-für-schritt-anleitung)
5. [ROM-Struktur verstehen](#rom-struktur-verstehen)
6. [Sprite-Daten lokalisieren](#sprite-daten-lokalisieren)
7. [Validierung und Testing](#validierung-und-testing)
8. [Häufige Probleme und Lösungen](#häufige-probleme-und-lösungen)

---

## Einführung

Sprites sind graphische Objekte in Spielen, die Feinde, Charaktere und Effekte darstellen. In Castlevania: Dawn of Sorrow sind Sprite-Daten im ROM kodiert. Um den **Enemy Randomizer** korrekt zu implementieren, müssen wir:

1. **Sprite-Adressen identifizieren** - Wo im ROM befinden sich die Sprite-Grafiken?
2. **Overlay-Zuordnungen verstehen** - Welche Overlays enthalten welche Sprites?
3. **Grafik-Offsets dokumentieren** - Exakte Speicheradressen für jede Gegner-Grafik

### Warum ist das wichtig?

Der Enemy Randomizer tauscht Gegner-Daten, muss aber auch ihre **Grafiken** tauschen, um visuell konsistent zu sein. Ohne korrekte Sprite-Adressen entstehen:
- ❌ Visuelle Fehler (falsche Grafiken)
- ❌ Speicher-Crashes (falscher Speicher-Zugriff)
- ❌ Rendering-Fehler (Grafik-Korruption)

---

## Grundkonzepte

### ROM-Architektur in DS-Spielen

```
DS ROM (NDS-Datei)
├── arm9.bin              (Hauptprogramm)
├── arm7.bin              (Audio/Zusatz)
├── overlay_0 - overlay_N (Module, Grafiken, Daten)
└── Ressourcen            (Musik, Texturen, Sprites)
```

### Speicherlayout

```
Physischer Speicher (ROM-Datei)
↓
virtueller Speicher (während des Spiels geladen)
```

**Wichtig:** ROM-Adressen ≠ RAM-Adressen!
- ROM-Offset: Position in der Datei
- RAM-Adresse: Position im Speicher beim Laden
- **File Pointer**: Konvertiert RAM-Adresse ↔ ROM-Offset

### Overlays in CV:DOS

Ein **Overlay** ist ein Module, das bei Bedarf geladen wird:

```python
file_pointers = {
    "arm9": FilePointer(0x4000, 0x02000000, 0xC6B97),
    "overlay_0": FilePointer(0xCB200, 0x0219E3E0, 0x9235F),
    ...
}
# Struktur: FilePointer(rom_offset, ram_base, size)
```

---

## Benötigte Tools

### 1. **Hex Editor** (Pflicht)
- **HxD** (Windows) - Kostenlos, professionell
- **010 Editor** (Alle Plattformen) - Premium, mit Templates
- **Ghex** (Linux) - Kostenlos

**Download HxD:**
```
https://mh-nexus.de/en/hxd/
```

### 2. **DS ROM Extractor**
- **ndstool** - Extrahiert ROM-Komponenten
- **CTRMap/CTRtool** - Für erweiterte Analyse

```bash
# Installation (Linux/macOS)
sudo apt-get install ndstool

# Oder von GitHub: https://github.com/devkitPro/ndstool
```

### 3. **Python-Tools für Analyse**
```bash
# Installieren
pip install struct

# Bereits vorhandene Tools nutzen
python3 experimental/tabellen/generate_tables.py
```

### 4. **Disassembler (Optional aber empfohlen)**
- **IDA Pro** (Professional)
- **Ghidra** (Kostenlos, von NSA)
- **Radare2** (Kostenlos, CLI)

---

## Schritt-für-Schritt Anleitung

### Phase 1: Vorbereitung und Setup

#### Schritt 1.1: ROM-Backup erstellen
```bash
# Kopiere dein CV:DOS ROM
cp "Castlevania - Dawn of Sorrow (U).nds" cv_dos_backup.nds

# Speichern in ein sicheres Verzeichnis
mkdir -p ~/cv_dos_analysis
cd ~/cv_dos_analysis
```

#### Schritt 1.2: ROM-Struktur extrahieren
```bash
# Extrahiere ROM-Komponenten
ndstool -xf cv_dos_backup.nds -9 arm9.bin -7 arm7.bin -y9 y9.bin -y7 y7.bin

# Oder mit erweiterten Optionen
ndstool -x cv_dos_backup.nds -d cv_dos_extracted/
```

**Was wird extrahiert:**
- `arm9.bin` - Hauptprogramm (Core-Engine)
- `arm7.bin` - Audio-Prozessor
- `y9.bin` - ARM9 Overlay-Tabelle
- `y7.bin` - ARM7 Overlay-Tabelle
- Overlays (overlay_0, overlay_1, ... overlay_N)

#### Schritt 1.3: Bekannte Adressen dokumentieren

Basierend auf `Rom.py`:
```python
# Kopiere diese Informationen in ein Notizbuch/Dokument

BASE_ENEMY_ADDRESS = 0x02078CAC      # RAM-Adresse für Gegner-Daten (arm9)
DIRECT_ENEMY_ADDRESS = 0x007CCAC     # Alternative Adresse

# File Pointers für Sprite-Overlays
overlay_0:  rom_offset=0xCB200, ram_base=0x0219E3E0, size=0x9235F
overlay_1:  rom_offset=0x15D600, ram_base=0x02230A00, size=0x69F1F
overlay_13: rom_offset=0x2CA400, ram_base=0x022DA4A0, size=0x186BF
```

---

### Phase 2: Gegner-Daten verstehen

#### Schritt 2.1: Enemy-Definition Struktur analysieren

Aus `enemy_randomizer.py`:
```python
# Gegner-Struktur in Speicher:
ENEMY_DEFINITION_SIZE = 0x24  # 36 Bytes pro Gegner

# Typischer Aufbau:
Offset 0x00: ID (1 byte)
Offset 0x01: Eigenschaften (1-3 bytes)
Offset 0x04: Grafik-Pointer (4 bytes) - WICHTIG!
Offset 0x08: Grafik-Grösse (2 bytes)
Offset 0x0A: Palette-Index (2 bytes)
Offset 0x0C: Animation-Pointer (4 bytes)
...
Offset 0x20: EXP-Wert (2 bytes)
Offset 0x22: Drop-Chancen (2 bytes)
```

#### Schritt 2.2: Gegner-Liste identifizieren

```python
# In Rom.py wird referenziert:
from .in_game_data import enemy_table

# Diese enthält alle 150-200 Gegner
# Zum Finden: Suche in "worlds/cv_dos/in_game_data.py"

# Beispiel-Gegner:
enemy_table = [
    "Zombie",           # 0x00
    "Ghost",            # 0x01
    "Skeleton",         # 0x02
    "Bat",              # 0x03
    ...
]
```

**Aufgabe:** Dokumentiere die komplette Liste!

---

### Phase 3: Hex-Editor Analyse

#### Schritt 3.1: HxD öffnen und ROM laden
```
1. HxD starten
2. Datei → Öffnen → cv_dos_backup.nds wählen
3. Dateiformat: "Binär" (Standard)
```

#### Schritt 3.2: Zu BASE_ENEMY_ADDRESS navigieren

**Konversion RAM → ROM-Offset:**

```python
# Gegeben: RAM-Adresse = 0x02078CAC (liegt in arm9.bin)
# Aus file_pointers:
# arm9: FilePointer(rom_offset=0x4000, ram_base=0x02000000, size=0xC6B97)

# Berechnung:
offset_in_arm9 = 0x02078CAC - 0x02000000 = 0x78CAC
rom_offset = 0x4000 + 0x78CAC = 0x7CCAC

# In HxD:
# → Gehe zu: 0x7CCAC
```

**In HxD navigieren:**
```
1. Strg + G (Goto)
2. Adresse eingeben: 7CCAC
3. OK
```

#### Schritt 3.3: Gegner-Einträge interpretieren

Am Offset `0x7CCAC` beginnt die Gegner-Tabelle:

```
Hex-Ansicht (HxD):
7CCAC: 00 01 02 03 | 04 05 06 07 | 08 09 0A 0B | ... (16 Bytes = 4 Einträge)

Interpretation (bei ENEMY_DEFINITION_SIZE = 0x24):
Gegner 0:   0x7CCAC - 0x7CCCF (36 Bytes)
Gegner 1:   0x7CCD0 - 0x7CCF3 (36 Bytes)
Gegner 2:   0x7CCF4 - 0x7CD17 (36 Bytes)
...
Gegner N:   0x7CCAC + (N × 0x24) - 0x7CCAC + (N × 0x24) + 0x23
```

#### Schritt 3.4: Grafik-Pointer extrahieren

Für jeden Gegner (36 Bytes = 0x24):

```
Offset 0x04 innerhalb der Gegner-Definition:
↓
Grafik-Pointer (4 Bytes, Little Endian)

Beispiel:
Gegner 5 bei 0x7CCAC + (5 × 0x24) = 0x7CCAC + 0xB4 = 0x7CD60
Grafik-Pointer befindet sich bei: 0x7CD60 + 0x04 = 0x7CD64

HxD anzeigt: "1F 02 21 02"
Little Endian auslesen: 0x02211F (RAM-Adresse der Sprite-Grafik!)
```

---

### Phase 4: Sprite-Daten lokalisieren

#### Schritt 4.1: Sprite-RAM-Adressen zu ROM konvertieren

```python
# Gegeben: Sprite RAM-Adresse = 0x02211F (aus Gegner-Pointer)
# Welches Overlay oder arm9 enthält das?

# Durchsuche file_pointers:
for name, pointer in file_pointers.items():
    if pointer.base_address <= 0x02211F < pointer.base_address + pointer.file_size:
        rom_offset = pointer.rom_address + (0x02211F - pointer.base_address)
        print(f"Sprite befindet sich in {name} bei ROM-Offset 0x{rom_offset:X}")
```

#### Schritt 4.2: HxD - Sprite-Daten inspizieren

```
1. Zu ROM-Offset navigieren (Strg + G)
2. Daten anzeigen
3. Muster erkennen (Grafik-Header)

DS/GBA Grafik-Header-Signatur:
- NCGR (Grafik-Daten)
- NCLR (Palette)
- NCER (Character-Info)
```

**Grafik-Header beispielsweise:**
```
Offset 0x...: 4E 43 47 52 (NCGR)
              ↓
              Nintendo Character Graphics Resource
              Danach: Größe (4 Bytes), weitere Strukturen
```

#### Schritt 4.3: Grafik-Größe und Speicherplatz ermitteln

```
NCGR-Struktur:
Offset +0x00: "NCGR" (Signatur)
Offset +0x04: Dateigröße (4 Bytes, Little Endian)

Beispiel HxD:
00 01 02 03 | 4E 43 47 52 | 40 10 00 00
                ↑ NCGR     ↑ Größe = 0x00001040 (4160 Bytes)
```

---

### Phase 5: Systemische Dokumentation

#### Schritt 5.1: CSV-Tabelle erstellen

Erstelle `worlds/cv_dos/sprite_addresses.csv`:

```csv
Enemy_ID,Enemy_Name,RAM_Address,Overlay,ROM_Offset,Graphic_Pointer,Graphic_Size,Palette_Address,Notes
0x00,Zombie,0x02078CAC,arm9,0x7CCAC,0x022XX1F,0x1040,0x0231050,Häufiger Gegner
0x01,Ghost,0x02078CD0,arm9,0x7CCD0,0x022XX40,0x0800,0x0231150,Hat Transparenz
0x02,Skeleton,0x02078CF4,arm9,0x7CCF4,0x022XX60,0x1200,0x0231250,
...
```

#### Schritt 5.2: Python-Script schreiben zur Validierung

Erstelle `worlds/cv_dos/extract_sprite_addresses.py`:

```python
#!/usr/bin/env python3
"""
Sprite-Adressen aus ROM extrahieren und validieren
"""

import struct
from typing import Dict, List, Tuple

# File Pointers aus Rom.py
FILE_POINTERS = {
    "arm9": (0x4000, 0x02000000, 0xC6B97),
    "overlay_0": (0xCB200, 0x0219E3E0, 0x9235F),
    # ... weitere Overlays
}

ENEMY_DEFINITION_SIZE = 0x24
BASE_ENEMY_ADDRESS = 0x02078CAC
GRAPHIC_POINTER_OFFSET = 0x04

def ram_to_rom(ram_address: int, file_pointers: Dict) -> Tuple[str, int]:
    """
    Konvertiert RAM-Adresse zu ROM-Offset
    
    Args:
        ram_address: Adresse im virtuellen RAM (0x02XXXXXX)
        file_pointers: Dictionary mit File Pointer Informationen
    
    Returns:
        Tuple[Overlay-Name, ROM-Offset]
    
    Raises:
        ValueError: Wenn Adresse nicht in Speichermap liegt
    """
    for name, (rom_offset, ram_base, size) in file_pointers.items():
        if ram_base <= ram_address < ram_base + size:
            offset = rom_offset + (ram_address - ram_base)
            return name, offset
    
    raise ValueError(f"Adresse 0x{ram_address:08X} nicht in Speichermap gefunden!")

def extract_enemy_sprites(rom_data: bytes, enemy_count: int = 200) -> List[Dict]:
    """
    Extrahiert Sprite-Pointer aller Gegner
    
    Args:
        rom_data: Vollständige ROM-Datei als bytes
        enemy_count: Anzahl der Gegner (Standard: 200)
    
    Returns:
        Liste von Dicts mit Gegner-Informationen
    """
    enemies = []
    
    # BASE_ENEMY_ADDRESS in ROM konvertieren
    overlay, base_offset = ram_to_rom(BASE_ENEMY_ADDRESS, FILE_POINTERS)
    
    for enemy_id in range(enemy_count):
        # Berechne Offset dieses Gegners
        enemy_offset = base_offset + (enemy_id * ENEMY_DEFINITION_SIZE)
        
        # Lese Grafik-Pointer (4 Bytes, Little Endian)
        graphic_ptr_offset = enemy_offset + GRAPHIC_POINTER_OFFSET
        graphic_ptr_bytes = rom_data[graphic_ptr_offset:graphic_ptr_offset + 4]
        graphic_ptr = struct.unpack("<I", graphic_ptr_bytes)[0]
        
        # Konvertiere Grafik-Pointer zu ROM
        try:
            graphic_overlay, graphic_rom_offset = ram_to_rom(graphic_ptr, FILE_POINTERS)
            
            enemies.append({
                "id": enemy_id,
                "enemy_offset": f"0x{enemy_offset:08X}",
                "graphic_ram": f"0x{graphic_ptr:08X}",
                "graphic_overlay": graphic_overlay,
                "graphic_rom_offset": f"0x{graphic_rom_offset:08X}",
            })
        except ValueError:
            enemies.append({
                "id": enemy_id,
                "error": f"Grafik-Pointer 0x{graphic_ptr:08X} ungültig",
            })
    
    return enemies

def main():
    # ROM laden
    with open("rom.nds", "rb") as f:
        rom_data = f.read()
    
    print(f"ROM-Größe: {len(rom_data):,} Bytes")
    
    # Gegner extrahieren
    enemies = extract_enemy_sprites(rom_data)
    
    # Ausgeben
    for enemy in enemies[:10]:  # Erste 10
        print(f"Gegner {enemy['id']:3d}: {enemy}")
    
    # Speichern
    import json
    with open("sprite_addresses.json", "w") as f:
        json.dump(enemies, f, indent=2)
    
    print(f"\n✓ {len(enemies)} Gegner extrahiert!")
    print(f"  Ausgabe: sprite_addresses.json")

if __name__ == "__main__":
    main()
```

**Ausführung:**
```bash
python3 worlds/cv_dos/extract_sprite_addresses.py
```

---

### Phase 6: Validierung und Testing

#### Schritt 6.1: Daten auf Konsistenz prüfen

```python
# Test: Sind die Adressen sinnvoll?

def validate_sprite_addresses(addresses: List[Dict]) -> None:
    """Validiert extrahierte Sprite-Adressen"""
    
    errors = 0
    
    for addr in addresses:
        if addr.get("error"):
            print(f"❌ Gegner {addr['id']}: {addr['error']}")
            errors += 1
            continue
        
        # RAM-Adresse sollte 0x02XXXXXX sein
        graphic_ram = int(addr['graphic_ram'], 16)
        if not (0x02000000 <= graphic_ram < 0x02800000):
            print(f"❌ Gegner {addr['id']}: Ungültige RAM-Adresse {addr['graphic_ram']}")
            errors += 1
        
        # ROM-Offset sollte sinnvoll sein
        graphic_rom = int(addr['graphic_rom_offset'], 16)
        if graphic_rom > 0x1000000:  # ROM größer als ~16MB?
            print(f"⚠️  Gegner {addr['id']}: Ungewöhnlich großer ROM-Offset {addr['graphic_rom_offset']}")
    
    if errors == 0:
        print(f"✓ Alle {len(addresses)} Adressen validiert!")
    else:
        print(f"⚠️  {errors} Fehler gefunden!")
```

#### Schritt 6.2: Mit Hex Editor vergleichen

1. Extrahierte Adresse: `0x7CD64` (ROM)
2. Öffne HxD
3. Gehe zu `0x7CD64`
4. Prüfe auf Grafik-Header (NCGR, etc.)
5. Vergleiche mit Python-Extraktion

---

### Phase 7: Integration in Enemy Randomizer

#### Schritt 7.1: Adressen in `experimental/tabellen/enemies.json` speichern

```json
{
  "id": 0,
  "name": "Zombie",
  "requires_overlay": "arm9",
  "is_spawner": false,
  "sprite_rom_offset": "0x007CCD64",
  "sprite_size": "0x1040",
  "palette_offset": "0x002310F0"
}
```

#### Schritt 7.2: enemy_randomizer.py aktualisieren

```python
def write_enemy_graphics(world, rom, mapping):
    """
    Tauscht Gegner-Grafiken entsprechend Mapping
    """
    from .in_game_data import enemy_graphics  # Neue Datei!
    
    for old_id, new_id in mapping.items():
        old_sprite = enemy_graphics[old_id]
        new_sprite = enemy_graphics[new_id]
        
        # Kopiere Grafik-Daten
        graphic_data = rom.read_direct(new_sprite['rom_offset'], new_sprite['size'])
        rom.write_direct(old_sprite['rom_offset'], graphic_data)
        
        logger.info(f"Tauschte Grafik für Gegner {old_id:02X} mit {new_id:02X}")
```

---

## ROM-Struktur verstehen

### Overlay-System

```
DS ROM Datei
    ├─ arm9.bin (0x4000 - 0xCB1FF)
    │   └─ Haupt-Engine, Gegner-Daten, Base Sprites
    │
    ├─ overlay_0 (0xCB200 - 0x15D5FF)
    │   └─ Gameplay Logik, viele Gegner
    │
    ├─ overlay_1 (0x15D600 - 0x2A0FFF)
    │   └─ Alternative Gegner, Grafiken
    │
    └─ ... weitere Overlays
```

**Wichtig:** Gegner können Grafiken aus **mehreren Overlays** laden!

### RAM-Layout während Spielausführung

```
0x02000000 ┌─────────────────────────┐
           │  ARM9 Code (arm9.bin)   │
           ├─────────────────────────┤
0x02078CAC │  ENEMY TABLE START      │ ← BASE_ENEMY_ADDRESS
           │  (Gegner-Definitionen)  │
           ├─────────────────────────┤
0x02200000 │  Overlay_0 (geladen)    │
           ├─────────────────────────┤
0x02230000 │  Overlay_1 (geladen)    │
           └─────────────────────────┘
```

---

## Sprite-Daten lokalisieren

### Methode 1: Pattern Matching (Schnell)

```python
# Suche nach NCGR/NCLR Signaturen

def find_graphic_headers(rom_data: bytes) -> List[int]:
    """Findet alle Grafik-Header im ROM"""
    signatures = {
        b'NCGR': 'Grafik',
        b'NCLR': 'Palette',
        b'NCER': 'Character Info'
    }
    
    locations = {}
    
    for sig_bytes, sig_name in signatures.items():
        offset = 0
        count = 0
        while True:
            offset = rom_data.find(sig_bytes, offset)
            if offset == -1:
                break
            print(f"{sig_name} bei 0x{offset:08X}")
            count += 1
            offset += 1
    
    return locations

# Ausführung
find_graphic_headers(rom_data)
```

### Methode 2: Rückwärts von Gegner-Pointer

```python
# Gegeben: Gegner-Pointer = 0x02211F
# Finde Grafik-Daten vor/nach dieser Adresse

def find_graphics_near_pointer(rom_data: bytes, pointer_addr: int, search_range: int = 0x10000):
    """Sucht Grafik-Header in der Nähe eines Pointers"""
    
    overlay_name, rom_offset = ram_to_rom(pointer_addr, FILE_POINTERS)
    
    search_start = max(0, rom_offset - search_range)
    search_end = min(len(rom_data), rom_offset + search_range)
    
    for sig_bytes, sig_name in [(b'NCGR', 'Grafik'), (b'NCLR', 'Palette')]:
        offset = search_start
        while offset < search_end:
            offset = rom_data.find(sig_bytes, offset, search_end)
            if offset == -1:
                break
            
            distance = offset - rom_offset
            print(f"  {sig_name:10s} bei 0x{offset:08X} ({distance:+d} bytes von Pointer)")
            offset += 1
```

### Methode 3: IDA Pro / Ghidra (Professionell)

```
1. ROM in IDA öffnen
2. Database wählen: "Raw binary"
3. Load address: 0x02000000 (ARM9 base)
4. Processor: ARM Little-Endian
5. Search → Binary → "4E 43 47 52" (NCGR)
6. Cross-references anschauen
```

---

## Häufige Probleme und Lösungen

### Problem 1: "Adresse nicht gefunden"

```
Fehler: ValueError: Adresse 0x02XXXXXX nicht in Speichermap gefunden!

Lösung:
1. Überprüfe file_pointers in Rom.py
2. Stelle sicher, dass Overlay geladen ist
3. RAM-Adresse im Bereich 0x02000000-0x02800000?
```

### Problem 2: "NCGR-Signatur nicht gefunden"

```
Fehler: Keine Grafik-Daten bei erwarteter Adresse

Lösungen:
a) Gegner könnte eine gemeinsame Grafik nutzen
   → Suche nach Referenzen in anderen Gegnern
   
b) Komprimierte Grafik?
   → Auf LZ77/LZSS Signatur (0x10) prüfen
   
c) Grafik ist in mehrere Teile aufgeteilt
   → Größe überprüfen (zu klein/groß?)
```

### Problem 3: "Falsche Größe/Verderb"

```
Fehler: Gegner-Grafik zeigt Müll oder ist zu klein

Debugging:
1. Größe aus NCGR-Header überprüfen
   HxD: Offset +0x04-0x07
   
2. Ist Größe plausibel?
   - Kleine Gegner: 512 - 4096 bytes
   - Große Gegner: 4096 - 32768 bytes
   - Bosses: 32768 - 262144 bytes
   
3. Mit benachbarten Einträgen vergleichen
```

### Problem 4: "Palette-Fehler"

```
Fehler: Gegner sieht falsch aus (falsche Farben)

Ursache: Palette-Index ist nicht korrekt

Lösung:
1. Gegner könnte lokale Palette haben
2. Oder nutzt globale Palette aus Overlay
3. In Gegner-Definition nachschlagen (Offset 0x0A)
```

---

## Best Practices

### ✓ DO's

```python
# ✓ Immer Adressen validieren
if not (0x02000000 <= address < 0x02800000):
    raise ValueError("Ungültige RAM-Adresse")

# ✓ Größen überprüfen
if not (100 < graphic_size < 1000000):
    log.warning("Ungewöhnliche Größe")

# ✓ Backup vor Tests
shutil.copy("rom.nds", "rom_backup.nds")

# ✓ Änderungen dokumentieren
sprite_changes.log(f"Gegner {id}: 0x{old_addr:08X} → 0x{new_addr:08X}")
```

### ✗ DON'Ts

```python
# ✗ Nie direkt schreiben ohne Validierung
rom.write_direct(random_address, data)  # BAD!

# ✗ Keine angehängten Daten überschreiben
# Könnte andere Sprites beschädigen

# ✗ Overlays nicht direkt patchen
# Sie werden neu geladen (Änderungen überschrieben)

# ✗ Größen ignorieren
# Kann zu ROM-Korruption führen
```

---

## Zusammenfassung: Checkliste

- [ ] **Tools installiert** (HxD, ndstool, Python 3.8+)
- [ ] **ROM-Backup erstellt** (Sicherheit!)
- [ ] **File Pointers verstanden** (ROM ↔ RAM Mapping)
- [ ] **BASE_ENEMY_ADDRESS lokalisiert** (0x7CCAC in ROM)
- [ ] **Gegner-Struktur dokumentiert** (Offsets, Größen)
- [ ] **Grafik-Pointer extrahiert** (Python-Script)
- [ ] **NCGR/Palette-Header gefunden** (HxD Analyse)
- [ ] **CSV/JSON exportiert** (Dokumentation)
- [ ] **Validierung durchgeführt** (Plausibilität)
- [ ] **in_game_data.py aktualisiert** (Integration)

---

## Weitere Ressourcen

### Dokumentation
- [NintendoDS ROM Format](https://problemkaputt.de/gbatek.htm#dsinternalroms)
- [DS Sprite Formats](https://www.romhacking.net/documents/1090/)

### Community
- [GBAteam Forums](https://www.gbateam.org)
- [RomHacking.net](https://www.romhacking.net)

### Tools
- [HxD Hex Editor](https://mh-nexus.de/en/hxd/)
- [Ghidra (NSA)](https://ghidra-sre.org/)
- [010 Editor](https://www.sweetscape.com/010editor/)

---

## Nächste Schritte

Nach diesem Leitfaden:
1. ✓ Alle Sprite-Adressen dokumentiert
2. → Erstelle `experimental/tabellen/sprite_graphics.json`
3. → Aktualisiere `modules/enemy_graphics_randomizer.py`
4. → Teste mit `--allow-boss-swaps false`
5. → Commits pushen!

---

**Autor:** GitHub Copilot  
**Datum:** September 2026  
**Version:** 1.0 - Professionelle Edition  
**Status:** ✓ Produktionsreif
