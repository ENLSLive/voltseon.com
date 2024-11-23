import json, struct, sys, os
from operator import xor

from util import *

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
    checksum = ((self.block_id & 0xFFFF) + (self.block_id >> 0x10) + (self.save_count & 0xFFFF) + (self.save_count >> 0x10))

    data = self.actual_data

    for i in range(0, len(data), 2):
      word = (data[i] << 8) + data[i + 1]
      checksum += word

    calculated_checksum_a = checksum & 0xFFFF
    calculated_checksum_b = (0xF004 - checksum) & 0xFFFF

    self.valid = (calculated_checksum_a == self.checksum_a) and (calculated_checksum_b == self.checksum_b)

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
    pokemon = "{"
    for i, mon in enumerate(self.pokemon_data):
      if mon is not None and mon.personality_value != "":
        pokemon += f'{i}: {{{mon}}},\n'
    return pokemon + "}"
  
  def __str__(self):
    return f'<PokemonBoxData current_box={self.current_box} pokemon_data={self.get_all_pokemon()} box_names={self.get_all_box_names()} box_wallpapers={len(self.box_wallpapers)}>'
  
class Pokemon:
  def __init__(self, personality_value, trainer_id, nickname, language, ot_name, markings, checksum, org_data, status, level, mail_id, current_hp, total_hp, attack, defense, speed, special_attack, special_defense):
    self.personality_value = to_hex(personality_value)
    self.secret_id, self.trainer_id = split_bits(trainer_id)
    key = personality_value ^ self.trainer_id ^ (self.secret_id << 16)
    self.nickname = nickname
    self.language = language
    self.ot_name = ot_name
    self.markings = MARK_TABLE[markings]
    self.checksum = checksum
    
    if personality_value == 0:
      return

    data = bytearray()
    for i in range(12):
      dec = struct.unpack('<I', org_data[i*4:i*4+4])[0]
      dec ^= key
      data.append(dec & 0xFF)
      data.append((dec >> 8) & 0xFF)
      data.append((dec >> 16) & 0xFF)
      data.append((dec >> 24) & 0xFF)
    
    shuffle_val = personality_value % 24
    funcs = [self.read_growth, self.read_moves, self.read_evs, self.read_misc]

    # First function call
    funcs[shuffle_val // 6](data[0:12])

    # Remove the called function and shift others left
    for i in range(shuffle_val // 6, 3):
        funcs[i] = funcs[i + 1]

    # Second function call
    funcs[(shuffle_val // 2) % 3](data[12:24])

    # Remove the called function and shift others left
    for i in range((shuffle_val // 2) % 3, 2):
        funcs[i] = funcs[i + 1]

    # Third and fourth function calls
    funcs[shuffle_val % 2](data[24:36])
    funcs[1 - (shuffle_val % 2)](data[36:48])

    self.status = status
    self.level = level
    self.mail_id = mail_id
    self.current_hp = current_hp
    self.total_hp = total_hp
    self.attack = attack
    self.defense = defense
    self.speed = speed
    self.special_attack = special_attack
    self.special_defense = special_defense

    self.shiny = ((personality_value >> 16) ^ (personality_value & 0xFFFF) ^ self.trainer_id ^ self.secret_id) < 8
    self.nature = NATURES[personality_value % 25]
  
  def read_growth(self, data):
    self.species = int.from_bytes(data[0:2], "little")
    self.species = self.species
    self.item = int.from_bytes(data[2:4], "little")
    self.exp = int.from_bytes(data[4:8], "little")
    self.pp = data[8]
    self.friendship = data[9]
    self._unused = int.from_bytes(data[10:12], "little")

  def read_moves(self, data):
    self.moves = []
    for i in range(4):
      self.moves.append([int.from_bytes(data[i*2:i*2+2], "little"), int.from_bytes(data[i+8:i+9], "little")])
  
  def read_evs(self, data):
    self.evs = list(data[0:6])
    self.contest_stats = list(data[6:12])

  def read_misc(self, data):
    self.pokerus = data[0]
    self.met_location = data[1]
    stuff = int.from_bytes(data[2:4], "little")
    self.level_met = stuff & 0x7F
    self.game_met = (stuff >> 7) & 0x0F
    self.ball = (stuff >> 11) & 0x0F
    self.ot_gender = stuff >> 15
    self.extract_values(int.from_bytes(data[4:8], "little"))
    self.ribbons_obedience = int.from_bytes(data[8:12], "little")
  
  def extract_values(self, x):
    # Extract HP (bits 0-4)
    self.hp = x & 0x1F  # 0x1F is the mask for the lower 5 bits
    # Extract Attack (bits 5-9)
    self.attack = (x >> 5) & 0x1F  # Shift right by 5 bits, mask the lower 5 bits
    # Extract Defense (bits 10-14)
    self.defense = (x >> 10) & 0x1F  # Shift right by 10 bits, mask the lower 5 bits
    # Extract Speed (bits 15-19)
    self.speed = (x >> 15) & 0x1F  # Shift right by 15 bits, mask the lower 5 bits
    # Extract Special Attack (bits 20-24)
    self.special_attack = (x >> 20) & 0x1F  # Shift right by 20 bits, mask the lower 5 bits
    # Extract Special Defense (bits 25-29)
    self.special_defense = (x >> 25) & 0x1F  # Shift right by 25 bits, mask the lower 5 bits
    # Extract Egg? (bit 30)
    self.egg = (x >> 30) & 0x01  # Shift right by 30 bits, mask the lower 1 bit
    # Extract Ability (bit 31)
    self.ability = (x >> 31) & 0x01  # Shift right by 31 bits, mask the lower 1 bit
  
  @classmethod
  def unpack(cls, data):
    personality_value, trainer_id = struct.unpack('<2I', data[0x0:0x8])
    nickname = readstring(struct.unpack('<10B',data[0x8:0x12]))
    language, flags = struct.unpack('<2B', data[0x12:0x14])
    ot_name = readstring(struct.unpack('<7B', data[0x14:0x1B]))
    markings = struct.unpack('<B', data[0x1B:0x1C])[0]
    checksum = struct.unpack('<H', data[0x1C:0x1E])[0]
    if personality_value == 0:
      return cls(0, 0, "", 0, "", 0, 0, data[0x20:0x50], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    if len(data[0x50:0x64]) == 14:
      status, level, mail_id, current_hp, total_hp, attack, defense, speed, special_attack, special_defense = struct.unpack('<I2B7H', data[0x50:0x64])
    else:
      status, level, mail_id, current_hp, total_hp, attack, defense, speed, special_attack, special_defense = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    #offset = 36
    #species, item, exp, pp, friendship, _unused  = struct.unpack('<HHIBBH', data[32+offset:44+offset])
    return cls(personality_value, trainer_id, nickname, language, ot_name, markings, checksum, data[0x20:0x50], status, level, mail_id, current_hp, total_hp, attack, defense, speed, special_attack, special_defense)
  
  def __str__(self):
    return '\t'.join(f'{key}: {"\"" if isinstance(value, str) else ""}{value}{"\"" if isinstance(value, str) else ""},\n' for key, value in vars(self).items())
    return f'<Pokemon personality_value={self.personality_value} ot={self.trainer_id} nickname={self.nickname} ot_name={self.ot_name} species={self.species}>'
  
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