// Language Toggle Functionality
const languageMenu = document.getElementById('language-menu');
let isLanguageMenuOpen = false;

function toggleLanguageMenu() {
  if (isLanguageMenuOpen) {
    languageMenu.style.display = 'none';
  } else {
    languageMenu.style.display = 'block';
  }
  isLanguageMenuOpen = !isLanguageMenuOpen;
}

// Close language menu when clicking outside
document.addEventListener('click', function(event) {
  const isClickInsideMenu = languageMenu.contains(event.target);
  const isClickOnToggle = document.getElementById('lang-toggle').contains(event.target);
  
  if (!isClickInsideMenu && !isClickOnToggle && isLanguageMenuOpen) {
    languageMenu.style.display = 'none';
    isLanguageMenuOpen = false;
  }
});

// Language Selection
function selectLanguage(lang) {
  document.body.setAttribute('data-lang', lang);
  
  // Update label text based on selected language
  const langLabels = {
    'en': 'العربية',
    'ar': 'English',
    'fr': 'العربية',
    'tr': 'العربية',
    'bn': 'العربية',
    'hi': 'العربية',
    'id': 'العربية',
    'fil': 'العربية',
    'ur': 'English'
  };
  
  document.getElementById('lang-label').textContent = langLabels[lang];
  
  // Update text content based on data attributes
  updateTextContent(lang);
  
  // Close the language menu
  languageMenu.style.display = 'none';
  isLanguageMenuOpen = false;
}

// Update text content for all elements with data-{lang} attributes
function updateTextContent(lang) {
  const elements = document.querySelectorAll(`[data-${lang}]`);
  
  elements.forEach(element => {
    const text = element.getAttribute(`data-${lang}`);
    if (text) {
      element.textContent = text;
    }
  });
}

// Map Tabs Functionality
function showMap(mapType, event) {
  // Hide all map frames
  const mapFrames = document.querySelectorAll('.map-frame');
  mapFrames.forEach(frame => {
    frame.style.display = 'none';
  });
  
  // Show the selected map frame
  const selectedFrame = document.querySelector(`.map-frame[data-map="${mapType}"]`);
  if (selectedFrame) {
    selectedFrame.style.display = 'block';
  }
  
  // Update active tab
  if (event) {
    const tabs = document.querySelectorAll('.map-tab');
    tabs.forEach(tab => {
      tab.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
  }
}

// Initialize with English language on page load
document.addEventListener('DOMContentLoaded', function() {
  // Set initial language
  const initialLang = 'en';
  document.body.setAttribute('data-lang', initialLang);
  
  // Update text content for initial language
  updateTextContent(initialLang);
  
  // Set initial map
  showMap('makkah');
})