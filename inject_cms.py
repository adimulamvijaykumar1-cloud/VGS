import glob
import re

html_files = glob.glob('*.html')
html_files = [f for f in html_files if f != 'admin.html'] # Don't inject into admin

# The CMS javascript
cms_js = """
<!-- ===================== DYNAMIC CMS INTEGRATION ===================== -->
<script>
document.addEventListener('DOMContentLoaded', async function() {
  try {
    const res = await fetch('/api/settings');
    const data = await res.json();
    if (data.success && data.settings) {
      
      // Update Phone Numbers
      const phoneNodes = document.querySelectorAll('.cms-phone');
      phoneNodes.forEach(node => {
        if (node.tagName === 'A') node.href = 'tel:' + data.settings.phone;
        else node.textContent = data.settings.phone;
      });
      
      const phoneTextNodes = document.querySelectorAll('.cms-phone-text');
      phoneTextNodes.forEach(node => {
        node.textContent = data.settings.phone;
      });

      // Update Instagram Links
      const instaNodes = document.querySelectorAll('.cms-instagram');
      instaNodes.forEach(node => {
        if (node.tagName === 'A') node.href = data.settings.instagram;
      });

      // Update Location
      const locNodes = document.querySelectorAll('.cms-location');
      locNodes.forEach(node => {
        node.textContent = data.settings.location;
      });

      // Update Nav Brand Logo / Favicon
      const navIconNodes = document.querySelectorAll('.cms-nav-icon');
      navIconNodes.forEach(node => {
        if (node.tagName === 'IMG') {
          node.src = data.settings.nav_icon;
        } else {
          // It's the span.brand-mark, replace it with an image if it's an image URL, or keep text if it's just a letter
          if (data.settings.nav_icon.startsWith('http') || data.settings.nav_icon.startsWith('data:image')) {
            node.innerHTML = `<img src="${data.settings.nav_icon}" style="width:100%; height:100%; object-fit:contain;">`;
            node.style.background = 'transparent';
            node.style.border = 'none';
          } else {
            node.textContent = data.settings.nav_icon.charAt(0);
          }
        }
      });
    }
  } catch(e) { console.error('CMS Settings Fetch Failed', e); }
});
</script>
</body>
"""

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Inject cms.js before </body>
    if 'DYNAMIC CMS INTEGRATION' not in content:
        content = content.replace('</body>', cms_js)

    # 2. Add classes to Phone links and text
    content = content.replace('<a href="tel:9963736363"', '<a href="tel:9963736363" class="cms-phone"')
    content = content.replace('<span>9963736363</span>', '<span class="cms-phone-text">9963736363</span>')
    
    # 3. Add classes to Instagram links
    content = content.replace('<a href="https://instagram.com/vgsacademyofficial"', '<a href="https://instagram.com/vgsacademyofficial" class="cms-instagram"')
    
    # 4. Add classes to Location text
    content = content.replace('<span>Jammi Chettu Veedhi, Near Sloka School, Vempalli</span>', '<span class="cms-location">Jammi Chettu Veedhi, Near Sloka School, Vempalli</span>')
    
    # 5. Add classes to Nav icon
    content = content.replace('<span class="brand-mark">V</span>', '<span class="brand-mark cms-nav-icon">V</span>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Injected cms.js into public HTML files and updated CMS classes.')
