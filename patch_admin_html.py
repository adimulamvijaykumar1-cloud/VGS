import re

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

sidebar_css = """
  .dashboard-container {
    display: flex;
    height: 100vh;
    background-color: var(--navy-deep);
  }

  .sidebar {
    width: 260px;
    background-color: var(--navy-mid);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    height: 100%;
    flex-shrink: 0;
  }

  .sidebar-header {
    padding: 24px;
    border-bottom: 1px solid var(--border-color);
  }

  .sidebar-nav {
    padding: 20px 0;
    flex: 1;
    overflow-y: auto;
  }

  .nav-item {
    padding: 12px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text-muted);
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    cursor: pointer;
  }

  .nav-item:hover {
    color: #fff;
    background-color: rgba(255,255,255,0.05);
  }

  .nav-item.active {
    color: var(--gold);
    background-color: rgba(212, 175, 55, 0.1);
    border-right: 3px solid var(--gold);
  }

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .top-header {
    height: 70px;
    padding: 0 30px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: var(--navy-deep);
  }

  .content-area {
    flex: 1;
    padding: 30px;
    overflow-y: auto;
  }

  .tab-pane {
    display: none;
  }
  .tab-pane.active {
    display: block;
  }
"""

admin_html = re.sub(r'\.dashboard-container.*?\}', sidebar_css.strip(), admin_html, flags=re.DOTALL)

dashboard_html = """
  <!-- ===================== DASHBOARD VIEW ===================== -->
  <div class="dashboard-container" id="dashboard-view">
    
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <a href="index.html" class="dash-brand" style="text-decoration:none;">
          <div class="dash-brand-logo">V</div>
          <div class="dash-brand-text">
            <h1>VGS Academy</h1>
            <span>ADMIN CMS</span>
          </div>
        </a>
      </div>
      <div class="sidebar-nav">
        <div class="nav-item active" data-target="tab-dashboard"><i class="fa-solid fa-chart-pie"></i> Dashboard</div>
        <div class="nav-item" data-target="tab-settings"><i class="fa-solid fa-gear"></i> Site Settings</div>
        <div class="nav-item" data-target="tab-courses"><i class="fa-solid fa-book-open"></i> Courses</div>
        <div class="nav-item" data-target="tab-gallery"><i class="fa-solid fa-images"></i> Gallery</div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="top-header">
        <h2 id="page-title">Dashboard Overview</h2>
        <div class="user-menu">
          <div class="user-info">Logged in as <strong>Admin</strong></div>
          <button class="btn btn-outline btn-sm" id="logout-btn"><i class="fa-solid fa-arrow-right-from-bracket"></i> Logout</button>
        </div>
      </div>

      <div class="content-area">
        
        <!-- DASHBOARD TAB -->
        <div id="tab-dashboard" class="tab-pane active">
          <div class="metrics-grid">
            <div class="metric-card total">
              <div class="metric-info">
                <h3>Total Enquiries</h3>
                <div class="value" id="metric-total">0</div>
              </div>
              <div class="metric-icon"><i class="fa-solid fa-inbox"></i></div>
            </div>
            <div class="metric-card pending">
              <div class="metric-info">
                <h3>Pending Follow-up</h3>
                <div class="value" id="metric-pending">0</div>
              </div>
              <div class="metric-icon"><i class="fa-solid fa-clock-rotate-left"></i></div>
            </div>
            <div class="metric-card contacted">
              <div class="metric-info">
                <h3>Contacted</h3>
                <div class="value" id="metric-contacted">0</div>
              </div>
              <div class="metric-icon"><i class="fa-solid fa-user-check"></i></div>
            </div>
            <div class="metric-card users">
              <div class="metric-info">
                <h3>Registered Users</h3>
                <div class="value" id="metric-users">0</div>
              </div>
              <div class="metric-icon" style="background-color: rgba(66, 133, 244, 0.1); color: #4285F4;"><i class="fa-brands fa-google"></i></div>
            </div>
          </div>

          <!-- Enquiries Table -->
          <div class="table-card" style="margin-bottom: 24px;">
            <div class="table-header-toolbar">
              <h2 class="table-title">Student Enquiries</h2>
              <div class="toolbar-filters">
                <select class="filter-select" id="filter-class">
                  <option value="all">All Classes</option>
                  <option value="Class 6">Class 6</option>
                  <option value="Class 7">Class 7</option>
                  <option value="Class 8">Class 8</option>
                  <option value="Class 9">Class 9</option>
                  <option value="Class 10">Class 10</option>
                  <option value="Sainik School Aspirant">Sainik School</option>
                  <option value="Olympiad Aspirant">Olympiad</option>
                </select>
                <select class="filter-select" id="filter-status">
                  <option value="all">All Statuses</option>
                  <option value="pending">Pending</option>
                  <option value="contacted">Contacted</option>
                  <option value="archived">Archived</option>
                </select>
                <button class="btn btn-outline btn-sm" id="refresh-btn"><i class="fa-solid fa-arrows-rotate"></i> Refresh</button>
              </div>
            </div>
            <div class="table-wrapper">
              <table id="enquiries-table">
                <thead>
                  <tr>
                    <th>Student Details</th>
                    <th>Class</th>
                    <th>Enquiry Message</th>
                    <th>Status</th>
                    <th>Date Received</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody id="table-body">
                  <tr><td colspan="6" class="no-data"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Users Table Card -->
          <div class="table-card">
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
                  <tr><td colspan="4" class="no-data"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading users...</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- SETTINGS TAB -->
        <div id="tab-settings" class="tab-pane">
          <div class="table-card" style="padding: 30px;">
            <h2 style="margin-bottom: 20px;">Global Site Settings</h2>
            <form id="settings-form">
              <div class="form-group">
                <label>Phone Number</label>
                <input type="text" class="form-control" id="setting-phone" required>
              </div>
              <div class="form-group">
                <label>Instagram URL</label>
                <input type="text" class="form-control" id="setting-instagram" required>
              </div>
              <div class="form-group">
                <label>Physical Location (Address)</label>
                <input type="text" class="form-control" id="setting-location" required>
              </div>
              <div class="form-group">
                <label>Navbar Icon URL (SVG or Image URL)</label>
                <input type="text" class="form-control" id="setting-navicon" required>
              </div>
              <button type="submit" class="btn btn-gold">Save Settings</button>
            </form>
          </div>
        </div>

        <!-- COURSES TAB -->
        <div id="tab-courses" class="tab-pane">
          <div class="table-card" style="padding: 30px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
              <h2>Manage Courses</h2>
              <button class="btn btn-gold btn-sm" id="btn-add-course"><i class="fa-solid fa-plus"></i> Add Course</button>
            </div>
            <div id="courses-list" style="display: flex; flex-direction: column; gap: 15px;">
              <!-- Dynamically populated -->
            </div>
          </div>
        </div>

        <!-- GALLERY TAB -->
        <div id="tab-gallery" class="tab-pane">
          <div class="table-card" style="padding: 30px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 20px;">
              <h2>Manage Gallery</h2>
              <button class="btn btn-gold btn-sm" id="btn-add-gallery"><i class="fa-solid fa-plus"></i> Add Image URL</button>
            </div>
            <div id="gallery-list" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
              <!-- Dynamically populated -->
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
"""

admin_html = re.sub(r'<!-- ===================== DASHBOARD VIEW ===================== -->.*<!-- Toast Message -->', dashboard_html.strip() + '\n\n  <!-- Toast Message -->', admin_html, flags=re.DOTALL)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin_html)

print('Updated admin.html HTML structure.')
