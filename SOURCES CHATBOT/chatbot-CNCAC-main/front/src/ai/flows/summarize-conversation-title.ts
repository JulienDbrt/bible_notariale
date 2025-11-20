'use server';

/**
 * @fileOverview A flow that automatically sets the title of a newly created conversation by summarizing the first few messages using GenAI.
 *
 * - summarizeConversationTitle - A function that handles the summarization process.
 * - SummarizeConversationTitleInput - The input type for the summarizeConversationTitle function.
 * - SummarizeConversationTitleOutput - The return type for the summarizeConversationTitle function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SummarizeConversationTitleInputSchema = z.object({
  messages: z
    .string()
    .describe('The first few messages of the conversation.'),
});
export type SummarizeConversationTitleInput = z.infer<typeof SummarizeConversationTitleInputSchema>;

const SummarizeConversationTitleOutputSchema = z.object({
  title: z.string().describe('A short summary of the conversation.'),
});
export type SummarizeConversationTitleOutput = z.infer<typeof SummarizeConversationTitleOutputSchema>;

export async function summarizeConversationTitle(
  input: SummarizeConversationTitleInput
): Promise<SummarizeConversationTitleOutput> {
  return summarizeConversationTitleFlow(input);
}

const prompt = ai.definePrompt({
  name: 'summarizeConversationTitlePrompt',
  input: {schema: SummarizeConversationTitleInputSchema},
  output: {schema: SummarizeConversationTitleOutputSchema},
  prompt: `Summarize the following conversation in a short title:

  {{messages}}`,
});

const summarizeConversationTitleFlow = ai.defineFlow(
  {
    name: 'summarizeConversationTitleFlow',
    inputSchema: SummarizeConversationTitleInputSchema,
    outputSchema: SummarizeConversationTitleOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
