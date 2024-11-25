import math
import json, struct, sys, os
from operator import xor

from personal import *
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
    pokemon = "{\n"
    for i, mon in enumerate(self.pokemon_data):
      if mon is not None and mon.personality_value != "":
        pokemon += f'\t\"{i}\": {{\n\t\t{mon}\t}},\n'
    return pokemon.removesuffix(",\n") + "\n}"
  
  def __str__(self):
    return f'<PokemonBoxData current_box={self.current_box} pokemon_data={self.get_all_pokemon()} box_names={self.get_all_box_names()} box_wallpapers={len(self.box_wallpapers)}>'
  
class Pokemon:
  def __init__(self, personality_value, trainer_id, nickname, language, flags, ot_name, markings, checksum, org_data, status, level, mail_id, current_hp, total_hp, attack, defense, speed, special_attack, special_defense):
    self.pid = personality_value
    self.personality_value = to_hex(personality_value)
    self.secret_id, self.trainer_id = split_bits(trainer_id)
    key = personality_value ^ self.trainer_id ^ (self.secret_id << 16)
    self.nickname = nickname
    self.language = LANG[language]
    self.bad_egg = flags & 1 == 1
    self.has_species = (flags >> 1) & 1 == 1
    self.use_egg_name = (flags >> 2) & 1 == 1
    self.block_box_rs = (flags >> 3) & 1 == 1
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
    self.growth_rate = GROWTH[self.species]
    self.species_name = SPECIES[self.species]
    self.level = 100
    for i in range(99):
      if (self.exp < EXPERIENCE[i * 6 + self.growth_rate]):
          self.level = i
          break
    if self.level < 100:
      levelexp = EXPERIENCE[self.level * 6 + self.growth_rate]
      self.exp_percentage = round(self.exp / levelexp, 3) * 100
      self.exp_to_next_level = levelexp - self.exp
    self.ability_name = ABILITIES[get_abilities(self.species)[self.ability]]
    types = get_types(self.species)
    self.types = [TYPES[types[0]], TYPES[types[1]]]
    self.get_gender()
    self.get_stats()
    self.get_hidden_power()
    for i in range(4):
      self.moves[i][1] = math.floor(self.moves[i][1] * (1 + self.pp_bonuses[i] * 0.2))
  
  def read_growth(self, data):
    self.species = int.from_bytes(data[0:2], "little")
    self.species = get_species(self.species)
    self.item = int.from_bytes(data[2:4], "little")
    self.item_name = ITEMS[self.item]
    self.exp = int.from_bytes(data[4:8], "little")
    self.pp_bonuses = [data[8] & 0b11, (data[8] >> 2) & 0b11, (data[8] >> 4) & 0b11, (data[8] >> 6) & 0b11]
    self.friendship = data[9]
    self._unused = int.from_bytes(data[10:12], "little")

  def read_moves(self, data):
    self.moves = []
    for i in range(4):
      self.moves.append([MOVES[int.from_bytes(data[i*2:i*2+2], "little")], int.from_bytes(data[i+8:i+9], "little")])
  
  def read_evs(self, data):
    self.evs = list(data[0:6])
    self.contest_stats = list(data[6:12])

  def read_misc(self, data):
    self.has_pokerus = data[0] > 0
    if (self.has_pokerus):
      self.pokerus_days = data[0] & 0b1111
      self.pokerus_strain = (data[0] >> 4) & 0b1111
      self.cured = self.pokerus_days == 0 and self.pokerus_strain > 0
    stuff = int.from_bytes(data[2:4], "little")
    self.level_met = stuff & 0x7F
    self.hatched = self.level_met == 0
    self.game_met = (stuff >> 7) & 0x0F
    self.origin_game = ORIGIN_GAME[self.game_met]
    self.met_location = LOCATION_OVERRIDES[data[1]][self.origin_game] if data[1] in LOCATION_OVERRIDES and self.origin_game in LOCATION_OVERRIDES[data[1]] else LOCATIONS_GC[data[1]] if self.game_met == 15 else LOCATIONS[data[1]]
    self.ball = (stuff >> 11) & 0x0F
    self.pokeball = BALLS[self.ball]
    self.ot_gender = stuff >> 15
    self.extract_values(int.from_bytes(data[4:8], "little"))
    ribbons_obedience = int.from_bytes(data[8:12], "little")
    self.ribbons = []
    for i, name in enumerate(["Cool", "Beauty", "Cute", "Smart", "Tough"]):
      ribbon = (ribbons_obedience >> (i * 3)) & 0b111
      if ribbon == 0:
        continue
      self.ribbons.append(f"{["", "", "Super ", "Hyper ", "Master ", "Unknown ", "Unknown "][ribbon]}{name} Ribbon")
    for i, name in enumerate(["Champion", "Winning", "Victory", "Artist", "Effort", "Marine", "Land", "Sky", "Country", "National", "Earth", "World"]):
      if (ribbons_obedience >> (15 + i)) & 1 == 1:
        self.ribbons.append(f"{name} Ribbon")
    self.fateful_encounter = (ribbons_obedience >> 31) & 1 == 1
  
  def get_hidden_power(self):
    lsbsum = 0
    for i in range(6):
      lsbsum += self.ivs[i] % 2 * 2**i
    type = TYPES[(lsbsum * 15) // 63 + 1]
    lsbsum = 0
    for i in range(6):
      lsbsum += (1 if self.ivs[i] % 4 == 2 or self.ivs[i] % 4 == 3 else 0) * 2**i
    power = (lsbsum * 40) // 63 + 30
    self.hidden_power = [type, power]

  def extract_values(self, x):
    self.ivs = [0] * 6
    for i in range(6):
      self.ivs[i] = x & 0x1F
      x >>= 5
    self.egg = (x & 1) == 1
    self.ability = x >> 1
  
  def get_gender(self):
    genderRate = GENDER_RATE[self.species]
    if (genderRate == -1):
      self.gender = -1
      return
    if ((self.pid & 0xFF) < (genderRate * 32)):
      self.gender = 1
    else:
      self.gender = 0
    
  def get_stats(self):
    base_stats = STATS[self.species]
    self.stats = {
      "hp": math.floor(Pokemon.calc_stat(0, base_stats[0], self.ivs[0], self.evs[0], self.level, self.pid % 25)),
      "attack": math.floor(Pokemon.calc_stat(1, base_stats[1], self.ivs[1], self.evs[1], self.level, self.pid % 25)),
      "defense": math.floor(Pokemon.calc_stat(2, base_stats[2], self.ivs[2], self.evs[2], self.level, self.pid % 25)),
      "speed": math.floor(Pokemon.calc_stat(3, base_stats[3], self.ivs[3], self.evs[3], self.level, self.pid % 25)),
      "special_attack": math.floor(Pokemon.calc_stat(4, base_stats[4], self.ivs[4], self.evs[4], self.level, self.pid % 25)),
      "special_defense": math.floor(Pokemon.calc_stat(5, base_stats[5], self.ivs[5], self.evs[5], self.level, self.pid % 25))
    }
  
  @classmethod
  def calc_stat(cls, index, base_stat, iv, ev, level, nature):
    if (base_stat == 1):
      return 1
    if index == 0:
      return math.floor((base_stat * 2 + ev // 4 + iv) * level / 100) + level + 10
    else:
      natureBoost = 10
      if ((nature // 5) == (index - 1)):
        natureBoost += 1
      if ((nature % 5) == (index - 1)):
        natureBoost -= 1
      natureBoost = natureBoost / 10
      return math.floor((((base_stat * 2 + ev // 4 + iv) * level) // 100 + 5) * natureBoost)
  
  @classmethod
  def unpack(cls, data):
    personality_value, trainer_id = struct.unpack('<2I', data[0x0:0x8])
    nickname = readstring(struct.unpack('<10B',data[0x8:0x12]))
    language, flags = struct.unpack('<2B', data[0x12:0x14])
    ot_name = readstring(struct.unpack('<7B', data[0x14:0x1B]))
    markings = struct.unpack('<B', data[0x1B:0x1C])[0]
    checksum = struct.unpack('<H', data[0x1C:0x1E])[0]
    if personality_value == 0:
      return cls(0, 0, "", 0, 0, "", 0, 0, data[0x20:0x50], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    if len(data[0x50:0x64]) == 14:
      status, level, mail_id, current_hp, total_hp, attack, defense, speed, special_attack, special_defense = struct.unpack('<I2B7H', data[0x50:0x64])
    else:
      status, level, mail_id, current_hp, total_hp, attack, defense, speed, special_attack, special_defense = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    return cls(personality_value, trainer_id, nickname, language, flags, ot_name, markings, checksum, data[0x20:0x50], status, level, mail_id, current_hp, total_hp, attack, defense, speed, special_attack, special_defense)
  
  def __str__(self):
    return '\t\t'.join(f'\"{key}\": {"\"" if isinstance(value, str) else ""}{("true" if value else "false") if isinstance(value, bool) else json.dumps(value) if isinstance(value, dict) or isinstance(value, list) else value}{"\"" if isinstance(value, str) else ""},\n' for key, value in vars(self).items()).removesuffix(',\n') + '\n'
  
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