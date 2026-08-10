import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update the Add Course Modal HTML
old_modal = """
          <!-- Add Course Modal -->
          <div id="add-course-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; justify-content:center; align-items:center;">
            <div style="background:var(--navy-light); padding:30px; border-radius:10px; width:500px; max-width:90%; border:1px solid var(--border-color); max-height:85vh; overflow-y:auto;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h3 style="color:#fff; margin:0;">Add New Course</h3>
                <button class="btn btn-outline-light btn-sm" id="btn-close-course-modal"><i class="fa-solid fa-xmark"></i></button>
              </div>
              
              <div style="display:flex; flex-direction:column; gap:15px; margin-bottom:25px;">
                <input type="text" id="course-title" placeholder="Course Title (e.g. IIT Foundation)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                <input type="text" id="course-subtitle" placeholder="Subtitle (e.g. For classes 6th to 10th)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                <textarea id="course-desc" placeholder="Description..." rows="3" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%; resize:vertical;"></textarea>
                <input type="text" id="course-icon" placeholder="FontAwesome Icon (e.g. fa-solid fa-book)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                <input type="text" id="course-bullets" placeholder="Bullets (comma separated)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                
                <div style="display:flex; gap:10px;">
                  <input type="text" id="course-badge-num" placeholder="Badge Num (e.g. 6-10)" style="flex:1; padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff;">
                  <input type="text" id="course-badge-text" placeholder="Badge Text (e.g. Grade Levels)" style="flex:1; padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff;">
                </div>
              </div>
              
              <div style="display:flex; justify-content:flex-end; gap:10px;">
                <button class="btn btn-outline-light" id="btn-cancel-course-modal">Cancel</button>
                <button class="btn btn-gold" id="btn-submit-course-modal">Save Course</button>
              </div>
            </div>
          </div>
"""

new_modal = """
          <!-- Add/Edit Course Modal -->
          <div id="add-course-modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:9999; justify-content:center; align-items:center;">
            <div style="background:var(--navy-light); padding:30px; border-radius:10px; width:500px; max-width:90%; border:1px solid var(--border-color); max-height:85vh; overflow-y:auto;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h3 id="course-modal-title" style="color:#fff; margin:0;">Add New Course</h3>
                <button class="btn btn-outline-light btn-sm" id="btn-close-course-modal"><i class="fa-solid fa-xmark"></i></button>
              </div>
              
              <div style="display:flex; flex-direction:column; gap:15px; margin-bottom:25px;">
                <input type="hidden" id="course-id" value="">
                <input type="text" id="course-title" placeholder="Course Title (e.g. IIT Foundation)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                <input type="text" id="course-subtitle" placeholder="Subtitle (e.g. For classes 6th to 10th)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                <textarea id="course-desc" placeholder="Description..." rows="3" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%; resize:vertical;"></textarea>
                <input type="text" id="course-icon" placeholder="FontAwesome Icon (e.g. fa-solid fa-book)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                <input type="text" id="course-image" placeholder="Background Image URL (Optional)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                <input type="text" id="course-bullets" placeholder="Bullets (comma separated)" style="padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff; width:100%;">
                
                <div style="display:flex; gap:10px;">
                  <input type="text" id="course-badge-num" placeholder="Badge Num (e.g. 6-10)" style="flex:1; padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff;">
                  <input type="text" id="course-badge-text" placeholder="Badge Text (e.g. Grade Levels)" style="flex:1; padding:12px 15px; border-radius:8px; border:1px solid var(--border-color); background:rgba(255,255,255,0.05); color:#fff;">
                </div>
              </div>
              
              <div style="display:flex; justify-content:flex-end; gap:10px;">
                <button class="btn btn-outline-light" id="btn-cancel-course-modal">Cancel</button>
                <button class="btn btn-gold" id="btn-submit-course-modal">Save Course</button>
              </div>
            </div>
          </div>
"""
html = html.replace(old_modal.strip(), new_modal.strip())

# 2. Update Javascript
old_js = """
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

    document.getElementById('btn-add-course').addEventListener('click', () => {
      document.getElementById('add-course-modal').style.display = 'flex';
    });

    document.getElementById('btn-close-course-modal').addEventListener('click', () => {
      document.getElementById('add-course-modal').style.display = 'none';
    });
    
    document.getElementById('btn-cancel-course-modal').addEventListener('click', () => {
      document.getElementById('add-course-modal').style.display = 'none';
    });

    document.getElementById('btn-submit-course-modal').addEventListener('click', async () => {
      const title = document.getElementById('course-title').value.trim();
      const subtitle = document.getElementById('course-subtitle').value.trim();
      const description = document.getElementById('course-desc').value.trim();
      const icon = document.getElementById('course-icon').value.trim() || "fa-solid fa-book";
      const bullets = document.getElementById('course-bullets').value.trim();
      const badge_num = document.getElementById('course-badge-num').value.trim();
      const badge_text = document.getElementById('course-badge-text').value.trim();

      if (!title) return;

      try {
        const res = await fetch(`${API_BASE}/api/admin/courses`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ title, subtitle, description, icon, bullets, badge_num, badge_text })
        });
        const data = await res.json();
        if (data.success) {
          showToast('Course added!');
          document.getElementById('add-course-modal').style.display = 'none';
          
          // Clear inputs
          document.getElementById('course-title').value = '';
          document.getElementById('course-subtitle').value = '';
          document.getElementById('course-desc').value = '';
          document.getElementById('course-icon').value = '';
          document.getElementById('course-bullets').value = '';
          document.getElementById('course-badge-num').value = '';
          document.getElementById('course-badge-text').value = '';
          
          fetchAdminCourses();
        } else {
          showToast(data.error || 'Error adding course', 'danger');
        }
      } catch(e) { showToast('Error adding course', 'danger'); }
    });
"""

new_js = """
    // --- Courses Management ---
    let allCourses = [];
    async function fetchAdminCourses() {
      try {
        const res = await fetch(`${API_BASE}/api/courses`);
        const data = await res.json();
        const list = document.getElementById('courses-list');
        if (data.success) {
          allCourses = data.courses;
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
              <div style="display:flex; gap:10px;">
                <button class="btn btn-outline-light btn-sm" onclick="editCourse(${c.id})"><i class="fa-solid fa-pencil"></i> Edit</button>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteCourse(${c.id})"><i class="fa-solid fa-trash"></i> Delete</button>
              </div>
            </div>
          `).join('');
        }
      } catch(e) { console.error(e); }
    }
    
    window.editCourse = (id) => {
      const course = allCourses.find(c => c.id === id);
      if(!course) return;
      document.getElementById('course-modal-title').innerText = 'Edit Course';
      document.getElementById('course-id').value = course.id;
      document.getElementById('course-title').value = course.title || '';
      document.getElementById('course-subtitle').value = course.subtitle || '';
      document.getElementById('course-desc').value = course.description || '';
      document.getElementById('course-icon').value = course.icon || '';
      document.getElementById('course-image').value = course.image_url || '';
      document.getElementById('course-bullets').value = course.bullets || '';
      document.getElementById('course-badge-num').value = course.badge_num || '';
      document.getElementById('course-badge-text').value = course.badge_text || '';
      document.getElementById('add-course-modal').style.display = 'flex';
    };

    document.getElementById('btn-add-course').addEventListener('click', () => {
      document.getElementById('course-modal-title').innerText = 'Add New Course';
      document.getElementById('course-id').value = '';
      document.getElementById('course-title').value = '';
      document.getElementById('course-subtitle').value = '';
      document.getElementById('course-desc').value = '';
      document.getElementById('course-icon').value = '';
      document.getElementById('course-image').value = '';
      document.getElementById('course-bullets').value = '';
      document.getElementById('course-badge-num').value = '';
      document.getElementById('course-badge-text').value = '';
      document.getElementById('add-course-modal').style.display = 'flex';
    });

    document.getElementById('btn-close-course-modal').addEventListener('click', () => {
      document.getElementById('add-course-modal').style.display = 'none';
    });
    
    document.getElementById('btn-cancel-course-modal').addEventListener('click', () => {
      document.getElementById('add-course-modal').style.display = 'none';
    });

    document.getElementById('btn-submit-course-modal').addEventListener('click', async () => {
      const id = document.getElementById('course-id').value;
      const title = document.getElementById('course-title').value.trim();
      const subtitle = document.getElementById('course-subtitle').value.trim();
      const description = document.getElementById('course-desc').value.trim();
      const icon = document.getElementById('course-icon').value.trim() || "fa-solid fa-book";
      const image_url = document.getElementById('course-image').value.trim();
      const bullets = document.getElementById('course-bullets').value.trim();
      const badge_num = document.getElementById('course-badge-num').value.trim();
      const badge_text = document.getElementById('course-badge-text').value.trim();

      if (!title) return;

      try {
        const endpoint = id ? `${API_BASE}/api/admin/courses/${id}` : `${API_BASE}/api/admin/courses`;
        const method = id ? 'PUT' : 'POST';
        const res = await fetch(endpoint, {
          method: method,
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ title, subtitle, description, icon, image_url, bullets, badge_num, badge_text })
        });
        const data = await res.json();
        if (data.success) {
          showToast(id ? 'Course updated!' : 'Course added!');
          document.getElementById('add-course-modal').style.display = 'none';
          fetchAdminCourses();
        } else {
          showToast(data.error || 'Error saving course', 'danger');
        }
      } catch(e) { showToast('Error saving course', 'danger'); }
    });
"""

html = html.replace(old_js.strip(), new_js.strip())

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated admin.html successfully.")
