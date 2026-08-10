import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

# I will append the JS for tabs and CMS to the end of the existing JS block.
cms_js = """
    // --- Tabs Navigation ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const pageTitle = document.getElementById('page-title');
    
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        navItems.forEach(n => n.classList.remove('active'));
        tabPanes.forEach(t => t.classList.remove('active'));
        
        item.classList.add('active');
        const target = document.getElementById(item.dataset.target);
        if(target) target.classList.add('active');
        
        pageTitle.textContent = item.textContent.trim();
        
        // Fetch data based on tab
        if (item.dataset.target === 'tab-settings') fetchSettings();
        if (item.dataset.target === 'tab-courses') fetchAdminCourses();
        if (item.dataset.target === 'tab-gallery') fetchAdminGallery();
      });
    });

    // --- Settings Management ---
    const settingsForm = document.getElementById('settings-form');
    async function fetchSettings() {
      try {
        const res = await fetch(`${API_BASE}/api/settings`);
        const data = await res.json();
        if (data.success) {
          document.getElementById('setting-phone').value = data.settings.phone || '';
          document.getElementById('setting-instagram').value = data.settings.instagram || '';
          document.getElementById('setting-location').value = data.settings.location || '';
          document.getElementById('setting-navicon').value = data.settings.nav_icon || '';
        }
      } catch(e) { console.error('Error fetching settings', e); }
    }

    settingsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const res = await fetch(`${API_BASE}/api/admin/settings`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            phone: document.getElementById('setting-phone').value,
            instagram: document.getElementById('setting-instagram').value,
            location: document.getElementById('setting-location').value,
            nav_icon: document.getElementById('setting-navicon').value
          })
        });
        const data = await res.json();
        if (data.success) showToast('Settings saved successfully!');
        else showToast('Error saving settings', 'danger');
      } catch (error) { showToast('Network error', 'danger'); }
    });

    // --- Courses Management ---
    async function fetchAdminCourses() {
      try {
        const res = await fetch(`${API_BASE}/api/courses`);
        const data = await res.json();
        const list = document.getElementById('courses-list');
        if (data.success) {
          if(data.courses.length === 0) {
            list.innerHTML = `<div class="no-data">No courses found. Add one!</div>`;
            return;
          }
          list.innerHTML = data.courses.map(c => `
            <div style="background: rgba(255,255,255,0.05); border: 1px solid var(--border-color); padding: 15px; border-radius: 8px; display:flex; justify-content:space-between; align-items:center;">
              <div>
                <h4 style="margin:0; color:var(--gold);">${c.title}</h4>
                <div style="font-size:12px; color:#aaa; margin-top:4px;">${c.subtitle}</div>
              </div>
              <button class="btn btn-outline-danger btn-sm" onclick="deleteCourse(${c.id})"><i class="fa-solid fa-trash"></i> Delete</button>
            </div>
          `).join('');
        }
      } catch(e) { console.error(e); }
    }

    document.getElementById('btn-add-course').addEventListener('click', async () => {
      const title = prompt("Course Title:");
      if (!title) return;
      const subtitle = prompt("Subtitle:");
      const description = prompt("Description:");
      const icon = prompt("FontAwesome Icon Class (e.g. fa-solid fa-book):", "fa-solid fa-book");
      const bullets = prompt("Bullets (comma separated):");
      const badge_num = prompt("Badge Number (e.g. 6-10):");
      const badge_text = prompt("Badge Text (e.g. Grade Levels):");

      try {
        const res = await fetch(`${API_BASE}/api/admin/courses`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ title, subtitle, description, icon, bullets, badge_num, badge_text })
        });
        const data = await res.json();
        if (data.success) {
          showToast('Course added!');
          fetchAdminCourses();
        }
      } catch(e) { showToast('Error adding course', 'danger'); }
    });

    window.deleteCourse = async (id) => {
      if(!confirm("Delete this course?")) return;
      try {
        const res = await fetch(`${API_BASE}/api/admin/courses/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
          showToast('Course deleted!');
          fetchAdminCourses();
        }
      } catch(e) { showToast('Error deleting course', 'danger'); }
    };

    // --- Gallery Management ---
    async function fetchAdminGallery() {
      try {
        const res = await fetch(`${API_BASE}/api/gallery`);
        const data = await res.json();
        const list = document.getElementById('gallery-list');
        if (data.success) {
          if(data.images.length === 0) {
            list.innerHTML = `<div class="no-data" style="grid-column: 1 / -1;">No images found. Add one!</div>`;
            return;
          }
          list.innerHTML = data.images.map(img => `
            <div style="position:relative; background: rgba(255,255,255,0.05); border: 1px solid var(--border-color); border-radius: 8px; overflow:hidden;">
              <img src="${img.image_url}" style="width:100%; height:150px; object-fit:cover; display:block;">
              <div style="padding:10px; font-size:12px; text-align:center;">${img.caption || 'No caption'}</div>
              <button onclick="deleteGalleryImage(${img.id})" style="position:absolute; top:5px; right:5px; background:var(--danger); color:#fff; border:none; border-radius:4px; padding:4px 8px; cursor:pointer;"><i class="fa-solid fa-trash"></i></button>
            </div>
          `).join('');
        }
      } catch(e) { console.error(e); }
    }

    document.getElementById('btn-add-gallery').addEventListener('click', async () => {
      const image_url = prompt("Image URL:");
      if (!image_url) return;
      const caption = prompt("Caption (optional):");

      try {
        const res = await fetch(`${API_BASE}/api/admin/gallery`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ image_url, caption })
        });
        const data = await res.json();
        if (data.success) {
          showToast('Image added!');
          fetchAdminGallery();
        }
      } catch(e) { showToast('Error adding image', 'danger'); }
    });

    window.deleteGalleryImage = async (id) => {
      if(!confirm("Delete this image?")) return;
      try {
        const res = await fetch(`${API_BASE}/api/admin/gallery/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
          showToast('Image deleted!');
          fetchAdminGallery();
        }
      } catch(e) { showToast('Error deleting image', 'danger'); }
    };
"""

admin_html = admin_html.replace('</script>\n</body>', cms_js + '\n  </script>\n</body>')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

print('Updated admin.html with CMS Javascript.')
