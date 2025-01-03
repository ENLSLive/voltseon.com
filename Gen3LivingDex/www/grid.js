fetch("data/dex.json")
  .then(response => response.json())
  .then(data => {
    initPokemonGrid(data);
  });

var dex = []

function createGridContainer() {
  const gridContainer = document.createElement("div");
  gridContainer.classList.add("pokemon-grid");
  document.getElementById("gridPanel").appendChild(gridContainer);
  return gridContainer;
}

function createGridItem(pokemon) {
  const gridItem = document.createElement("div");
  gridItem.classList.add("pokemon-grid-item");
  if (pokemon !== null) {
    const suffix = pokemon.unown_form ? `-${pokemon.unown_form.toLowerCase()}` : "";
    const speciesId = pokemon.species
    if (speciesId == 0) {
      return gridItem;
    }
    var img = document.createElement("img");
    img.src = `assets/img/pokemon/icons/${speciesId}${suffix}.gif`;
    img.dataset.speciesId = speciesId;
    img.addEventListener("mouseover", function() {
      var paddedSpeciesId = speciesId.toString().padStart(3, "0");
      img.src = `assets/img/pokemon/icons_gif/${paddedSpeciesId}${suffix}.gif`;
    });
    img.addEventListener("mouseout", function() {
      img.src = `assets/img/pokemon/icons/${speciesId}${suffix}.gif`;
    });
    img.addEventListener("click", function() {
      // Update the Pokemon Info Panel (in summary.js)
      console.log(pokemon);
      updatePokemonInfoPanel(pokemon);
    });
    gridItem.style.cursor = "pointer";
    gridItem.appendChild(img);
  }
  return gridItem;
}

function populateGrid(gridContainer, data, sortBy = 'boxOrder') { // Default sort by boxOrder
  const sortedData = Object.entries(data).sort((a, b) => {
    if (sortBy === 'speciesId') {
      return a[1].species - b[1].species;
    } else if (sortBy === 'boxOrder') {
      return parseInt(a[0]) - parseInt(b[0]);
    }
  });

  if (sortBy === 'speciesId') {
    const maxSpeciesId = Math.max(...Object.values(data).map(pokemon => pokemon.species));
    for (let i = 1; i <= maxSpeciesId; i++) {
      const pokemon = sortedData.find(entry => entry[1].species === i);
      const gridItem = createGridItem(pokemon ? pokemon[1] : null);
      gridContainer.appendChild(gridItem);
    }
  } else if (sortBy === 'boxOrder') {
    sortedData.forEach(entry => {      
      const gridItem = createGridItem(entry[1]);
      gridContainer.appendChild(gridItem);
    });
  }
  dex = sortedData;
  console.log(dex);
}

function initPokemonGrid(data) {
  const sortOptions = document.createElement("select");
  sortOptions.id = "sortOptions";
  sortOptions.innerHTML = `
  <option value="boxOrder">Box Order</option>
  <option value="speciesId">National Dex Order</option>
  `;
  document.getElementById("headerBar").appendChild(sortOptions);

  sortOptions.addEventListener("change", function() {
    document.querySelector(".pokemon-grid").remove();
    const gridContainer = createGridContainer();
    populateGrid(gridContainer, data, this.value);
  });

  const gridContainer = createGridContainer();
  populateGrid(gridContainer, data);
}