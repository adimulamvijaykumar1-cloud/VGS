import re

with open('gallery.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the old container script with the new one that supports Categories and Lightbox
new_js_and_html = """
<style>
/* Category Filters */
.gallery-filters {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 30px;
}
.filter-btn {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}
.filter-btn.active, .filter-btn:hover {
  background: var(--gold);
  color: var(--navy);
  border-color: var(--gold);
}

/* New Dynamic Lightbox */
.dynamic-lightbox {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}
.dynamic-lightbox.show {
  opacity: 1;
  pointer-events: auto;
}
.dl-content {
  position: relative;
  max-width: 90%;
  max-height: 90%;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.dl-img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.dl-caption {
  color: white;
  margin-top: 15px;
  font-size: 1.2rem;
  text-align: center;
}
.dl-close {
  position: absolute;
  top: 20px; right: 20px;
  color: white;
  font-size: 30px;
  cursor: pointer;
  z-index: 10000;
}
.dl-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  color: white;
  font-size: 40px;
  cursor: pointer;
  user-select: none;
  padding: 20px;
  transition: 0.2s;
}
.dl-nav:hover { color: var(--gold); }
.dl-prev { left: 10px; }
.dl-next { right: 10px; }
</style>

<div class="container">
  <div class="gallery-filters" id="gallery-filters">
    <!-- Buttons generated via JS -->
  </div>
</div>

<div id="dynamic-gallery-container" class="gallery-grid" style="margin-top:10px; margin-bottom:40px;">
  <div style="grid-column: 1 / -1; text-align:center; padding: 50px;">
    <i class="fa-solid fa-circle-notch fa-spin" style="font-size:2rem; color:var(--gold);"></i>
    <p style="margin-top:20px;">Loading gallery...</p>
  </div>
</div>

<!-- Lightbox Element -->
<div class="dynamic-lightbox" id="dynamic-lightbox">
  <i class="fa-solid fa-xmark dl-close" id="dl-close"></i>
  <i class="fa-solid fa-chevron-left dl-nav dl-prev" id="dl-prev"></i>
  <i class="fa-solid fa-chevron-right dl-nav dl-next" id="dl-next"></i>
  <div class="dl-content">
    <img src="" class="dl-img" id="dl-img">
    <div class="dl-caption" id="dl-caption"></div>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async function() {
  let allImages = [];
  let currentFilteredImages = [];
  let currentIndex = 0;

  try {
    const res = await fetch('/api/gallery');
    const data = await res.json();
    if (data.success && data.images.length > 0) {
      allImages = data.images;
      
      // Extract unique categories
      const categories = ['All', ...new Set(allImages.map(img => img.category || 'All').filter(c => c !== 'All'))];
      
      // Render Filter Buttons
      const filterContainer = document.getElementById('gallery-filters');
      filterContainer.innerHTML = categories.map(cat => 
        `<button class="filter-btn ${cat === 'All' ? 'active' : ''}" data-cat="${cat}">${cat}</button>`
      ).join('');

      // Add Filter Event Listeners
      document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
          e.target.classList.add('active');
          const selectedCat = e.target.getAttribute('data-cat');
          renderGallery(selectedCat);
        });
      });

      // Initial Render
      renderGallery('All');

    } else if (data.success) {
      document.getElementById('dynamic-gallery-container').innerHTML = '<p style="grid-column: 1 / -1; text-align:center; padding:50px;">No images available in the gallery yet.</p>';
    }
  } catch(e) {
    console.error('Failed to load gallery', e);
  }

  function renderGallery(category) {
    currentFilteredImages = category === 'All' ? allImages : allImages.filter(img => (img.category || 'All') === category);
    
    const container = document.getElementById('dynamic-gallery-container');
    if (currentFilteredImages.length === 0) {
      container.innerHTML = '<p style="grid-column: 1 / -1; text-align:center; padding:50px;">No images in this category.</p>';
      return;
    }

    container.innerHTML = currentFilteredImages.map((img, index) => `
      <div class="gallery-item" onclick="openLightbox(${index})" style="cursor:pointer;">
        <img src="${img.image_url}" alt="${img.caption}" loading="lazy">
        <div class="gallery-overlay">
          <span class="gallery-caption">${img.caption || ''}</span>
        </div>
      </div>
    `).join('');
  }

  // Lightbox Logic
  const lightbox = document.getElementById('dynamic-lightbox');
  const lbImg = document.getElementById('dl-img');
  const lbCap = document.getElementById('dl-caption');

  window.openLightbox = function(index) {
    currentIndex = index;
    updateLightbox();
    lightbox.classList.add('show');
  };

  function updateLightbox() {
    if(currentFilteredImages.length === 0) return;
    const img = currentFilteredImages[currentIndex];
    lbImg.src = img.image_url;
    lbCap.textContent = img.caption || '';
  }

  document.getElementById('dl-close').addEventListener('click', () => lightbox.classList.remove('show'));
  
  document.getElementById('dl-prev').addEventListener('click', (e) => {
    e.stopPropagation();
    currentIndex = (currentIndex > 0) ? currentIndex - 1 : currentFilteredImages.length - 1;
    updateLightbox();
  });
  
  document.getElementById('dl-next').addEventListener('click', (e) => {
    e.stopPropagation();
    currentIndex = (currentIndex < currentFilteredImages.length - 1) ? currentIndex + 1 : 0;
    updateLightbox();
  });

  // Close when clicking outside image
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) lightbox.classList.remove('show');
  });

  // Keyboard support
  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('show')) return;
    if (e.key === 'Escape') lightbox.classList.remove('show');
    if (e.key === 'ArrowLeft') document.getElementById('dl-prev').click();
    if (e.key === 'ArrowRight') document.getElementById('dl-next').click();
  });
});
</script>
"""

# Replace the existing dynamic script injection
html = re.sub(r'<div id="dynamic-gallery-container".*?</script>', new_js_and_html, html, flags=re.DOTALL)

with open('gallery.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated gallery.html with Categories and Lightbox')
