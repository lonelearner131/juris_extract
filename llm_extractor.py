import os
from typing import List, Literal
from dotenv import load_dotenv
import instructor
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 1. Load the environment variables FIRST
load_dotenv()

# 2. Initialize the Google GenAI client and wrap it with Instructor
raw_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
client = instructor.from_genai(raw_client, mode=instructor.Mode.GENAI_STRUCTURED_OUTPUTS)

# --- 1. Define the Strict JSON Schema ---
class ActionItem(BaseModel):
    action_type: Literal["Compliance", "Appeal Consideration", "Policy Review", "Other"] = Field(
        description="Categorize the nature of the action required."
    )
    compliance_action: str = Field(
        description="The specific action required by the judgment."
    )
    responsible_department: str = Field(
        description="The government department responsible. Write 'Unspecified' if unknown."
    )
    timeline_days: str = Field(
        description="The exact timeframe (e.g., '60 days'). If none, write 'Statutory Period'."
    )
    confidence_score: int = Field(
        description="A score from 0 to 100 representing confidence.", ge=0, le=100
    )
    verbatim_source_quote: str = Field(
        description="CRITICAL: The EXACT, verbatim quote from the text. Do not paraphrase."
    )

class ActionPlan(BaseModel):
    case_title: str = Field(description="The name or title of the case (e.g., 'State vs. John Doe').")
    date_of_order: str = Field(description="The date the judgment was passed.")
    parties_involved: str = Field(description="The Petitioner(s) and Respondent(s).")
    case_summary: str = Field(description="A brief 2-sentence summary of the judgment.")
    action_items: List[ActionItem] = Field(description="List of all required compliance actions.")

# --- 2. The Extraction Engine ---
def extract_action_plan(retrieved_context: str) -> ActionPlan:
    print("Sending context to Google AI Studio (Gemini 3.8 Flash) for strict JSON Extraction...")
    
    action_plan = client.chat.completions.create(
        model="gemini-3.5-flash-lite",
        response_model=ActionPlan,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert Indian Legal AI Assistant working for the government. "
                    "Read extracts from court judgments and output strict, factual action plans. "
                    "Extract the case title, date, parties involved, and all compliance directives. "
                    "Categorize each action carefully into Compliance, Appeal Consideration, Policy Review, or Other. "
                    "You MUST extract exact verbatim quotes for every action item."
                )
            },
            {
                "role": "user",
                "content": f"Extract the action plan from the following retrieved context:\n\n{retrieved_context}"
            }
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
        ),
    )
    
    return action_plan