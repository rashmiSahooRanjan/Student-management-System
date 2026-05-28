// static/js/animation.js
// Futuristic Animations & Background Effects

document.addEventListener('DOMContentLoaded', () => {
    createFloatingParticles();
    initButtonHoverEffects();
    initGlassHover();
});

// Create Floating Background Particles
function createFloatingParticles() {
    const particlesContainer = document.querySelector('.floating-particles');
    if (!particlesContainer) return;

    for (let i = 0; i < 60; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        const size = Math.random() * 6 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${Math.random() * 100}vw`;
        particle.style.top = `${Math.random() * 100}vh`;
        particle.style.opacity = Math.random() * 0.6 + 0.2;
        particle.style.animationDuration = `${Math.random() * 25 + 15}s`;
        particle.style.animationDelay = `-${Math.random() * 30}s`;
        
        particlesContainer.appendChild(particle);
    }
}

// Button Hover Glow Effect
function initButtonHoverEffects() {
    const buttons = document.querySelectorAll('.glow-btn');
    buttons.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            btn.style.backgroundPosition = `${x}px ${y}px`;
        });
    });
}

// Enhanced Glass Card Hover
function initGlassHover() {
    const cards = document.querySelectorAll('.glass-card');
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width;
            const y = (e.clientY - rect.top) / rect.height;
            
            card.style.transform = `perspective(1000px) rotateX(${(y - 0.5) * 12}deg) rotateY(${(0.5 - x) * 12}deg)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    });
}

// Add CSS for particles dynamically
const style = document.createElement('style');
style.innerHTML = `
.particle {
    position: absolute;
    background: #00f5ff;
    border-radius: 50%;
    animation: floatParticle linear infinite;
    box-shadow: 0 0 8px #00f5ff;
}

@keyframes floatParticle {
    0% { transform: translateY(0) scale(1); }
    100% { transform: translateY(-120vh) scale(0.6); }
}
`;
document.head.appendChild(style);