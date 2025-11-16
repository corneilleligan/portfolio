// ========================================
// NAVIGATION ENTRE LES PAGES
// ========================================

const navLinks = document.querySelectorAll('[data-nav-link]');
const pages = document.querySelectorAll('[data-page]');

navLinks.forEach(link => {
  link.addEventListener('click', function() {
    const targetPage = this.getAttribute('data-nav-link');
    
    // Animation de sortie pour la page actuelle
    const currentPage = document.querySelector('article.active');
    if(currentPage) {
      currentPage.style.animation = 'fadeOut 0.3s ease';
      setTimeout(() => {
        currentPage.classList.remove('active');
        currentPage.style.animation = '';
      }, 300);
    }
    
    // Mise à jour de la navigation
    navLinks.forEach(l => l.classList.remove('active'));
    this.classList.add('active');
    
    // Animation d'entrée pour la nouvelle page
    setTimeout(() => {
      pages.forEach(page => {
        if(page.getAttribute('data-page') === targetPage) {
          page.classList.add('active');
        }
      });
    }, 300);
  });
});

// Animation fadeOut pour la transition
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeOut {
    from { 
      opacity: 1; 
      transform: translateY(0);
    }
    to { 
      opacity: 0; 
      transform: translateY(-20px);
    }
  }
`;
document.head.appendChild(style);

// ========================================
// CONFIGURATION EMAILJS
// ========================================

// Initialiser EmailJS avec la clé publique
emailjs.init("32E63pgVVxxkLE4md");

// ========================================
// GESTION DU FORMULAIRE DE CONTACT
// ========================================

const contactForm = document.getElementById('contact-form');
const formStatus = document.getElementById('form-status');

if(contactForm) {
  contactForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btn = this.querySelector('.form-btn');
    const originalText = btn.innerHTML;
    
    // Désactiver le bouton et afficher le chargement
    btn.disabled = true;
    btn.innerHTML = '📤 Envoi en cours...';
    formStatus.style.display = 'none';
    
    // Préparer les paramètres pour EmailJS
    const templateParams = {
      from_name: this.querySelector('input[name="name"]').value,
      from_email: this.querySelector('input[name="email"]').value,
      message: this.querySelector('textarea[name="message"]').value,
      to_email: 'corneilleligan@gmail.com'
    };
    
    try {
      // Envoyer l'email via EmailJS
      await emailjs.send('service_c5wt6wr', 'template_bz403aq', templateParams);
      
      // Afficher le message de succès
      formStatus.className = 'form-status success';
      formStatus.textContent = '✓ Message envoyé avec succès! Corneille vous répondra bientôt.';
      formStatus.style.display = 'block';
      
      // Réinitialiser le formulaire
      this.reset();
      
      // Masquer le message après 5 secondes
      setTimeout(() => {
        formStatus.style.display = 'none';
      }, 5000);
      
    } catch (error) {
      console.error('Erreur:', error);
      
      // Afficher le message d'erreur
      formStatus.className = 'form-status error';
      formStatus.textContent = '✗ Une erreur est survenue. Veuillez réessayer ou contacter directement par email.';
      formStatus.style.display = 'block';
    }
    
    // Réactiver le bouton
    btn.disabled = false;
    btn.innerHTML = originalText;
  });
}

// ========================================
// ANIMATION DES CARTES DE COMPÉTENCES
// ========================================

const serviceItems = document.querySelectorAll('.service-item');
serviceItems.forEach(item => {
  item.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-10px) scale(1.02)';
  });
  
  item.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0) scale(1)';
  });
});

// ========================================
// ANIMATION DES PROJETS
// ========================================

const projectCards = document.querySelectorAll('.project-card');
projectCards.forEach((card, index) => {
  // Ajouter une animation de chargement progressive
  card.style.opacity = '0';
  card.style.transform = 'translateY(20px)';
  
  setTimeout(() => {
    card.style.transition = 'all 0.6s ease';
    card.style.opacity = '1';
    card.style.transform = 'translateY(0)';
  }, 100 * index);
});

// ========================================
// ANIMATION DES ÉLÉMENTS DE LA TIMELINE
// ========================================

const timelineItems = document.querySelectorAll('.timeline-item');

// Observer pour animer les éléments au scroll
const observerOptions = {
  threshold: 0.2,
  rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if(entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateX(0)';
    }
  });
}, observerOptions);

timelineItems.forEach(item => {
  observer.observe(item);
});

// ========================================
// EFFET DE HOVER SUR LES LIENS SOCIAUX
// ========================================

const socialLinks = document.querySelectorAll('.social-link');
socialLinks.forEach(link => {
  link.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-5px) scale(1.1)';
  });
  
  link.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0) scale(1)';
  });
});

// ========================================
// ANIMATION DE L'AVATAR AU CHARGEMENT
// ========================================

window.addEventListener('load', function() {
  const avatar = document.querySelector('.avatar-box img');
  if(avatar) {
    avatar.style.transform = 'scale(0)';
    setTimeout(() => {
      avatar.style.transition = 'transform 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
      avatar.style.transform = 'scale(1)';
    }, 200);
  }
});

// ========================================
// ANIMATION DES CONTACTS AU CHARGEMENT
// ========================================

document.addEventListener('DOMContentLoaded', function() {
  const contactItems = document.querySelectorAll('.contact-item');
  contactItems.forEach((item, index) => {
    setTimeout(() => {
      item.style.animation = `slideInLeft 0.5s ease forwards`;
    }, 100 * index);
  });
});

// ========================================
// EFFET RIPPLE SUR LE BOUTON
// ========================================

const formBtn = document.querySelector('.form-btn');
if(formBtn) {
  formBtn.addEventListener('click', function(e) {
    const ripple = document.createElement('span');
    const rect = this.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    this.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  });
}

// Style pour l'effet ripple
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
  .ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: ripple-animation 0.6s ease-out;
    pointer-events: none;
  }
  
  @keyframes ripple-animation {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
`;
document.head.appendChild(rippleStyle);

// ========================================
// EFFET DE TYPING SUR LE TITRE (OPTIONNEL)
// ========================================

function typeWriter(element, text, speed = 100) {
  let i = 0;
  element.textContent = '';
  
  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }
  
  type();
}

// Activer l'effet sur le nom au chargement
window.addEventListener('load', function() {
  const nameElement = document.querySelector('.name');
  if(nameElement) {
    const originalText = nameElement.textContent;
    typeWriter(nameElement, originalText, 80);
  }
});

// ========================================
// SMOOTH SCROLL
// ========================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if(target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

console.log('✨ Portfolio Corneille Ligan chargé avec succès!');