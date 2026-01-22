// ============================================
// Translations
// ============================================
const translations = {
    en: {
        pageTitle: 'The Sims 4 Save Helper - Download',
        tagline: 'Never lose your progress again',
        description: 'A simple utility that automatically reminds you to save your game at regular intervals. Since The Sims 4 doesn\'t have auto-save, this helper presses a key (like Escape) periodically to open the save menu and remind you to save.',
        downloadTitle: 'Download',
        checkingVersion: 'Checking for latest version...',
        downloadFor: 'Download for',
        downloadNote: '<strong>Windows:</strong> Download and run the .exe file directly.<br><strong>macOS:</strong> Unzip and move the app to your Applications folder.',
        screenshotTitle: 'Simple and Easy to Use',
        featuresTitle: 'Features',
        feature1: '<strong>Auto-detects The Sims 4</strong> - Only runs when the game is active',
        feature2: '<strong>Configurable intervals</strong> - From 1 second to 30 minutes',
        feature3: '<strong>Multiple key options</strong> - Escape, F5, F9, Ctrl+S, and more',
        feature4: '<strong>Test mode</strong> - Verify it works without the game running',
        feature5: '<strong>Remembers settings</strong> - Your preferences are saved automatically',
        viewOnGithub: 'View on GitHub',
        allReleases: 'All Releases',
        copyright: 'Open source software. Free to use.',
        released: 'Released',
        noReleases: 'No releases available yet. Check back soon!',
        fetchError: 'Unable to fetch the latest release. Please try again later.',
        viewAllReleases: 'View all releases on GitHub'
    },
    da: {
        pageTitle: 'The Sims 4 Save Helper - Download',
        tagline: 'Mist aldrig dine fremskridt igen',
        description: 'Et simpelt værktøj der automatisk minder dig om at gemme dit spil med jævne mellemrum. Da The Sims 4 ikke har auto-gem, trykker denne hjælper på en tast (som Escape) periodisk for at åbne gem-menuen og minde dig om at gemme.',
        downloadTitle: 'Download',
        checkingVersion: 'Søger efter seneste version...',
        downloadFor: 'Download til',
        downloadNote: '<strong>Windows:</strong> Download og kør .exe filen direkte.<br><strong>macOS:</strong> Pak ud og flyt appen til mappen Programmer.',
        screenshotTitle: 'Simpel og nem at bruge',
        featuresTitle: 'Funktioner',
        feature1: '<strong>Finder automatisk The Sims 4</strong> - Kører kun når spillet er aktivt',
        feature2: '<strong>Indstillelige intervaller</strong> - Fra 1 sekund til 30 minutter',
        feature3: '<strong>Flere tastevalg</strong> - Escape, F5, F9, Ctrl+S, og mere',
        feature4: '<strong>Testtilstand</strong> - Test uden at spillet kører',
        feature5: '<strong>Husker indstillinger</strong> - Dine præferencer gemmes automatisk',
        viewOnGithub: 'Se på GitHub',
        allReleases: 'Alle udgivelser',
        copyright: 'Open source software. Gratis at bruge.',
        released: 'Udgivet',
        noReleases: 'Ingen udgivelser tilgængelige endnu. Kom tilbage snart!',
        fetchError: 'Kunne ikke hente seneste udgivelse. Prøv igen senere.',
        viewAllReleases: 'Se alle udgivelser på GitHub'
    }
};

// Current language
let currentLang = 'en';

/**
 * Detect browser language and return 'da' for Danish, 'en' for everything else
 */
function detectLanguage() {
    const browserLang = navigator.language || navigator.userLanguage || 'en';
    // Check if Danish (da, da-DK, etc.)
    if (browserLang.toLowerCase().startsWith('da')) {
        return 'da';
    }
    return 'en';
}

/**
 * Get a translation string
 */
function t(key) {
    return translations[currentLang][key] || translations.en[key] || key;
}

/**
 * Apply translations to all elements with data-i18n attributes
 */
function applyTranslations() {
    // Update document language
    document.documentElement.lang = currentLang;
    
    // Update page title
    document.title = t('pageTitle');
    
    // Update text content
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.textContent = t(key);
    });
    
    // Update HTML content (for elements with formatting)
    document.querySelectorAll('[data-i18n-html]').forEach(el => {
        const key = el.getAttribute('data-i18n-html');
        el.innerHTML = t(key);
    });
    
    // Update active language button
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === currentLang);
    });
}

/**
 * Set language and save preference
 */
function setLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        localStorage.setItem('preferred-language', lang);
        applyTranslations();
    }
}

/**
 * Initialize language switcher
 */
function initLanguageSwitcher() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            setLanguage(btn.dataset.lang);
        });
    });
}

/**
 * Initialize localization
 */
function initLocalization() {
    // Check for saved preference, otherwise detect from browser
    const savedLang = localStorage.getItem('preferred-language');
    currentLang = savedLang || detectLanguage();
    
    applyTranslations();
    initLanguageSwitcher();
}

// ============================================
// GitHub Release Fetching
// ============================================
const REPO_OWNER = 'Topping';
const REPO_NAME = 'sims4-saver';
const API_URL = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/releases/latest`;
const RELEASES_URL = `https://github.com/${REPO_OWNER}/${REPO_NAME}/releases`;

// DOM elements
const versionInfo = document.getElementById('version-info');
const windowsBtn = document.getElementById('download-windows');
const macosBtn = document.getElementById('download-macos');

/**
 * Format a date string to a human-readable format based on current language
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const locale = currentLang === 'da' ? 'da-DK' : 'en-US';
    return date.toLocaleDateString(locale, {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Find an asset by file extension
 */
function findAsset(assets, extension) {
    return assets.find(asset => asset.name.toLowerCase().endsWith(extension));
}

/**
 * Enable a download button with the given URL
 */
function enableButton(button, url) {
    button.href = url;
    button.classList.remove('disabled');
    button.removeAttribute('aria-disabled');
}

/**
 * Show an error message with fallback to releases page
 */
function showError(message) {
    versionInfo.innerHTML = `
        <div class="error-message">
            <p>${message}</p>
            <p><a href="${RELEASES_URL}" target="_blank" rel="noopener">${t('viewAllReleases')}</a></p>
        </div>
    `;
    
    // Enable buttons to point to releases page as fallback
    windowsBtn.href = RELEASES_URL;
    macosBtn.href = RELEASES_URL;
    windowsBtn.classList.remove('disabled');
    macosBtn.classList.remove('disabled');
}

/**
 * Fetch the latest release from GitHub API and update download links
 */
async function fetchLatestRelease() {
    try {
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            if (response.status === 404) {
                showError(t('noReleases'));
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
            return;
        }
        
        const release = await response.json();
        
        // Update version info
        const version = release.tag_name || release.name;
        const publishedDate = formatDate(release.published_at);
        versionInfo.innerHTML = `
            <span class="version">${version}</span> &bull; ${t('released')} ${publishedDate}
        `;
        
        // Find Windows and macOS assets
        const windowsAsset = findAsset(release.assets, '.exe');
        const macosAsset = findAsset(release.assets, '.zip');
        
        // Enable download buttons
        if (windowsAsset) {
            enableButton(windowsBtn, windowsAsset.browser_download_url);
        } else {
            windowsBtn.href = RELEASES_URL;
            windowsBtn.classList.remove('disabled');
        }
        
        if (macosAsset) {
            enableButton(macosBtn, macosAsset.browser_download_url);
        } else {
            macosBtn.href = RELEASES_URL;
            macosBtn.classList.remove('disabled');
        }
        
    } catch (error) {
        console.error('Failed to fetch release:', error);
        showError(t('fetchError'));
    }
}

// ============================================
// Initialization
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initLocalization();
    fetchLatestRelease();
});
