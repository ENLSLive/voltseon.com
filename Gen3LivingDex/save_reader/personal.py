import struct


data = []

def load_data():
  global data
  with open("personal/personal_e", "rb") as f:
    data = f.read()

load_data()

def get_pokemon(id):
  offset = 0x1C * id
  return data[offset:offset+0x1C]

def get_abilities(id):
  return struct.unpack('<BB', get_pokemon(id)[0x16:0x18])

def get_types(id):
  return struct.unpack('<BB', get_pokemon(id)[0x06:0x08])

def get_egg_groups(id):
  return struct.unpack('<BB', get_pokemon(id)[0x14:0x16])

def get_hatch_cycles(id):
  return struct.unpack('<B', get_pokemon(id)[0x11])

def get_base_exp(id):
  return struct.unpack('<B', get_pokemon(id)[0x09])