const natureBoosts = {
  "Lonely": ["attack", "defense"],
  "Brave": ["attack", "speed"],
  "Adamant": ["attack", "special_attack"],
  "Naughty": ["attack", "special_defense"],
  "Bold": ["defense", "attack"],
  "Relaxed": ["defense", "speed"],
  "Impish": ["defense", "special_attack"],
  "Lax": ["defense", "special_defense"],
  "Timid": ["speed", "attack"],
  "Hasty": ["speed", "defense"],
  "Jolly": ["speed", "special_attack"],
  "Naive": ["speed", "special_defense"],
  "Modest": ["special_attack", "attack"],
  "Mild": ["special_attack", "defense"],
  "Quiet": ["special_attack", "speed"],
  "Rash": ["special_attack", "special_defense"],
  "Calm": ["special_defense", "attack"],
  "Gentle": ["special_defense", "defense"],
  "Sassy": ["special_defense", "speed"],
  "Careful": ["special_defense", "special_attack"],
};

const maxValues = {
  ivs: 31,
  evs: 252
};

document.addEventListener("DOMContentLoaded", () => {
  const summaryPanel = document.getElementById("summaryPanel");
  const closeSummaryPanelBtn = document.getElementById("summaryClose");

  closeSummaryPanelBtn.addEventListener("click", () => {
    summaryPanel.style.display = "none";
  });

  const currentPokemon = JSON.parse(localStorage.getItem("currentPokemon"));
  if (currentPokemon) {
    updatePokemonInfoPanel(currentPokemon, false);
  }
  else {
    const firstPokemon = dex[0];
    updatePokemonInfoPanel(firstPokemon, false);
  }
});


function updatePokemonInfoPanel(pokemon, audio = true) {
  const dexId = document.getElementById("summaryNumber");
  const summaryname = document.getElementById("summaryName");
  const img = document.getElementById("summaryImg");
  const type1 = document.getElementById("type1");
  const type2 = document.getElementById("type2");
  const level = document.getElementById("summaryLevel");

  localStorage.setItem("currentPokemon", JSON.stringify(pokemon));
  //dexId.textContent = paddedSpeciesId(pokemon.species);
  level.textContent = `Lv. ${pokemon.level} `;
  summaryname.innerHTML = fullNameText(pokemon);
  const suffix = pokemon.unown_form ? `-${pokemon.unown_form.toLowerCase()}` : "";
  if (pokemon.shiny) {
    img.src = `assets/img/pokemon/anim_shiny/${pokemon.species}${suffix}.gif`;
    document.getElementById("shinyStar").style.display = "flex";
  } else {
    img.src = `assets/img/pokemon/anim/${pokemon.species}${suffix}.gif`;
    document.getElementById("shinyStar").style.display = "none";
  }
  if (pokemon.types.length === 1 || pokemon.types[1] === pokemon.types[0]) {
    type1.innerHTML = `<img src="/Gen3LivingDex/www/assets/img/types/${pokemon.types[0]}.webp">`;
    type2.innerHTML = '';
  } else {
    type1.innerHTML = `<img src="/Gen3LivingDex/www/assets/img/types/${pokemon.types[0]}.webp">`;
    type2.innerHTML = `<img src="/Gen3LivingDex/www/assets/img/types/${pokemon.types[1]}.webp">`;
  }
  setStats(pokemon);
  setAbility(pokemon.ability_name);
  setGender(pokemon.gender);
  setHeldItem(pokemon.item_name);
  setMoves(pokemon.moves);
  if (audio) {
    playCry(pokemon);
  }
  updateChart(pokemon);
  showSummaryPanel();
}

function paddedSpeciesId(speciesId) {
  return "#" + speciesId.toString().padStart(3, "0");
}

function fullNameText(pokemon) {
  if (pokemon.nickname === "" || pokemon.nickname === pokemon.species_name.toUpperCase()) {
    return pokemon.species_name.toUpperCase();
  }
  return `${pokemon.nickname}<br>${pokemon.species_name.toUpperCase()}`;
}

function setHeldItem(item) {
  const heldItem = document.getElementById("heldItem");
  const heldItemName = document.getElementById("heldItemName");
  if (item === "" || item === "(None)") {
    heldItem.firstChild.style.display = "none";
    heldItemName.textContent = "";
    return;
  }
  heldItem.firstChild.style.display = "flex";
  heldItemName.textContent = item;
  heldItem.firstChild.src = `/assets/img/items/${getItemId(item)}.png`;
}

function getItemId(item) {
  if (item.includes("TM")) {
    return "machine_NORMAL";
  }
  if (item.includes("HM")) {
    return "machine_hm_NORMAL";
  }
  return item.replace(/ /g, "").replace("'", "").toUpperCase();
}

function setGender(gender) {
  const genderIcon = document.getElementById('summaryGender');
  if (gender === 1) {
    genderIcon.classList.remove('summaryGender--male');
    genderIcon.classList.add('summaryGender--female');
    genderIcon.textContent = "♀";
  }
  else if (gender === 0) {
    genderIcon.classList.remove('summaryGender--female');
    genderIcon.classList.add('summaryGender--male');
    genderIcon.textContent = "♂";
  }
  else {
    genderIcon.classList.remove('summaryGender--male');
    genderIcon.classList.remove('summaryGender--female');
    genderIcon.textContent = "";
  }
}

function setStats(pokemon) {
  const statClasses = ["HP", "SPATK", "ATK", "SPDEF", "DEF", "SPEED"];
  const statNames = ["hp", "special_attack", "attack", "special_defense", "defense", "speed"];
  const natureElement = document.getElementById("nature");
  const natureBoost = natureBoosts[pokemon.nature];

  natureElement.textContent = pokemon.nature + " nature";
  
  for (let i = 0; i < 6; i++) {
    document.getElementById("summaryStat--" + statClasses[i]).textContent = pokemon.stats[statNames[i]];
    document.getElementById("summaryStat--" + statClasses[i]).classList.remove("summaryStat--boosted");
    document.getElementById("summaryStat--" + statClasses[i]).classList.remove("summaryStat--lowered");
    if (natureBoost === undefined) {
      continue;
    }
    if (natureBoost[0] === statNames[i]) {
      document.getElementById("summaryStat--" + statClasses[i]).classList.add("summaryStat--boosted");
    }
    else if (natureBoost[1] === statNames[i]) {
      document.getElementById("summaryStat--" + statClasses[i]).classList.add("summaryStat--lowered");
    }
    console.log(document.getElementById("summaryStat--" + statClasses[0]).textContent);
  }
}

function setAbility(ability) {
  const abilityElement = document.getElementById("abilityName");
  abilityElement.textContent = ability;
}

function setMoves(moves) {

  for (let i = 0; i < 4; i++) {
    const move = moves[i];
    if (move[0] !== "---") {
      const moveName = move[0];
      const moveType = move[3];
      const maxPp = move[2];
      const ppLeft = Math.min(move[1], maxPp);

      document.getElementById(`summaryMove${i + 1}`).innerHTML = `<div><img src="/Gen3LivingDex/www/assets/img/types/${moveType}.webp"><span>${moveName}</span></div><span>${ppLeft}/${maxPp}</span>`;
    }
    else {
      clearMove(i);
    }
  }
}

function clearMove(moveNumber) {
  document.getElementById(`summaryMove${moveNumber + 1}`).innerHTML = "<div><div style='width: 64px;'></div><span>-</span></div><span>--</span>";
}

function playCry(pokemon) {
  const cry = new Audio(`assets/cries/${pokemon.species}.ogg`);
  cry.volume = 0.5;
  cry.play();
  
  if (pokemon.shiny) {
    cry.addEventListener("loadedmetadata", () => {
      setTimeout(playShinySparkle, cry.duration * 800);
    });
  }
}

function playShinySparkle() {
  const sparkleGif = document.getElementById("summaryShinySparkle");
  sparkleGif.src = "/Gen3LivingDex/www/assets/img/shiny_sparkle.gif"
  sparkleGif.style.display = "flex";

  const sparkleSound = new Audio(`assets/cries/shiny_sparkle.ogg`);
  sparkleSound.volume = 0.25;
  sparkleSound.play();

  sparkleSound.addEventListener("ended", () => {
    sparkleGif.src = "";
    sparkleGif.style.display = "none";
  });
}

function showSummaryPanel() {
  const summaryPanel = document.getElementById("summaryPanel");
  const closeSummaryPanelBtn = document.getElementById("summaryClose");

  summaryPanel.style.display = "block";
  closeSummaryPanelBtn.focus();
}


function isMobile() {
  return window.innerWidth <= 840;
}

window.addEventListener("resize", () => {
  if (isMobile()) {
    document.getElementById("summaryPanel").style.display = "none";
  }
  else {
    document.getElementById("summaryPanel").style.display = "block";
  }
});

function updateChart(pokemon) {
  const hexagonData = document.getElementById('summaryEvIv');

  const currentView = localStorage.getItem("currentView") || "ivs";
  const currentStats = Object.assign([], pokemon[currentView]);
  const temp = currentStats[currentStats.length - 1];
  currentStats[currentStats.length - 1] = currentStats[currentStats.length - 2];
  currentStats[currentStats.length - 2] = temp;
  const maxValue = maxValues[currentView];

  const clipPathPoints = currentStats.map((value, index) => {
    const percentage = value / maxValue;
    const minOffset = 4;
    const minOffsetDiag = Math.round(minOffset / 2);
    const minimum = 50 - minOffset;
    const minimumDiag = 50 - minOffsetDiag;
    switch (index) {
      case 0:
        return `50% ${minimum - percentage * minimum}%`;
      case 1:
        return `${50 + minOffsetDiag + percentage * minimumDiag}% ${minimumDiag - percentage * (25 - minOffsetDiag)}%`;
      case 2:
        return `${50 + minOffsetDiag + percentage * minimumDiag}% ${50 + minOffsetDiag + percentage * (25 - minOffsetDiag)}%`;
      case 3:
        return `50% ${50 + minOffset + percentage * (50 - minOffset)}%`;
      case 4:
        return `${minimumDiag - percentage * minimumDiag}% ${50 + minOffsetDiag + percentage * (25 - minOffsetDiag)}%`;
      case 5:
        return `${minimumDiag - percentage * minimumDiag}% ${minimumDiag - percentage * (25 - minOffsetDiag)}%`;
    }
  }).join(', ');

  hexagonData.style.clipPath = `polygon(${clipPathPoints})`;
  hexagonData.style.backgroundColor = currentView === "ivs" ? "#E8A0F8" : "#58D878";

  const currentIvEv = document.getElementById("currentIvEv");
  currentIvEv.innerHTML = currentView.toUpperCase().replace("S", "'s");
}

function toggleView() {
  const currentView = localStorage.getItem("currentView");
  localStorage.setItem("currentView", currentView === "ivs" ? "evs" : "ivs");

  const currentPokemon = JSON.parse(localStorage.getItem("currentPokemon"));
  if (currentPokemon) {
    updateChart(currentPokemon);
  }
}