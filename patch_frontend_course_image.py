import re

with open('courses.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_js = """
        let badgeTextHtml = '';
        if (c.badge_text) {
          badgeTextHtml = c.badge_text.replace(' ', '<br>');
        }

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
                  <span class="l">${badgeTextHtml}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
        `;
"""

new_js = """
        let badgeTextHtml = '';
        if (c.badge_text) {
          badgeTextHtml = c.badge_text.replace(' ', '<br>');
        }
        
        let visualContent = `<i class="${c.icon}" ${iconColor}></i>`;
        let visualStyle = gradStyle;
        if (c.image_url) {
            visualContent = `<img src="${c.image_url}" alt="${mainTitle}" style="width:100%; height:100%; object-fit:cover; position:absolute; top:0; left:0; z-index:1;">`;
            // Remove icon color style and let the image be the main visual
            visualStyle = 'style="position:relative; background: var(--navy-dark);"';
        }

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
                <div class="about-frame" ${visualStyle}>${visualContent}</div>
                <div class="about-badge-float" style="z-index:2;">
                  <span class="n">${c.badge_num}</span>
                  <span class="l">${badgeTextHtml}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
        `;
"""

html = html.replace(old_js.strip(), new_js.strip())

with open('courses.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated courses.html")


with open('index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

old_index_js = """
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
"""

new_index_js = """
            let iconOrImage = `<div class="cc-icon"><i class="${c.icon}"></i></div>`;
            if (c.image_url) {
                iconOrImage = `<div style="width:100%; height:180px; margin-bottom:15px; border-radius:12px; overflow:hidden;"><img src="${c.image_url}" alt="${c.title}" style="width:100%; height:100%; object-fit:cover;"></div>`;
            }
            coursesHtml += `
              <div class="course-card reveal ${delay}" style="display:flex; flex-direction:column; justify-content:space-between;">
                <div class="cc-head" style="margin-bottom:0;">
                  <span class="cc-num">Program 0${index + 1}</span>
                  ${iconOrImage}
                  <h3 style="margin-top: ${c.image_url ? '15px' : '20px'};">${c.title}</h3>
                </div>
                <div class="cc-body">
                  <p class="desc">${c.subtitle}</p>
                  <ul class="course-list">
                    ${bulletsList}
                  </ul>
                  <a href="courses.html#course-${c.id}" class="btn btn-navy btn-block" style="margin-top:15px;">Learn More</a>
                </div>
              </div>
            `;
"""

index_html = index_html.replace(old_index_js.strip(), new_index_js.strip())

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)
print("Updated index.html")
