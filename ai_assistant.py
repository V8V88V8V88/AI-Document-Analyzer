import os
import json
import logging
import google.generativeai as genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class AIAssistant:
    """Handles AI-powered document analysis and interaction"""
    
    def __init__(self):
        try:
            # Configure the generative AI model
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            # Handle cases where the API key is not set or invalid
            raise ValueError("Failed to configure Gemini API. Please check your API key.") from e
    
    def generate_summary(self, document_text):
        """Generate a 150-word summary of the document"""
        try:
            prompt = f"Summarize the following document in about 150 words:\n\n{document_text}"
            
            response = self.model.generate_content(prompt)
            
            return response.text or "Unable to generate summary"
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def answer_question(self, document_text, question):
        """Answer a question based solely on the document content with justification."""
        try:
            prompt = f"""
            You are an AI assistant for a document analysis tool. Your primary function is to answer questions based *only* on the provided document content.

            **Crucial Rules:**
            1.  **Grounding:** Base your entire answer strictly on the text of the document. Do not use any external knowledge or make assumptions.
            2.  **No Hallucination:** If the answer cannot be found in the document, you MUST state: "I could not find an answer to that in the document." Do not try to infer or guess.
            3.  **Justification:** You MUST provide a direct quote from the document that justifies your answer. The quote should be clearly marked and relevant.

            **Document Text:**
            ---
            {document_text}
            ---

            **Question:** {question}

            **Output Format:**
            Answer: [Your answer here]
            Justification: "[Direct quote from the document that supports your answer]"
            """
            
            response = self.model.generate_content(prompt)
            
            return response.text or "Unable to generate answer"
        
        except Exception as e:
            return f"Error answering question: {str(e)}"
    
    def generate_quiz(self, document_text):
        """Generate 3 logic-based quiz questions from the document"""
        try:
            prompt = f"""
            You are an AI assistant creating a quiz for a document analysis tool. Your task is to generate 3 challenging, logic-based questions that test a user's understanding of the provided document.

            **Crucial Rules:**
            1.  **Logic-Based:** Questions should require inference, understanding of relationships (cause-effect, compare-contrast), or application of concepts found in the text. Avoid simple fact-recall questions.
            2.  **Grounded:** Each question and its correct answer must be directly supported by the document's content.
            3.  **JSON Format:** The output MUST be a valid JSON array of objects.

            **Document Text:**
            ---
            {document_text}
            ---

            **JSON Output Example:**
            [
                {{
                    "question": "Based on the project's timeline, what is the most likely consequence of a delay in phase 2?",
                    "answer": "A delay in phase 2 would likely postpone the final product launch, as phase 3 is dependent on its completion."
                }},
                {{
                    "question": "How does the author's tone in the introduction contrast with the conclusion?",
                    "answer": "The introduction is optimistic, highlighting potential benefits, while the conclusion is more cautious, emphasizing potential risks."
                }}
            ]
            """
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                logging.error(f"Failed to decode JSON for quiz generation. Raw text: {response.text}")
                return []
        
        except Exception as e:
            logging.error(f"Error generating quiz: {e}")
            return []
    
    def evaluate_answer(self, document_text, question, user_answer, correct_answer):
        """Evaluate user's answer and provide justified feedback."""
        try:
            prompt = f"""
            You are an AI assistant evaluating a user's quiz answer for a document analysis tool.

            **Crucial Rules:**
            1.  **Evaluation:** Determine if the user's answer is correct, partially correct, or incorrect based on the provided correct answer and the document text.
            2.  **Justification:** Your feedback MUST explain *why* the user's answer is correct or incorrect, referencing specific information from the document to support your evaluation.
            3.  **Tone:** Be encouraging and helpful.

            **Document Text:**
            ---
            {document_text}
            ---

            **Question:** {question}
            **The User's Answer:** {user_answer}
            **The Correct Answer:** {correct_answer}
            
            **Feedback:**
            """
            
            response = self.model.generate_content(prompt)
            
            return response.text or "Unable to evaluate answer"
        
        except Exception as e:
            return f"Error evaluating answer: {str(e)}"
