const carousel = document.querySelector(".carousel");
const items = document.querySelectorAll(".carousel-item");
const leftButton = document.querySelector("#left-button");
const rightButton = document.querySelector("#right-button");
const carouselCaptions = document.querySelectorAll(".carousel-caption");
const coverText = document.getElementById("cover-text");
const navigationButtons = document.getElementById("navigation-buttons");
var viewingContent = false;

document.addEventListener("DOMContentLoaded", function () {
  let currentIndex = 0;
  let autoScrollInterval;

  // Function to update the carousel to show the current item
  const updateCarousel = () => {
    carousel.style.transform = `translateX(-${currentIndex * 100}%)`;
  };

  // Function to go to the next item in the carousel
  function nextSlide(force) {
    if (viewingContent && !force) return;

    clearInterval(autoScrollInterval); // Clear the autoscroll interval
    currentIndex = (currentIndex + 1) % items.length;
    updateCarousel();

    // Set a delay before allowing autoscroll again
    setTimeout(() => {
      startAutoScroll();
    }, 5000); // Delay of 5 seconds
  };

  // Function to go to the previous item in the carousel
  function prevSlide(force) {
    if (viewingContent && !force) return;

    clearInterval(autoScrollInterval); // Clear the autoscroll interval
    currentIndex = (currentIndex - 1 + items.length) % items.length;
    updateCarousel();

    // Set a delay before allowing autoscroll again
    setTimeout(() => {
      startAutoScroll();
    }, 5000); // Delay of 5 seconds
  };

  // Function to start autoscroll with a 3-second interval
  const startAutoScroll = () => {
    clearInterval(autoScrollInterval);
    autoScrollInterval = setInterval(() => {
      if (!viewingContent) {
        nextSlide();
      }
    }, 3000); // Autoscroll every 3 seconds
  };


  // Attach click event listeners to the buttons
  leftButton.addEventListener("click", function () { prevSlide(true); });
  rightButton.addEventListener("click", function () { nextSlide(true); });

  // Set up initial carousel position
  updateCarousel();
  carouselCaptions.forEach((caption) => {
    updateCaptions(caption, false);
  });
  startAutoScroll();
});

carousel.addEventListener("mouseover", function () {
  hoverOn();
});

coverText.addEventListener("mouseover", function () {
  hoverOn();
});

navigationButtons.addEventListener("mouseover", function () {
  hoverOn();
});

carousel.addEventListener("mouseout", function () {
  hoverOff();
});

coverText.addEventListener("mouseout", function () {
  hoverOff();
});

navigationButtons.addEventListener("mouseout", function () {
  hoverOff();
});


function hoverOn() {
  viewingContent = true;
  carouselCaptions.forEach((caption) => {
    updateCaptions(caption, true);
  });
  items.forEach((item) => {
    item.style.backgroundSize = "120%";
    item.style.boxShadow = "inset 0 0 0 10000px rgba(5, 0, 28, 0.3)";
  });
}

function hoverOff() {
  viewingContent = false;
  carouselCaptions.forEach((caption) => {
    updateCaptions(caption, false);
  });
  items.forEach((item) => {
    item.style.backgroundSize = "100%";
    item.style.boxShadow = "none";
  });
}

function updateCaptions(caption, show) {
  if (show) {
    caption.style.opacity = "1";
    caption.style.transform = "scaleY(1)";
    caption.style.backgroundSize = "150%";
  } else {
    caption.style.opacity = "0";
    caption.style.transform = "scaleY(0)";
    caption.style.backgroundSize = "100%";
  }
}