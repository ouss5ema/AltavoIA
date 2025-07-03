import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const features = [
  {
    icon: '📄➡️💬',
    title: 'IA Conversationnelle (RAG)',
    desc: 'Dialoguez avec vos documents. Posez des questions complexes et obtenez des réponses synthétisées et précises, basées sur votre propre contenu.'
  },
  {
    icon: '🧠',
    title: 'Historique & Contexte',
    desc: 'Reprenez vos conversations là où vous les avez laissées. Altavo mémorise le contexte pour un suivi fluide et des réponses toujours plus pertinentes.'
  },
  {
    icon: '🇫🇷',
    title: 'Technologie Souveraine',
    desc: 'Propulsé par les modèles de Mistral AI et l\'infrastructure d\'OVHcloud, garantissant performance, confidentialité et souveraineté de vos données.'
  },
  {
    icon: '🔒',
    title: 'Sécurité & Contrôle',
    desc: 'Vos documents et conversations sont chiffrés et sécurisés. Vous gardez le contrôle total sur vos informations à chaque instant.'
  }
];

export default function LandingPage() {
  const navigate = useNavigate();
  return (
    <div className="landing-root">
      <header className="landing-header">
        <img src="/logo-altavo.png" alt="Altavo Logo" className="landing-logo" />
        <nav className="landing-nav">
          <a href="#features">Fonctionnalités</a>
          <a href="#how-it-works">Comment ça marche ?</a>
          <button className="landing-login-btn" onClick={() => navigate('/connexion')}>Se connecter</button>
        </nav>
      </header>
      <main className="landing-main">
        <section className="landing-hero">
          <div className="landing-hero-content">
            <h1>L'IA qui dialogue avec vos documents</h1>
            <p className="landing-slogan">
              Transformez vos fichiers en une base de connaissance interactive.
              <br />
              Posez vos questions, obtenez des réponses intelligentes.
            </p>
            <div className="landing-btns">
              <button className="landing-cta" onClick={() => navigate('/inscription')}>Commencer gratuitement</button>
            </div>
          </div>
          <div className="landing-hero-img">
            <img src="/ai-illustration.png" alt="Illustration IA" className="ai-illustration" />
          </div>
        </section>

        <section id="features" className="landing-features">
          <h2 className="section-title">Une IA nouvelle génération à votre service</h2>
          <div className="features-grid">
            {features.map((feature, idx) => (
              <div className="feature-card" key={idx}>
                <div className="feature-icon">{feature.icon}</div>
                <h3>{feature.title}</h3>
                <p>{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section id="how-it-works" className="landing-how-it-works">
          <h2 className="section-title">Simple comme 1, 2, 3</h2>
          <div className="how-it-works-steps">
            <div className="step-card">
              <div className="step-number">1</div>
              <h3>Importez vos documents</h3>
              <p>Téléversez vos fichiers PDF, DOCX ou TXT pour construire votre base de connaissances sécurisée.</p>
            </div>
            <div className="step-card">
              <div className="step-number">2</div>
              <h3>Posez vos questions</h3>
              <p>Interrogez l'assistant en langage naturel. Il utilise vos documents comme unique source de vérité.</p>
            </div>
            <div className="step-card">
              <div className="step-number">3</div>
              <h3>Innovez et créez</h3>
              <p>Exploitez les réponses pour vos rapports, analyses, ou pour accélérer votre prise de décision.</p>
            </div>
          </div>
        </section>

      </main>
      <footer className="landing-footer">
        <p>© {new Date().getFullYear()} Altavo. Tous droits réservés.</p>
        <p>Propulsé par l'IA, sécurisé par design.</p>
      </footer>
    </div>
  );
} 