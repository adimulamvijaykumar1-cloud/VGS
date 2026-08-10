with open('templates/admin.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add metric card
metric_insert = '''
        <div class="metric-card users">
          <div class="metric-info">
            <h3>Registered Users</h3>
            <div class="value" id="metric-users">0</div>
          </div>
          <div class="metric-icon" style="background-color: rgba(66, 133, 244, 0.1); color: #4285F4;"><i class="fa-brands fa-google"></i></div>
        </div>
'''
html = html.replace('</div>\n\n      <!-- Data Table Card -->', metric_insert + '      </div>\n\n      <!-- Data Table Card -->')

# 2. Add Users Table
table_insert = '''
      <!-- Users Table Card -->
      <div class="table-card" style="margin-top: 24px;">
        <div class="table-header-toolbar">
          <h2 class="table-title">Registered Users (Google Auth)</h2>
        </div>
        <div class="table-wrapper">
          <table id="users-table">
            <thead>
              <tr>
                <th>Profile</th>
                <th>Name</th>
                <th>Email</th>
                <th>Registration Date</th>
              </tr>
            </thead>
            <tbody id="users-table-body">
              <tr>
                <td colspan="4" class="no-data">
                  <i class="fa-solid fa-circle-notch fa-spin"></i> Loading users...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
'''
html = html.replace('</main>', table_insert + '\n    </main>')

# 3. Add JS fetching logic
js_insert = '''
    const usersTableBody = document.getElementById('users-table-body');
    const metricUsers = document.getElementById('metric-users');

    async function fetchUsers() {
      try {
        const response = await fetch(`${API_BASE}/api/admin/users`);
        if (response.status === 401) return;
        const data = await response.json();
        
        if (data.success) {
          metricUsers.textContent = data.users.length;
          
          if (data.users.length === 0) {
            usersTableBody.innerHTML = `<tr><td colspan="4" class="no-data"><i class="fa-solid fa-users"></i> No registered users yet.</td></tr>`;
            return;
          }
          
          usersTableBody.innerHTML = data.users.map(u => `
            <tr>
              <td><img src="${u.picture || 'https://via.placeholder.com/40'}" style="width:40px; height:40px; border-radius:50%; object-fit:cover;"></td>
              <td style="font-weight:600;">${u.name}</td>
              <td>${u.email}</td>
              <td>${formatDate(u.created_at)}</td>
            </tr>
          `).join('');
        }
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    }
'''
html = html.replace('async function fetchEnquiries() {', js_insert + '\n    async function fetchEnquiries() {')

# 4. Call fetchUsers in showDashboard
html = html.replace('fetchEnquiries();', 'fetchEnquiries();\n      fetchUsers();')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated admin.html successfully.')
