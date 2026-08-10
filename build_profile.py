with open('about.html', 'r', encoding='utf-8') as f:
    html = f.read()

header, rest = html.split('</header>', 1)
nav, rest = rest.split('<section class="page-hero">', 1)
_, footer = rest.split('<footer class="footer">', 1)

new_content = """
<section class="page-hero">
  <div class="container">
    <div class="breadcrumb"><a href="index.html">Home</a> / Profile</div>
    <h1>My Profile</h1>
    <p>Manage your account and view your enrolled courses.</p>
  </div>
</section>

<section class="section-pad">
  <div class="container">
    <div class="row g-5">
      <!-- Profile Card -->
      <div class="col-lg-4">
        <div class="card" style="border: none; border-radius: 16px; box-shadow: var(--shadow-sm); padding: 30px; text-align: center;">
          <div id="profile-picture-container" style="width: 120px; height: 120px; margin: 0 auto 20px; border-radius: 50%; overflow: hidden; background: #eee;">
            <!-- Fetched from Google -->
          </div>
          <h3 id="profile-name-display" style="color: var(--navy); margin-bottom: 5px;">Loading...</h3>
          <p id="profile-email-display" style="color: #666; margin-bottom: 25px;">Loading...</p>
          <button id="profile-page-logout" class="btn btn-outline-danger w-100"><i class="fa-solid fa-right-from-bracket"></i> Logout</button>
        </div>
      </div>
      
      <!-- Profile Content -->
      <div class="col-lg-8">
        <div class="card" style="border: none; border-radius: 16px; box-shadow: var(--shadow-sm); padding: 30px;">
          <h4 style="color: var(--navy); margin-bottom: 20px; border-bottom: 2px solid var(--gold-light); padding-bottom: 10px; display: inline-block;">My Courses</h4>
          
          <div class="alert alert-info" style="background: rgba(11, 31, 77, 0.05); border: none; color: var(--navy); border-radius: 12px; display: flex; gap: 15px; align-items: flex-start; padding: 20px;">
            <i class="fa-solid fa-circle-info" style="font-size: 1.5rem; color: var(--gold);"></i>
            <div>
              <strong style="display: block; margin-bottom: 5px; font-size: 1.1rem;">You are not enrolled in any courses yet.</strong>
              <p style="margin: 0; opacity: 0.8;">Explore our premium coaching programs and start your journey towards a bright future.</p>
            </div>
          </div>
          
          <div style="margin-top: 20px;">
            <a href="courses.html" class="btn btn-gold"><i class="fa-solid fa-graduation-cap" style="margin-right: 5px;"></i>Browse Courses</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', async function() {
  try {
    const res = await fetch('/api/auth/session');
    const data = await res.json();
    
    if (data.authenticated && data.user) {
      document.getElementById('profile-name-display').textContent = data.user.name;
      document.getElementById('profile-email-display').textContent = data.user.email;
      
      const picUrl = data.user.picture || 'https://via.placeholder.com/150';
      document.getElementById('profile-picture-container').innerHTML = `<img src="${picUrl}" style="width:100%; height:100%; object-fit:cover;" alt="Profile Picture">`;
      
      document.title = `${data.user.name.split(' ')[0]}'s Profile | VGS Academy`;
    } else {
      window.location.href = 'index.html';
    }
  } catch (e) {
    console.error('Session check failed', e);
  }
  
  document.getElementById('profile-page-logout')?.addEventListener('click', async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = 'index.html';
  });
});
</script>
"""

with open('profile.html', 'w', encoding='utf-8') as f:
    f.write(header + '</header>' + nav + new_content + '<footer class="footer">' + footer)
