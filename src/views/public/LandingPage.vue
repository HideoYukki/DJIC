<script setup>
import { ref } from 'vue'

const features = ref([
  { icon: '📂', title: 'Zasoby plików', description: 'Przechowywanie wideo 4K i dużych paczek danych. Automatyczna optymalizacja pod urządzenia mobilne.', isFlipped: false },
  { icon: '📈', title: 'Analityka w czasie rzeczywistym', description: 'Logi aktywności uczniów na żywo. Pełna kontrola nad tym, jak użytkownicy konsumują treść.', isFlipped: false },
  { icon: '🛠️', title: 'Edytor struktury kursu', description: 'Zaawansowany system rozdziałów i materiałów. Twórz skomplikowane ścieżki edukacyjne bez wysiłku.', isFlipped: false },
  { icon: '🏆', title: 'Grywalizacja i XP', description: 'System odznak, punktów XP i certyfikatów motywuje uczniów do ukończenia kursów.', isFlipped: false },
])

const testimonials = ref([
  { name: 'Anna Kowalska', role: 'Twórca kursów IT', text: 'W ciągu miesiąca wygenerowałam 12 000 zł z własnego kursu Vue.js. Platforma zajęła się wszystkim.', avatar: 'A' },
  { name: 'Marek Wiśniewski', role: 'Trener korporacyjny', text: 'Analityka postępów uczniów to game-changer. Wiem dokładnie, gdzie zatrzymują się moi studenci.', avatar: 'M' },
  { name: 'Karolina Nowak', role: 'UX Designer', text: 'Edytor quizów i certyfikaty zautomatyzowały 80% mojej pracy. Polecam każdemu twórcy treści.', avatar: 'K' },
])
</script>

<template>
  <div class="landing-wrapper">

    <!-- HERO -->
    <section class="hero">
      <div class="hero-bg">
        <div class="hero-glow hero-glow-1"></div>
        <div class="hero-glow hero-glow-2"></div>
      </div>
      <div class="container hero-content">
        <span class="badge">Professional Learning Systems</span>
        <h1>Architektura Twojej <span>Wiedzy</span></h1>
        <p>Skoncentruj się na merytoryce. My dostarczymy silnik, który zmieni Twoje materiały w profesjonalne doświadczenie edukacyjne.</p>
        <div class="hero-actions">
          <router-link to="/register" class="btn-primary-large">Załóż darmowe konto</router-link>
          <router-link to="/courses" class="btn-ghost">Przeglądaj kursy →</router-link>
        </div>
        <div class="hero-stats">
          <div class="hero-stat"><strong>500+</strong><span>Kursów</span></div>
          <div class="hero-stat-div"></div>
          <div class="hero-stat"><strong>12 000+</strong><span>Uczniów</span></div>
          <div class="hero-stat-div"></div>
          <div class="hero-stat"><strong>4.8/5</strong><span>Śr. ocena</span></div>
        </div>
      </div>
    </section>

    <!-- CIEMNA SEKCJA PRZEJŚCIOWA -->
    <section class="about-dark">
      <div class="container">
        <h2>Wszystko pod Twoją kontrolą</h2>
        <p>DJIC Platform to stabilność, bezpieczeństwo danych i przejrzysty model rozliczeń. Twój kontent, Twoje zasady, nasza technologia.</p>
      </div>
    </section>

    <!-- FUNKCJE — karty z efektem odwrócenia -->
    <section class="features">
      <div class="container">
        <div class="section-header">
          <h2>Narzędzia Projektowe</h2>
          <p>Kliknij w kartę, aby poznać szczegóły techniczne.</p>
        </div>
        <div class="card-grid">
          <div
            v-for="(f, i) in features"
            :key="i"
            class="flip-card"
            :class="{ flipped: f.isFlipped }"
            @click="f.isFlipped = !f.isFlipped"
          >
            <div class="flip-card-inner">
              <div class="flip-card-front">
                <div class="card-icon">{{ f.icon }}</div>
                <h3>{{ f.title }}</h3>
                <p class="hint">Kliknij, aby odwrócić</p>
              </div>
              <div class="flip-card-back">
                <h3>Specyfikacja</h3>
                <p>{{ f.description }}</p>
                <div class="specs"><span>99.9% Uptime</span><span>SSL Encryption</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- STATYSTYKI -->
    <section class="stats-bar">
      <div class="container stats-flex">
        <div class="stat-box"><span class="num">128-bit</span><span class="lab">Szyfrowanie AES</span></div>
        <div class="stat-box"><span class="num">No-Limit</span><span class="lab">Transfer danych</span></div>
        <div class="stat-box"><span class="num">24/7</span><span class="lab">Support techniczny</span></div>
      </div>
    </section>

    <!-- OPINIE -->
    <section class="testimonials">
      <div class="container">
        <div class="section-header">
          <h2>Twórcy o nas</h2>
          <p>Dołącz do setek profesjonalistów, którzy budują swoje biznesy edukacyjne na DJIC Platform.</p>
        </div>
        <div class="testimonial-grid">
          <div v-for="(t, i) in testimonials" :key="i" class="testimonial-card">
            <p class="quote">"{{ t.text }}"</p>
            <div class="author">
              <div class="avatar">{{ t.avatar }}</div>
              <div>
                <strong>{{ t.name }}</strong>
                <small>{{ t.role }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA KOŃCOWE -->
    <section class="cta-final">
      <div class="container">
        <h2>Gotowy na wdrożenie?</h2>
        <p>Dołącz do profesjonalistów i uruchom swój system edukacyjny w kilka minut.</p>
        <router-link to="/register" class="btn-primary-large">Zacznij teraz — bez opłat na start</router-link>
      </div>
    </section>

  </div>
</template>

<style scoped lang="scss">
.landing-wrapper { width: 100%; overflow-x: hidden; }

.container {
  width: 100%;
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 1.5rem;
  box-sizing: border-box;
}

/* HERO */
.hero {
  min-height: 100vh;
  background: #020617;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}
.hero-bg { position: absolute; inset: 0; pointer-events: none; }
.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.25;
}
.hero-glow-1 { width: 800px; height: 800px; background: #3b82f6; top: -200px; left: -200px; }
.hero-glow-2 { width: 600px; height: 600px; background: #6366f1; bottom: -200px; right: -100px; }

.hero-content {
  position: relative;
  padding-top: 100px;
  padding-bottom: 80px;
  color: white;

  .badge {
    display: inline-block;
    color: #60a5fa;
    font-weight: 800;
    letter-spacing: 2px;
    font-size: 0.8rem;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    padding: 0.3rem 0.8rem;
    border-radius: 2rem;
  }

  h1 {
    font-size: 5rem;
    font-weight: 900;
    line-height: 1.05;
    margin: 0 0 1.5rem;
    max-width: 800px;
    span { color: #3b82f6; }
  }

  p {
    font-size: 1.3rem;
    color: #94a3b8;
    max-width: 580px;
    line-height: 1.7;
    margin-bottom: 3rem;
  }
}

.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 4rem;
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 2rem;

  .hero-stat {
    strong { display: block; font-size: 1.8rem; font-weight: 900; color: white; }
    span { font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
  }
  .hero-stat-div { width: 1px; height: 40px; background: rgba(255,255,255,0.1); }
}

/* DARK SECTION */
.about-dark {
  background: #0f172a;
  padding: 8rem 0;
  color: white;
  text-align: center;

  h2 { font-size: 2.8rem; font-weight: 800; margin-bottom: 1.5rem; color: #3b82f6; }
  p { font-size: 1.2rem; max-width: 800px; margin: 0 auto; line-height: 1.8; color: #94a3b8; }
}

/* FEATURES */
.features {
  padding: 8rem 0;
  background: #f8fafc;

  .section-header {
    text-align: center;
    margin-bottom: 5rem;
    h2 { font-size: 2.5rem; color: #1e293b; font-weight: 800; }
    p { color: #64748b; font-size: 1.05rem; margin-top: 0.5rem; }
  }

  .card-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
  }
}

.flip-card {
  height: 380px;
  perspective: 1000px;
  cursor: pointer;

  &.flipped .flip-card-inner { transform: rotateY(180deg); }
}
.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.7s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
}
.flip-card-front, .flip-card-back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  border-radius: 1.5rem;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.1);
  box-sizing: border-box;
}
.flip-card-front {
  background: white;
  border: 1px solid #e2e8f0;
  .card-icon { font-size: 3rem; margin-bottom: 1.5rem; }
  h3 { font-size: 1.4rem; color: #1e293b; font-weight: 700; }
  .hint { color: #3b82f6; font-size: 0.7rem; text-transform: uppercase; font-weight: 700; margin-top: 1.5rem; }
}
.flip-card-back {
  background: #3b82f6;
  color: white;
  transform: rotateY(180deg);
  h3 { font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.2); width: 100%; padding-bottom: 1rem; margin-bottom: 1rem; }
  p { line-height: 1.6; font-size: 0.9rem; margin-bottom: 2rem; }
  .specs { display: flex; gap: 0.75rem; font-size: 0.7rem; font-weight: 700; opacity: 0.85; }
}

/* STATS */
.stats-bar {
  background: white;
  padding: 6rem 0;
  .stats-flex {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 2rem;
  }
  .stat-box {
    text-align: center;
    .num { display: block; font-size: 3rem; font-weight: 900; color: #0f172a; }
    .lab { color: #64748b; text-transform: uppercase; font-size: 0.85rem; font-weight: 700; }
  }
}

/* TESTIMONIALS */
.testimonials {
  background: #020617;
  padding: 8rem 0;
  .section-header {
    text-align: center;
    margin-bottom: 4rem;
    h2 { font-size: 2.5rem; font-weight: 800; color: white; }
    p { color: #64748b; margin-top: 0.5rem; }
  }
  .testimonial-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
  }
}

.testimonial-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 1.5rem;
  padding: 2rem;

  .quote {
    color: #cbd5e1;
    font-size: 0.95rem;
    line-height: 1.7;
    margin-bottom: 1.5rem;
    font-style: italic;
  }
  .author {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    .avatar {
      width: 40px; height: 40px;
      background: linear-gradient(135deg, #3b82f6, #6366f1);
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; color: white;
    }
    strong { display: block; color: #f1f5f9; font-size: 0.9rem; }
    small { color: #64748b; font-size: 0.78rem; }
  }
}

/* CTA */
.cta-final {
  background: #020617;
  border-top: 1px solid rgba(255,255,255,0.05);
  padding: 10rem 0;
  text-align: center;
  color: white;
  h2 { font-size: 3rem; font-weight: 800; margin-bottom: 1.5rem; }
  p { font-size: 1.1rem; color: #94a3b8; margin-bottom: 3rem; }
}

/* BUTTONS */
.btn-primary-large {
  display: inline-block;
  background: #3b82f6;
  color: white;
  padding: 1rem 2.5rem;
  border-radius: 0.8rem;
  text-decoration: none;
  font-weight: 800;
  font-size: 1.05rem;
  transition: all 0.25s;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
  &:hover { background: #2563eb; transform: translateY(-3px); box-shadow: 0 16px 30px rgba(59, 130, 246, 0.45); }
}
.btn-ghost {
  display: inline-block;
  color: #94a3b8;
  padding: 1rem 2rem;
  border-radius: 0.8rem;
  text-decoration: none;
  font-weight: 700;
  font-size: 1rem;
  border: 1px solid rgba(255,255,255,0.1);
  transition: all 0.2s;
  &:hover { color: white; border-color: rgba(255,255,255,0.25); }
}

/* RESPONSYWNOŚĆ */
@media (max-width: 1100px) {
  .features .card-grid { grid-template-columns: repeat(2, 1fr); }
  .testimonials .testimonial-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  .hero-content h1 { font-size: 3rem; }
  .features .card-grid { grid-template-columns: 1fr; }
  .testimonials .testimonial-grid { grid-template-columns: 1fr; }
  .hero-stats { flex-wrap: wrap; gap: 1rem; }
}
</style>