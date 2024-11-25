from structs import *
import struct
import os
from personal import *

# https://projectpokemon.org/home/forums/topic/37630-pokemon-box-ramps-save-file-structure-research-research-complete/
# https://github.com/VitHuang/PokemonBoxSaveEditor/blob/054e9878a89fb385e9b8aaf72256107a4f758981/PokemonBoxRSSaveEditor/mainwindow.cpp
# https://docs.python.org/2/library/struct.html#format-characters
# https://github.com/ads04r/Gen3Save/blob/master/pokemondata/Gen3Pokemon.py
# https://calculator.name/baseconvert/decimal/hexadecimal

# Constants
SAVE_FILE = "save.gci"
SAVE_SIZE = 0x76000
GCI_OFFSET = 0x40

def unpack_save(save_path):
  # Read the save file
  with open(save_path, 'rb') as f:
    save_data = f.read()

  # Offset the save data if it's a GCI file
  if (len(save_data) == SAVE_SIZE + GCI_OFFSET):
    save_data = save_data[GCI_OFFSET:]

  # Stores the save slots
  save_slots = []
  used_slots = []
  for i in range(23):
    used_slots.append(None)

  # Unpack the save slots and store them
  for i in range(58):
    save_block = DataStructure.unpack(save_data[0x02000 + (0x2000 * i):0x02000 + (0x2000 * (i+1))])
    save_slots.append(save_block)

  # Decide which save slot to use
  valid_a = True
  valid_b = True

  save_count_a = save_slots[0].save_count
  save_count_b = save_slots[23].save_count
  
  for i in range(23):
    if (not save_slots[i].valid) or (save_slots[i].save_count != save_count_a):
      valid_a = False
    if (not save_slots[i+23].valid) or (save_slots[i+23].save_count != save_count_b):
      valid_b = False

  print(f"Save count A: {save_count_a}")
  print(f"Save count B: {save_count_b}")
  
  print(f"Save slot A valid: {valid_a}")
  print(f"Save slot B valid: {valid_b}")

  # Use the save slot with the most valid data
  if (valid_a and ((not valid_b) or save_count_a > save_count_b)):
    print("Using save slot A.")
    for i in range(23):
      used_slots[save_slots[i].block_id] = save_slots[i]
  elif (valid_b):
    print("Using save slot B.")
    for i in range(23):
      used_slots[save_slots[i + 23].block_id] = save_slots[i + 23]
  else:
    print("No valid save slots found.")
    return

  # Stores the box data
  box_data = b''

  # Append the actual data of each save slot to the box data
  for i in range(22):
    #print(used_slots[i].actual_data[0:128])
    box_data += used_slots[i].actual_data

  # Unpack the box data
  boxes = PokemonBoxData.unpack(box_data)

  # Write the box data
  f = open("dex.json", "w", encoding='utf-8')
  f.write(boxes.get_all_pokemon())
  f.close()

def main():
  unpack_save(SAVE_FILE)

if __name__ == '__main__':
  main()