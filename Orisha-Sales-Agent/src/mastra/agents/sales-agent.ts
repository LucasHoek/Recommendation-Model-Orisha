import { Agent } from '@mastra/core/agent';
import { Memory } from '@mastra/memory';
import { salesTool } from '../tools/sales-tool'; 
import { scorers } from '../scorers/sales-scorer';

export const salesAgent = new Agent({
  id: 'sales-agent',
  name: 'Sales Agent',
  instructions: `You are a helpful sales assistant that helps sales representatives get the recommended item list details for specific customers. When responding:
- Always ask for a customer ID if none is provided.
- If the customer ID isn't in the correct format, ask for it again.
- Include relevant details like product names, prices, and availability.
- Keep responses concise but informative.

Use the salesTool (id: get-advice) to fetch the current top 5 recommended items for a given klantcode.`,
  model: 'google/gemini-2.5-pro',
  tools: { salesTool }, // provide the tool object here
  scorers: {
    toolCallAppropriateness: {
      scorer: scorers.toolCallAppropriatenessScorer,
      sampling: { type: 'ratio', rate: 1 },
    },
    completeness: {
      scorer: scorers.completenessScorer,
      sampling: { type: 'ratio', rate: 1 },
    },
    translation: {
      scorer: scorers.translationScorer,
      sampling: { type: 'ratio', rate: 1 },
    },
  },
  memory: new Memory(),
});

export default salesAgent;
