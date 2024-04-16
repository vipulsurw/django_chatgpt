
import openai
from decouple import config
from django.http import HttpResponse
from django.shortcuts import render
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# Internal imports
from .models import Conversation
from .utils import send_message, logger

# Set up the OpenAI API client
openai.api_key = config("OPENAI_API_KEY")

def index():
    return HttpResponse("Hello")


@csrf_exempt
def reply(request):
    # Extract the phone number from the incoming webhook request
    whatsapp_number = request.POST.get('From').split("whatsapp:")[-1]
    print(f"Sending the ChatGPT response to this number: {whatsapp_number}")

    # Call the OpenAI API to generate text with ChatGPT
    body = request.POST.get('Body', '')
    messages = [{"role": "user", "content": body}]
    messages.append({"role": "system", "content": "You're an investor, a serial founder and you've sold many startups. You understand nothing but business."})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200,
        n=1,
        stop=None,
        temperature=0.5
        )

    # The generated text
    chatgpt_response = response.choices[0].message.content

    
    # Store the conversation in the database
    try:

        with transaction.atomic():
                conversation = Conversation.objects.create(
                    sender=whatsapp_number,
                    message=body,
                    response=chatgpt_response
                )
                conversation.save()
                logger.info(f"Conversation #{conversation.id} stored in database")
    except Exception as e:
        logger.error(f"Error storing conversation in database: {e}")
        return HttpResponse(status=500)

    send_message(whatsapp_number, chatgpt_response)
    return HttpResponse('')