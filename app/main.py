import traceback
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, RichMenu, RichMenuArea, RichMenuBounds, RichMenuSize, URIAction, MessageAction,
    FlexSendMessage, FlexComponent, FlexContainer, BubbleContainer, ImageComponent, BoxComponent, TextComponent, SeparatorComponent,
    ButtonComponent, CarouselContainer
)

from dotenv import load_dotenv
from os import environ
import os
import openai


openai.api_key = os.getenv("OPENAI_API_KEY")

load_dotenv('.env')
ACCESS_TOKEN = environ.get('ACCESS_TOKEN', '')
CHANNEL_SECRET = environ.get('CHANNEL_SECRET', '')

app = Flask(__name__)

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
init_message = {"role": "system", "content": "You are a helpful assistant. Answer as concisely as possible with a little humor expression."}
messages = []


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    print(request.headers)
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    except Exception as e:
        print(e)
        print(traceback.print_exception(e))

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    global messages
    if text == "@reset":  # by rich menu
        messages = []
        output = generate_response("ハロー")
        messages.append({"role": "assistant", "content": output})
    else:
        output = generate_response(text)
        messages.append({"role": "assistant", "content": output})

    message = TextSendMessage(text=output)

    line_bot_api.reply_message(
        event.reply_token,
        message)


def generate_response(prompt):
    messages.append({"role": "user", "content":prompt})
    completion=openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = messages
    )
    
    message=completion.choices[0].message.content
    return message


def get_chunk_list(data=[], chunk_size=12):
    n = chunk_size
    return [data[i:i + n] for i in range(0, len(data), n)]


if __name__ == "__main__":
    app.run('127.0.0.1', 8000, True)
