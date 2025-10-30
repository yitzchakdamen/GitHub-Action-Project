from google import genai
from google.genai import types
import os

from google import genai


API_KEY = os.getenv("GENAI_API_KEY")
client = genai.Client(api_key=API_KEY)

