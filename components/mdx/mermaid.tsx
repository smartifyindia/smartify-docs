'use client';

import { useEffect, useId, useRef } from 'react';

function isDark() {
  return document.documentElement.classList.contains('dark');
}

export function Mermaid({ chart }: { chart: string }) {
  const id = useId();
  const safeId = `mermaid${id.replace(/[^a-zA-Z0-9]/g, '')}`;
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;

    async function render() {
      const mermaid = (await import('mermaid')).default;
      const dark = isDark();

      mermaid.initialize({
        startOnLoad: false,
        theme: dark ? 'dark' : 'neutral',
        themeVariables: dark
          ? {
              primaryColor: '#0e7490',       // darker teal — readable on dark bg
              primaryTextColor: '#ffffff',
              primaryBorderColor: '#0FABBB',
              lineColor: '#94a3b8',
              secondaryColor: '#1e293b',
              tertiaryColor: '#0f172a',
              fontFamily: 'Inter, system-ui, sans-serif',
            }
          : {
              primaryColor: '#0FABBB',
              primaryTextColor: '#ffffff',
              primaryBorderColor: '#0d9aa8',
              lineColor: '#64748b',
              secondaryColor: '#f1f5f9',
              tertiaryColor: '#e2e8f0',
              fontFamily: 'Inter, system-ui, sans-serif',
            },
      });

      const renderId = `${safeId}${dark ? 'd' : 'l'}${Date.now()}`;
      try {
        const { svg } = await mermaid.render(renderId, chart);
        if (!cancelled && ref.current) ref.current.innerHTML = svg;
      } catch (e) {
        console.warn('Mermaid render failed', e);
      }
    }

    void render();

    const observer = new MutationObserver(() => void render());
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });

    return () => { cancelled = true; observer.disconnect(); };
  }, [chart, safeId]);

  return (
    <div
      ref={ref}
      className="my-6 flex justify-center overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-950 p-6"
    />
  );
}
