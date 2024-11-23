import json, struct, sys, os
from operator import xor

CHAR_MAP = { 0x00: " ", 0x1B: "é", 0xBB: "A", 0xD5: "a", 0xA1: "0", 0xBC: "B", 0xD6: "b", 0xA2: "1", 0xBD: "C", 0xD7: "c", 0xA3: "2", 0xBE: "D", 0xD8: "d", 0xA4: "3", 0xBF: "E", 0xD9: "e", 0xA5: "4", 0xC0: "F", 0xDA: "f", 0xA6: "5", 0xC1: "G", 0xDB: "g", 0xA7: "6", 0xC2: "H", 0xDC: "h", 0xA8: "7", 0xC3: "I", 0xDD: "i", 0xA9: "8", 0xC4: "J", 0xDE: "j", 0xAA: "9", 0xC5: "K", 0xDF: "k", 0xAB: "!", 0xC6: "L", 0xE0: "l", 0xAC: "?", 0xC7: "M", 0xE1: "m", 0xAD: ".", 0xC8: "N", 0xE2: "n", 0xAE: "-", 0xC9: "O", 0xE3: "o", 0xAF: "·", 0xCA: "P", 0xE4: "p", 0xB0: "…", 0xCB: "Q", 0xE5: "q", 0xB1: "“", 0xCC: "R", 0xE6: "r", 0xB2: "”", 0xCD: "S", 0xE7: "s", 0xB3: "‘", 0xCE: "T", 0xE8: "t", 0xB4: "’", 0xCF: "U", 0xE9: "u", 0xB5: "♂", 0xD0: "V", 0xEA: "v", 0xB6: "♀", 0xD1: "W", 0xEB: "w", 0xB7: "$", 0xD2: "X", 0xEC: "x", 0xB8: ",", 0xD3: "Y", 0xED: "y", 0xB9: "×", 0xD4: "Z", 0xEE: "z", 0xBA: "/" }

def readstring(bytes):
  str_ = ""
  for c in bytes:
    if c == 0xFF:
      break
    str_ += CHAR_MAP.get(c, "")
  return str_

class DataStructure:
  def __init__(self, raw_data, checksum_a, checksum_b, block_id, save_count, actual_data, footer):
    self.raw_data = raw_data
    self.checksum_a = checksum_a
    self.checksum_b = checksum_b
    self.block_id = block_id
    self.save_count = save_count
    self.actual_data = actual_data
    self.footer = footer
    self.calculate_checksums()

  def calculate_checksums(self):
    checksum = ((self.block_id & 0xFFFF) + ((self.block_id >> 0x10) & 0xFFFF) + (self.save_count & 0xFFFF) + ((self.save_count >> 0x10) & 0xFFFF))

    for i in range(0xC, 0x1FFC, 2):
      word = (self.raw_data[i] << 0x8) + self.raw_data[i + 1]
      checksum += word

    self.checksum_a = checksum & 0xFFFF
    self.checksum_b = 0xF004 - (checksum & 0xFFFF)

    self.valid = (checksum == self.checksum_a) and ((0xF004 - checksum) == self.checksum_b)

  @classmethod
  def unpack(cls, data):
    checksum_a, checksum_b, block_id, save_count = struct.unpack('>HHII', data[:0xC])
    actual_data = data[0xC:0x1FFC]
    footer = struct.unpack('>I', data[0x1FFC:])
    return cls(data, checksum_a, checksum_b, block_id, save_count, actual_data, footer)
  
  def __str__(self):
    return f'<DataStructure checksum_a={self.checksum_a} checksum_b={self.checksum_b} block_id={self.block_id} save_count={self.save_count} actual_data={len(self.actual_data)} footer={self.footer}>'

class PokemonBoxData:
  def __init__(self, current_box, pokemon_data, box_names, box_wallpapers):
    self.current_box = current_box
    self.pokemon_data = pokemon_data
    self.box_names = box_names
    self.box_wallpapers = box_wallpapers

  @classmethod
  def unpack(cls, data):
    current_box = struct.unpack('<I', data[0x04:0x08])
    
    # Unpack Pokemon data
    pokemon_data = []
    for i in range(1500):
      pokemon_data.append(Pokemon.unpack(data[0x08 + 0x54 * i:0x08 + 0x54 * (i + 1)]))

    # Unpack box names
    box_names = []
    for i in range(0x1EC38, 0x1ED19, 9):
      box_names.append(readstring(struct.unpack('<9B',data[i:i+9])))

    # Unpack box wallpapers
    box_wallpapers = list(data[0x1ED19:])

    return cls(current_box, pokemon_data, box_names, box_wallpapers)
  
  def get_box_name(self, box_id):
    return self.box_names[box_id]
  
  def get_all_box_names(self):
    box_names = ""
    for i, name in enumerate(self.box_names):
      if name is not None:
        box_names += f'Box {i}: {name}\n'
    return box_names
  
  def get_all_pokemon(self):
    pokemon = ""
    for i, mon in enumerate(self.pokemon_data):
      if mon is not None and mon.nickname is not None and mon.nickname != "" and mon.personality_value != 0:
        pokemon += f'Pokemon {i}: {mon}\n'
    return pokemon
  
  def __str__(self):
    return f'<PokemonBoxData current_box={self.current_box} pokemon_data={self.get_all_pokemon()} box_names={self.get_all_box_names()} box_wallpapers={len(self.box_wallpapers)}>'
  
class Pokemon:
  def __init__(self, personality_value, original_trainer_id, nickname):
    self.personality_value = personality_value
    self.original_trainer_id = original_trainer_id
    self.nickname = nickname
  
  @classmethod
  def unpack(cls, data):
    personality_value, original_trainer_id = struct.unpack('<2I', data[0:8])
    nickname = readstring(struct.unpack('<10B',data[8:18]))
    return cls(personality_value, original_trainer_id, nickname)
  
  def __str__(self):
    return f'<Pokemon personality_value={self.personality_value} ot={self.original_trainer_id} nickname={self.nickname}>'
  
class BaseStruct:
  @staticmethod
  def format():
    return ''
  
  @staticmethod
  def size():
    return struct.calcsize(__class__.format())

  def __init__(self, data):
    self.data = data

  def print(self):
    print(f'--== {self.__class__.__name__} ==--')
    for key, value in self.__dict__.items():
      if isinstance(value, list):
        for i, item in enumerate(value):
          if isinstance(item, BaseStruct):
            item.print()
          else:
            print(f'{key}[{i}]: {item}')
      elif isinstance(value, BaseStruct):
        value.print()
      else:
        print(f'{key}: {value}')
    print('')