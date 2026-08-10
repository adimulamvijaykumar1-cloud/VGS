import re

# ----------------- PATCH COURSES.HTML -----------------
with open('courses.html', 'r', encoding='utf-8') as f:
    html = f.read()

courses_html_container = """
<div id="dynamic-courses-full">
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
      const container = document.getElementById('dynamic-courses-full');
      
      let coursesHtml = '';
      data.courses.forEach((c, index) => {
        // Alternate background and layout
        const isEven = index % 2 !== 0; // 0-indexed, so 1,3,5 are 'even' visual blocks
        const bgClass = isEven ? 'bg-cream' : '';
        const order1 = isEven ? 'style="order:2;"' : '';
        const order2 = isEven ? 'style="order:1;"' : '';
        const gradStyle = isEven ? 'style="background:linear-gradient(155deg, var(--gold-deep), var(--gold-light));"' : '';
        const iconColor = isEven ? 'style="color:rgba(11,31,77,0.55);"' : '';
        
        let titleSplit = c.title.split(' ');
        let mainTitle = c.title;
        let empTitle = '';
        if (titleSplit.length > 1) {
            empTitle = titleSplit.pop();
            mainTitle = titleSplit.join(' ');
        }
        
        const bulletsList = c.bullets.split(',').map(b => `<li><i class="fa-solid fa-check"></i> ${b.trim()}</li>`).join('');

        coursesHtml += `
        <section class="section-pad ${bgClass}" id="course-${c.id}">
          <div class="container">
            <div class="about-split">
              <div class="reveal" ${order2}>
                <span class="eyebrow">Program 0${index + 1}</span>
                <h2 class="section-title">${mainTitle} <em>${empTitle}</em></h2>
                <p class="section-sub" style="margin-bottom:24px;">${c.subtitle} - ${c.description}</p>
                <ul class="course-list" style="max-width:420px;">
                  ${bulletsList}
                </ul>
                <a href="contact.html" class="btn btn-navy" style="margin-top:14px;">Enroll in This Program</a>
              </div>
              <div class="about-visual reveal" ${order1}>
                <div class="about-frame" ${gradStyle}><i class="${c.icon}" ${iconColor}></i></div>
                <div class="about-badge-float">
                  <span class="n">${c.badge_num}</span>
                  <span class="l">${c.badge_text.replace(' ', '<br>')}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
        `;
      });
      container.innerHTML = coursesHtml;
    } else if (data.success) {
      document.getElementById('dynamic-courses-full').innerHTML = '<p style="text-align:center; padding:50px;">No courses available at the moment.</p>';
    }
  } catch(e) {
    console.error('Failed to load courses', e);
  }
});
</script>
"""

html = re.sub(r'<!-- IIT FOUNDATION -->.*?(?=<!-- BATCH TIMINGS REPEAT -->)', courses_html_container + '\n\n', html, flags=re.DOTALL)

with open('courses.html', 'w', encoding='utf-8') as f:
    f.write(html)


# ----------------- PATCH INDEX.HTML -----------------
with open('index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

index_js = """
    <div class="grid grid-3" id="dynamic-courses-grid">
      <div style="grid-column: 1 / -1; text-align:center; padding: 50px;">
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
          const container = document.getElementById('dynamic-courses-grid');
          let coursesHtml = '';
          data.courses.forEach((c, index) => {
            const delay = index > 0 ? `reveal-delay-${index}` : '';
            const bulletsList = c.bullets.split(',').slice(0, 4).map(b => `<li><i class="fa-solid fa-check"></i> ${b.trim()}</li>`).join('');
            coursesHtml += `
              <div class="course-card reveal ${delay}">
                <div class="cc-head">
                  <span class="cc-num">Program 0${index + 1}</span>
                  <div class="cc-icon"><i class="${c.icon}"></i></div>
                  <h3>${c.title}</h3>
                </div>
                <div class="cc-body">
                  <p class="desc">${c.subtitle}</p>
                  <ul class="course-list">
                    ${bulletsList}
                  </ul>
                  <a href="courses.html#course-${c.id}" class="btn btn-navy btn-block">Learn More</a>
                </div>
              </div>
            `;
          });
          container.innerHTML = coursesHtml;
        }
      } catch(e) {
        console.error('Failed to load courses', e);
      }
    });
    </script>
"""

index_html = re.sub(r'<div class="grid grid-3">.*?</div>\s*</div>\s*</section>', index_js + '\n  </div>\n</section>', index_html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

print("Patched frontend courses successfully.")
