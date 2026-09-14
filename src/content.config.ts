import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    description: z.string().optional(),
    draft: z.boolean().optional(),
    canonicalUrl: z.string().url().optional(),
    tags: z.array(z.string()).optional(),
    jobForm: z.boolean().optional(),
  }),
});

const guides = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/guides' }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    canonicalUrl: z.string().url().optional(),
    contactForm: z.boolean().optional(),
    donateButton: z.boolean().optional(),
  }),
});

export const collections = { blog, guides };
