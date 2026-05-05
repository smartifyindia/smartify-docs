import defaultMdxComponents from 'fumadocs-ui/mdx';
import { ImageZoom } from 'fumadocs-ui/components/image-zoom';
import { Cards, Card } from 'fumadocs-ui/components/card';
import { Steps, Step } from 'fumadocs-ui/components/steps';
import { Callout } from 'fumadocs-ui/components/callout';
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';
import { Accordion, Accordions } from 'fumadocs-ui/components/accordion';
import { Mermaid } from '@/components/mdx/mermaid';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    // Product images — zoomable with styled container, handles string & StaticImport src
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    img: ({ src, alt, ...props }: any) => {
      if (!src) return null;
      return (
        <span className="block my-6 rounded-xl overflow-hidden border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900">
          <ImageZoom
            src={src}
            alt={alt ?? ''}
            className="w-full max-w-sm mx-auto object-contain p-4"
            {...props}
          />
        </span>
      );
    },
    // Spec table with consistent styling
    table: ({ children, ...props }) => (
      <div className="overflow-x-auto my-6">
        <table className="w-full text-sm border-collapse" {...props}>
          {children}
        </table>
      </div>
    ),
    th: ({ children, ...props }) => (
      <th
        className="text-left px-3 py-2.5 font-semibold text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700 text-xs uppercase tracking-wide"
        {...props}
      >
        {children}
      </th>
    ),
    td: ({ children, ...props }) => (
      <td
        className="px-3 py-2.5 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 text-sm"
        {...props}
      >
        {children}
      </td>
    ),
    Cards,
    Card,
    Steps,
    Step,
    Callout,
    Tab,
    Tabs,
    Accordion,
    Accordions,
    Mermaid,
    ...components,
  };
}
