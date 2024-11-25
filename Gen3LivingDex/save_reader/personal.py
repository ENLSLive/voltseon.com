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