import re

with open('gallery.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace hardcoded gallery grid with dynamic container
container_html = """
<div id="dynamic-gallery-container" class="gallery-grid" style="margin-top:40px; margin-bottom:40px;">
  <div style="grid-column: 1 / -1; text-align:center; padding: 50px;">
    <i class="fa-solid fa-circle-notch fa-spin" style="font-size:2rem; color:var(--gold);"></i>
    <p style="margin-top:20px;">Loading gallery...</p>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async function() {
  try {
    const res = await fetch('/api/gallery');
    const data = await res.json();
    if (data.success && data.images.length > 0) {
      const container = document.getElementById('dynamic-gallery-container');
      
      let galleryHtml = '';
      data.images.forEach(img => {
        galleryHtml += `
        <div class="gallery-item">
          <img src="${img.image_url}" alt="${img.caption}" loading="lazy">
          <div class="gallery-overlay">
            <span class="gallery-caption">${img.caption}</span>
          </div>
        </div>
        `;
      });
      container.innerHTML = galleryHtml;
    } else if (data.success) {
      document.getElementById('dynamic-gallery-container').innerHTML = '<p style="grid-column: 1 / -1; text-align:center; padding:50px;">No images available in the gallery yet.</p>';
    }
  } catch(e) {
    console.error('Failed to load gallery', e);
  }
});
</script>
"""

# Replace from <div class="gallery-grid"> up to but not including <!-- CTA SECTION -->
html = re.sub(r'<div class="gallery-grid">.*?<!-- CTA SECTION -->', container_html + '\n\n<!-- CTA SECTION -->', html, flags=re.DOTALL)

with open('gallery.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated gallery.html for dynamic rendering.')
