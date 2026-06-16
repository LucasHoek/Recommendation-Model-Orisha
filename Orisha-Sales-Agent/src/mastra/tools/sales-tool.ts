import { createTool } from '@mastra/core/tools';
import { z } from 'zod';

const BASE_URL = process.env.SALES_API_URL || "http://localhost:5000";

export const salesTool = createTool({
  id: "get-advice",
  description: "Fetch sales advice for a klantcode",
  inputSchema: z.object({
    klantcode: z.number(),
  }),
  execute: async ({ klantcode }) => {
    const url = `${BASE_URL}/api/customeradvice?klantcode=${klantcode}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch sales advice: ${response.statusText}`);
    }

    return await response.json();
  },
});
async function getAdvice(klantcode: string) {
  // Try the JSON API endpoint first
  const apiUrl = `/api/customeradvice?klantcode=${encodeURIComponent(klantcode)}`;

  let resp = await fetch(apiUrl, {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });

  // If the JSON endpoint is not available, try the HTML endpoint and attempt to extract JSON
  if (!resp.ok) {
    const htmlUrl = `/customeradvice?klantcode=${encodeURIComponent(klantcode)}`;
    resp = await fetch(htmlUrl, {
      method: 'GET',
      headers: {
        'Accept': 'text/html',
      },
    });

    if (!resp.ok) {
      throw new Error(`Backend returned ${resp.status} for klantcode ${klantcode}`);
    }

    const html = await resp.text();
    const markerStart = '<script id="results-json" type="application/json">';
    const markerEnd = '</script>';
    const startIdx = html.indexOf(markerStart);
    if (startIdx !== -1) {
      const jsonStart = startIdx + markerStart.length;
      const endIdx = html.indexOf(markerEnd, jsonStart);
      if (endIdx !== -1) {
        const jsonText = html.slice(jsonStart, endIdx).trim();
        try {
          const parsed = JSON.parse(jsonText);
          validateAndReturn(parsed);
          return parsed;
        } catch (err) {
          throw new Error('Failed to parse embedded JSON from HTML response');
        }
      }
    }

    throw new Error(
      'No JSON response found. Please expose a JSON API at /api/customeradvice?klantcode=... ' +
      'or embed results JSON in the HTML inside <script id="results-json" type="application/json">...</script>.'
    );
  }

  const data = await resp.json();
  validateAndReturn(data);
  return data;
}

function validateAndReturn(data: unknown) {
  const schema = z.object({
    results: z.array(
      z.object({
        id: z.string(),
        name: z.string(),
        description: z.string().optional(),
        score: z.number().optional(),
        url: z.string().optional(),
      })
    ),
  });

  const parsed = schema.safeParse(data);
  if (!parsed.success) {
    // Throw a helpful error so the caller knows the backend shape is wrong
    throw new Error('Invalid response shape from backend: ' + JSON.stringify(parsed.error.format()));
  }
  return parsed.data;
}
