import { createStep, createWorkflow } from '@mastra/core/workflows';
import { z } from 'zod';

// ---- SCHEMAS ----
const salesInputSchema = z.object({
  klantcode: z.number().describe("The klantcode to generate sales advice for"),
});

const salesResultSchema = z.object({
  results: z.any(), // You can refine this if you know the structure
});

// ---- STEP 1: FETCH SALES ADVICE ----
const fetchSalesAdvice = createStep({
  id: "fetch-sales-advice",
  description: "Fetches top-N sales recommendations for a klantcode",
  inputSchema: salesInputSchema,
  outputSchema: salesResultSchema,

  execute: async ({ inputData }) => {
    if (!inputData) {
      throw new Error("Input data not found");
    }

    const { klantcode } = inputData;

    // IMPORTANT:
    // You must expose your Python logic or replicate get_hybrid_topn in Node.
    // Here we assume you have a JS wrapper or service call:
    const { getHybridTopN } = await import("./services/salesService");

    const results = await getHybridTopN({
      klantcode,
      topn: 5,
    });

    return { results };
  },
});

// ---- STEP 2: FORMAT ADVICE USING AN AGENT ----
const formatSalesAdvice = createStep({
  id: "format-sales-advice",
  description: "Formats the sales recommendations into a readable summary",
  inputSchema: salesResultSchema,
  outputSchema: z.object({
    adviceText: z.string(),
  }),

  execute: async ({ inputData, mastra }) => {
    if (!inputData) {
      throw new Error("Sales results not found");
    }

    const agent = mastra?.getAgent("salesAgent");
    if (!agent) {
      throw new Error("Sales agent not found");
    }

    const prompt = `
Generate a clear, structured sales recommendation summary based on the following results:

${JSON.stringify(inputData.results, null, 2)}

Format the output as:

📌 SALES ADVICE SUMMARY
Klantcode: ${inputData.results?.klantcode ?? "Unknown"}

Top Recommendations:
• [Product] — [Reason]
• [Product] — [Reason]
• [Product] — [Reason]

Include:
- Why each product fits the customer
- Cross‑sell or upsell opportunities
- Any patterns in past purchases
`;

    const response = await agent.stream([
      { role: "user", content: prompt },
    ]);

    let adviceText = "";

    for await (const chunk of response.textStream) {
      process.stdout.write(chunk);
      adviceText += chunk;
    }

    return { adviceText };
  },
});

// ---- WORKFLOW ----
const salesWorkflow = createWorkflow({
  id: "sales-workflow",
  inputSchema: salesInputSchema,
  outputSchema: z.object({
    adviceText: z.string(),
  }),
})
  .then(fetchSalesAdvice)
  .then(formatSalesAdvice);

salesWorkflow.commit();

export { salesWorkflow };