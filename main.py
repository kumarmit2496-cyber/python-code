from openai import  OpenAI
from dotenv import load_dotenv
import os

#===============================
#Load Enviornment Variable
#================================

load_dotenv()

#=====================
#Read Open API Key
#=====================
api_key=os.getenv("OPENAI_API_KEY")

#=========================
#Create OpenAI Client
#==========================
client=OpenAI(api_key)

#=========================
#Funcation to call GPT Model
#==========================

def ask_gpt(input):

   response = client.responses.create(
             model= "gpt-5-mini",
             input = input,
   )
   return response.output_text
