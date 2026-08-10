import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Manage Categories button
html = html.replace(
    '<button class="btn btn-warning" id="btn-open-gallery-modal"><i class="fa-solid fa-plus"></i> Add Image URL</button>',
    '<div style="display:flex; gap:10px;"><button class="btn btn-outline-light" id="btn-open-categories-modal"><i class="fa-solid fa-folder-open"></i> Manage Categories</button><button class="btn btn-warning" id="btn-open-gallery-modal"><i class="fa-solid fa-plus"></i> Add Image URL</button></div>'
)

# 2. Add Categories Modal HTML right after gallery-modal
cat_modal = '''
          <!-- Manage Categories Modal -->
          <div id="categories-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; justify-content:center; align-items:center;">
            <div style="background:var(--navy-light); padding:30px; border-radius:10px; width:500px; max-width:90%; border:1px solid var(--border-color); max-height:80vh; overflow-y:auto;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h3 style="color:#fff; margin:0;">Manage Categories</h3>
                <button class="btn btn-outline-light btn-sm" id="btn-close-categories-modal"><i class="fa-solid fa-xmark"></i></button>
              </div>
              
              <div class="form-group" style="margin-bottom:25px; display:flex; gap:10px;">
                <input type="text" id="new-category-name" class="form-control" placeholder="New Category Name" style="flex:1;">
                <button class="btn btn-warning" id="btn-add-category">Add</button>
              </div>
              
              <div id="categories-list" style="display:flex; flex-direction:column; gap:10px;">
                <!-- Dynamically populated -->
              </div>
            </div>
          </div>
'''
html = html.replace('</div>\n        </div>\n\n      </div>\n    </div>', '</div>\n        </div>\n' + cat_modal + '\n      </div>\n    </div>')

# 3. Update Javascript to fetch categories and handle logic
js_logic = '''
    // --- Category Management ---
    let globalCategories = [];

    async function fetchCategories() {
      try {
        const res = await fetch(`${API_BASE}/api/categories`);
        const data = await res.json();
        if (data.success) {
          globalCategories = data.categories;
          renderCategoriesAdmin();
          updateCategoryDropdown(globalCategories);
          return globalCategories;
        }
      } catch(e) { console.error('Error fetching categories:', e); }
      return [];
    }

    function renderCategoriesAdmin() {
      // 1. Render in Manage Categories Modal
      const list = document.getElementById('categories-list');
      if (list) {
        if (globalCategories.length === 0) {
          list.innerHTML = '<div style="color:#aaa; text-align:center;">No categories found.</div>';
        } else {
          list.innerHTML = globalCategories.map(cat => `
            <div style="display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.05); padding:10px 15px; border-radius:6px;">
              <span style="color:#fff;">${cat.name}</span>
              <button onclick="deleteCategory(${cat.id})" class="btn btn-sm btn-danger" style="background:var(--danger); border:none; color:#fff; padding:4px 8px; border-radius:4px; cursor:pointer;"><i class="fa-solid fa-trash"></i></button>
            </div>
          `).join('');
        }
      }

      // 2. Render Filters in Gallery Tab
      const filterContainer = document.getElementById('admin-gallery-filters');
      if (filterContainer) {
        const allCats = ['All', ...globalCategories.map(c => c.name)];
        filterContainer.innerHTML = allCats.map(cat => 
          `<button class="btn btn-sm ${cat === 'All' ? 'btn-warning' : 'btn-outline-light'} admin-filter-btn" data-cat="${cat}" style="padding:6px 14px; border-radius:20px;">${cat}</button>`
        ).join('');

        document.querySelectorAll('.admin-filter-btn').forEach(btn => {
          btn.addEventListener('click', (e) => {
            document.querySelectorAll('.admin-filter-btn').forEach(b => {
              b.classList.remove('btn-warning');
              b.classList.add('btn-outline-light');
            });
            e.target.classList.remove('btn-outline-light');
            e.target.classList.add('btn-warning');
            filterAdminGallery(e.target.getAttribute('data-cat'));
          });
        });
      }
    }

    document.getElementById('btn-open-categories-modal')?.addEventListener('click', () => {
      document.getElementById('categories-modal').style.display = 'flex';
      fetchCategories();
    });

    document.getElementById('btn-close-categories-modal')?.addEventListener('click', () => {
      document.getElementById('categories-modal').style.display = 'none';
    });

    document.getElementById('btn-add-category')?.addEventListener('click', async () => {
      const name = document.getElementById('new-category-name').value.trim();
      if(!name) return;
      try {
        const res = await fetch(`${API_BASE}/api/admin/categories`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ name })
        });
        const data = await res.json();
        if(data.success) {
          document.getElementById('new-category-name').value = '';
          showToast('Category added!');
          fetchCategories();
        } else {
          showToast(data.error || 'Error adding category', 'danger');
        }
      } catch(e) { showToast('Error adding category', 'danger'); }
    });

    window.deleteCategory = async (id) => {
      if(!confirm("Delete this category? This will ALSO delete all images inside it!")) return;
      try {
        const res = await fetch(`${API_BASE}/api/admin/categories/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if(data.success) {
          showToast('Category deleted!');
          fetchCategories();
          fetchAdminGallery(); // refresh images since some might be deleted
        } else {
          showToast(data.error || 'Error deleting', 'danger');
        }
      } catch(e) { showToast('Error deleting', 'danger'); }
    };
'''

html = html.replace('// --- Gallery Management ---', js_logic + '\n    // --- Gallery Management ---')

# 4. Remove the old dynamic category extraction logic from fetchAdminGallery
old_logic = '''
          // Render categories
          const categories = ['All', ...new Set(adminAllImages.map(img => img.category || 'All').filter(c => c !== 'All'))];
          if (filterContainer) {
            filterContainer.innerHTML = categories.map(cat => 
              `<button class="btn btn-sm ${cat === 'All' ? 'btn-warning' : 'btn-outline-light'} admin-filter-btn" data-cat="${cat}" style="padding:6px 14px; border-radius:20px;">${cat}</button>`
            ).join('');

            document.querySelectorAll('.admin-filter-btn').forEach(btn => {
              btn.addEventListener('click', (e) => {
                document.querySelectorAll('.admin-filter-btn').forEach(b => {
                  b.classList.remove('btn-warning');
                  b.classList.add('btn-outline-light');
                });
                e.target.classList.remove('btn-outline-light');
                e.target.classList.add('btn-warning');
                filterAdminGallery(e.target.getAttribute('data-cat'));
              });
            });
          }
'''
html = html.replace(old_logic, '')

old_dropdown_update = '''
          // Update Category Dropdown options
          updateCategoryDropdown(categories.filter(c => c !== 'All'));
'''
html = html.replace(old_dropdown_update, '')

# 5. Fix updateCategoryDropdown
new_update_dropdown = '''
    function updateCategoryDropdown(cats) {
      const select = document.getElementById('modal-img-category-select');
      if (!select) return;
      const val = select.value;
      select.innerHTML = cats.map(c => `<option value="${c.name}" style="color:#000;">${c.name}</option>`).join('') + '<option value="_new_" style="color:#000;">+ Add New Category...</option>';
      
      let found = false;
      for(let i=0; i<select.options.length; i++) {
        if(select.options[i].value === val) { select.value = val; found = true; break; }
      }
      if (!found && cats.length > 0) select.value = cats[0].name;
    }
'''
html = re.sub(r'function updateCategoryDropdown\(cats\) \{.*?(?=    // Modal Logic)', new_update_dropdown, html, flags=re.DOTALL)

# 6. Change initial call
html = html.replace('fetchAdminGallery();', 'fetchCategories().then(() => fetchAdminGallery());')

# 7. Add category creation to Add Image if _new_ is selected
add_image_logic = '''
      let category = 'Campus';
      if (catSelect) {
        category = catSelect.value;
        if (category === '_new_' && catNew) {
          category = catNew.value.trim() || 'Campus';
          // Auto-create category in backend if it doesn't exist
          try {
            await fetch(`${API_BASE}/api/admin/categories`, {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({ name: category })
            });
            fetchCategories();
          } catch(e) {}
        }
      }
'''
html = re.sub(r'      let category = \'Campus\';\s+if \(catSelect\) \{\s+category = catSelect.value;\s+if \(category === \'_new_\' && catNew\) \{\s+category = catNew.value.trim\(\) \|\| \'Campus\';\s+\}\s+\}', add_image_logic, html)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated admin.html')
