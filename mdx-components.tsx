import defaultMdxComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import Image from 'next/image';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    // Override img for product images
    img: ({ src, alt, ...props }) => {
      if (!src || typeof src !== 'string') return null;
      return (
        <span className="block my-6 rounded-xl overflow-hidden border border-gray-100 bg-gray-50">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={src}
            alt={alt ?? ''}
            className="w-full max-w-sm mx-auto object-contain p-4"
          />
        </span>
      );
    },
    // Spec table with consistent styling
    table: ({ children, ...props }) => (
      <div className="overflow-x-auto my-6">
        <table
          className="w-full text-sm border-collapse"
          {...props}
        >
          {children}
        </table>
      </div>
    ),
    th: ({ children, ...props }) => (
      <th
        className="text-left px-3 py-2 font-medium text-gray-600 bg-gray-50 border border-gray-200 text-xs uppercase tracking-wide"
        {...props}
      >
        {children}
      </th>
    ),
    td: ({ children, ...props }) => (
      <td
        className="px-3 py-2 border border-gray-200 text-gray-900"
        {...props}
      >
        {children}
      </td>
    ),
    ...components,
  };
}
