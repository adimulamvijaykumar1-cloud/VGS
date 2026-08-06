/* ==========================================================================
   VGS ACADEMY — Site Script
   ========================================================================== */
document.addEventListener('DOMContentLoaded', function () {

  /* ---------- Sticky Navbar ---------- */
  const navbar = document.querySelector('.navbar');
  const toggleScrollState = () => {
    if (!navbar) return;
    if (window.scrollY > 40) navbar.classList.add('is-scrolled');
    else navbar.classList.remove('is-scrolled');
  };
  toggleScrollState();
  window.addEventListener('scroll', toggleScrollState, { passive: true });

  /* ---------- Mobile Menu ---------- */
  const navToggle = document.querySelector('.nav-toggle');
  const mobileMenu = document.querySelector('.mobile-menu');
  const mobileClose = document.querySelector('.mobile-close');
  if (navToggle && mobileMenu) {
    navToggle.addEventListener('click', () => mobileMenu.classList.add('open'));
  }
  if (mobileClose && mobileMenu) {
    mobileClose.addEventListener('click', () => mobileMenu.classList.remove('open'));
  }
  document.querySelectorAll('.mobile-menu a').forEach(a => {
    a.addEventListener('click', () => mobileMenu && mobileMenu.classList.remove('open'));
  });

  /* ---------- Scroll Reveal (IntersectionObserver) ---------- */
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && revealEls.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(el => io.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add('in'));
  }

  /* ---------- Animated Counters ---------- */
  const counters = document.querySelectorAll('[data-count]');
  const animateCounter = (el) => {
    const target = parseFloat(el.getAttribute('data-count'));
    const suffix = el.getAttribute('data-suffix') || '';
    const duration = 1600;
    const start = performance.now();
    const isInt = Number.isInteger(target);
    const step = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = target * eased;
      el.textContent = (isInt ? Math.floor(value) : value.toFixed(1)) + suffix;
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target + suffix;
    };
    requestAnimationFrame(step);
  };
  if ('IntersectionObserver' in window && counters.length) {
    const cio = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          cio.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });
    counters.forEach(el => cio.observe(el));
  }

  /* ---------- FAQ Accordion ---------- */
  document.querySelectorAll('.faq-item').forEach(item => {
    const q = item.querySelector('.faq-q');
    q && q.addEventListener('click', () => {
      const wasOpen = item.classList.contains('open');
      item.parentElement.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });

  /* ---------- Gallery Lightbox ---------- */
  const lightbox = document.querySelector('.lightbox');
  const lightboxBox = document.querySelector('.lightbox-box');
  document.querySelectorAll('.g-item').forEach(item => {
    item.addEventListener('click', () => {
      if (!lightbox || !lightboxBox) return;
      const label = item.getAttribute('data-label') || '';
      const imageSrc = item.getAttribute('data-image') || '';
      const icon = item.getAttribute('data-icon') || 'fa-image';
      const tone = item.querySelector('.g-bg')?.className.match(/tone-\d/)?.[0] || 'tone-1';
      
      lightboxBox.className = 'lightbox-box ' + tone;
      
      if (imageSrc) {
        lightboxBox.innerHTML = `
          <img src="${imageSrc}" alt="${label}" style="max-width:100%; max-height:72vh; object-fit:contain; border-radius:var(--radius-sm); box-shadow:var(--shadow-lg);">
          <div style="font-family:var(--ff-display); font-size:1.3rem; margin-top:16px; color:#fff;">${label}</div>
        `;
      } else {
        lightboxBox.innerHTML = `
          <i class="fa-solid ${icon}"></i>
          <div style="font-family:var(--ff-display); font-size:1.3rem; margin-top:16px;">${label}</div>
        `;
      }
      
      lightbox.classList.add('open');
    });
  });
  document.querySelector('.lightbox-close')?.addEventListener('click', () => lightbox.classList.remove('open'));
  lightbox?.addEventListener('click', (e) => { if (e.target === lightbox) lightbox.classList.remove('open'); });

  /* ---------- Contact Form ---------- */
  const contactForm = document.querySelector('.vgs-contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      
      const submitBtn = contactForm.querySelector('button[type="submit"]');
      const successBox = document.querySelector('.form-success');
      
      // Remove any existing error boxes
      const oldErrorBox = contactForm.querySelector('.form-error');
      if (oldErrorBox) oldErrorBox.remove();
      
      // Get form inputs
      const nameInput = document.getElementById('name');
      const phoneInput = document.getElementById('phone');
      const classInput = document.getElementById('class');
      const messageInput = document.getElementById('message');
      
      const formData = {
        name: nameInput ? nameInput.value : '',
        phone: phoneInput ? phoneInput.value : '',
        class: classInput ? classInput.value : '',
        message: messageInput ? messageInput.value : ''
      };
      
      // Set loading state on button
      const originalBtnText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = 'Sending Enquiry... <i class="fa-solid fa-spinner fa-spin"></i>';
      if (successBox) successBox.classList.remove('show');
      
      // Detect if accessed via file protocol (direct browser double-click)
      // and use the localhost API server, otherwise use relative path.
      const API_URL = (window.location.protocol === 'file:') 
        ? 'http://localhost:5000/api/enquiry' 
        : '/api/enquiry';
      
      try {
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
          if (successBox) {
            successBox.classList.add('show');
            successBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }

          // Formulate WhatsApp message text
          const messageText = `Hello VGS Academy, I would like to enquire about admission.\n\n*Details:*\n- *Name:* ${formData.name}\n- *Phone:* ${formData.phone}\n- *Class:* ${formData.class}\n- *Message:* ${formData.message || 'None'}`;
          const waUrl = `https://wa.me/919963736363?text=${encodeURIComponent(messageText)}`;
          
          // Try to open WhatsApp in a new tab
          const newWindow = window.open(waUrl, '_blank');
          
          // Fallback to direct redirect if popup blocker prevented the new tab
          if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
            window.location.href = waUrl;
          }

          contactForm.reset();
        } else {
          showFormError(data.error || 'Failed to submit enquiry. Please try again.');
        }
      } catch (err) {
        showFormError('Connection failed. Please verify that the backend server is running.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });

    function showFormError(message) {
      const errorBox = document.createElement('div');
      errorBox.className = 'form-error';
      errorBox.style.cssText = `
        display: flex;
        align-items: center;
        gap: 12px;
        background: #fdf2f2;
        border: 1px solid #f8d7da;
        color: #b02a37;
        padding: 16px 18px;
        border-radius: 12px;
        font-size: .9rem;
        margin-bottom: 22px;
      `;
      errorBox.innerHTML = `<i class="fa-solid fa-circle-exclamation" style="font-size: 1.1rem;"></i> <span>${message}</span>`;
      
      contactForm.insertBefore(errorBox, contactForm.firstChild);
      errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  /* ---------- Back to top / floating "top" button ---------- */
  const topBtn = document.querySelector('.float-btn.top');
  window.addEventListener('scroll', () => {
    if (!topBtn) return;
    if (window.scrollY > 500) topBtn.classList.add('show');
    else topBtn.classList.remove('show');
  }, { passive: true });
  topBtn && topBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

  /* ---------- Set active nav link based on current page ---------- */
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (path === '' && href === 'index.html')) {
      a.classList.add('active');
    }
  });

});
