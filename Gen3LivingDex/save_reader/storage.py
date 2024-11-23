order = DATA_ORDER[personality_value % 24]
self.species, self.item, self.exp, self.pp, self.friendship, self._unused = struct.unpack('<HHIBBH', data[order[0]:order[0]+12])
self.species = to_hex(self.species)
self.moves = []
for i in range(4):
  move = struct.unpack('<H', data[order[1]+i*2:order[1]+2+i*2])[0]
  self.moves.append(move)
self.evs = struct.unpack('<6B', data[order[2]:order[2]+6])
self.contest_stats = struct.unpack('<6B', data[order[2]+6:order[2]+12])
self.pokerus, self.met_location, self.origin, self.iv_egg_ability, self.ribbons_obedience = struct.unpack('<2BH2I', data[order[3]:order[3]+12])