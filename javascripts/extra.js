/**
 * GeekMind Docs — Subtle page interactions.
 *
 * Principles:
 * - Scroll-reveal cards/images only
 * - No complex animations
 * - Works with MkDocs instant navigation
 */

(function () {
  'use strict';

  // ── Scroll Reveal ────────────────────────────────────────
  function initReveal() {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -24px 0px' }
    );

    const elements = document.querySelectorAll(
      '.md-typeset .admonition, .md-typeset details, ' +
      '.md-typeset img, .md-typeset table'
    );

    elements.forEach((el) => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(12px)';
      el.style.transition =
        'opacity 0.45s ease-out, transform 0.45s ease-out';
      observer.observe(el);
    });
  }

  // ── Page load fade ───────────────────────────────────────
  function initPageFade() {
    const content = document.querySelector('.md-content__inner');
    if (!content) return;
    content.style.opacity = '0';
    content.style.transition = 'opacity 0.3s ease-out';
    requestAnimationFrame(() => {
      content.style.opacity = '1';
    });
  }

  // ── MkDocs SPA re-trigger ────────────────────────────────
  function watchContentChanges() {
    const el = document.querySelector('.md-content__inner');
    if (!el) return;
    const observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.type === 'childList' && m.addedNodes.length > 0) {
          initPageFade();
          initReveal();
          break;
        }
      }
    });
    observer.observe(el, { childList: true });
  }

  // ── Boot ─────────────────────────────────────────────────
  function boot() {
    initPageFade();
    initReveal();
    watchContentChanges();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
