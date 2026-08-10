import re

with open('courses.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace all hardcoded sections with a single container and JS
container_html = """
<div id="dynamic-courses-container">
  <div style="text-align:center; padding: 50px;">
    <i class="fa-solid fa-circle-notch fa-spin" style="font-size:2rem; color:var(--gold);"></i>
    <p style="margin-top:20px;">Loading courses...</p>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async function() {
  try {
    const res = await fetch('/api/courses');
    const data = await res.json();
    if (data.success && data.courses.length > 0) {
      const container = document.getElementById('dynamic-courses-container');
      
      let coursesHtml = '';
      data.courses.forEach((c, index) => {
        // Alternate background and layout
        const isEven = index % 2 !== 0; // 0-indexed, so 1,3,5 are 'even' visual blocks
        const bgClass = isEven ? 'bg-cream' : '';
        const order1 = isEven ? 'style="order:2;"' : '';
        const order2 = isEven ? 'style="order:1;"' : '';
        const gradStyle = isEven ? 'style="background:linear-gradient(155deg, var(--gold-deep), var(--gold-light));"' : '';
        const iconColor = isEven ? 'style="color:rgba(11,31,77,0.55);"' : '';
        
        const bulletsList = c.bullets.split(',').map(b => `<li><i class="fa-solid fa-check"></i> ${b.trim()}</li>`).join('');

        coursesHtml += `
        <section class="section-pad ${bgClass}" id="course-${c.id}">
          <div class="container">
            <div class="about-split">
              <div class="reveal" ${order2}>
                <span class="eyebrow">Program 0${index + 1}</span>
                <h2 class="section-title">${c.title} <em>${c.subtitle}</em></h2>
                <p class="section-sub" style="margin-bottom:24px;">${c.description}</p>
                <ul class="course-list" style="max-width:420px;">
                  ${bulletsList}
                </ul>
                <a href="contact.html" class="btn btn-navy" style="margin-top:14px;">Enroll in This Program</a>
              </div>
              <div class="about-visual reveal" ${order1}>
                <div class="about-frame" ${gradStyle}><i class="${c.icon}" ${iconColor}></i></div>
                <div class="about-badge-float">
                  <span class="n">${c.badge_num}</span>
                  <span class="l">${c.badge_text}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
        `;
      });
      container.innerHTML = coursesHtml;
    } else if (data.success) {
      document.getElementById('dynamic-courses-container').innerHTML = '<p style="text-align:center; padding:50px;">No courses available at the moment.</p>';
    }
  } catch(e) {
    console.error('Failed to load courses', e);
  }
});
</script>
"""

# Replace from <!-- IIT FOUNDATION --> to <!-- CTA SECTION -->
html = re.sub(r'<!-- IIT FOUNDATION -->.*?<!-- CTA SECTION -->', container_html + '\n\n<!-- CTA SECTION -->', html, flags=re.DOTALL)

with open('courses.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated courses.html for dynamic rendering.')
