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


load_dotenv('.env')
ACCESS_TOKEN = environ.get('ACCESS_TOKEN', '')
CHANNEL_SECRET = environ.get('CHANNEL_SECRET', '')

app = Flask(__name__)

line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


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
    if text.lower() == "pixiv":
        p = Pixiv()
        rank_list = p.get_rank_data()
        bubble_item_list = []
        for rank_item in rank_list['contents']:
            bubble_container = get_pixiv_bubble_messages(rank_item)
            bubble_item_list.append(bubble_container)

        messages = []
        chunk_list = get_chunk_list(bubble_item_list)
        for item_list in chunk_list:
            message = FlexSendMessage(
                alt_text='hello',
                contents=CarouselContainer(
                    contents=item_list
                )
            )
            messages.append(message)

        line_bot_api.reply_message(
            event.reply_token,
            messages)
    elif text.lower() == "nico":
        p = Niconico()
        rank_list = p.get_rank_data()
        bubble_item_list = []
        for rank_item in rank_list['contents']:
            bubble_container = get_niconico_bubble_messages(rank_item)
            bubble_item_list.append(bubble_container)

        messages = []
        chunk_list = get_chunk_list(bubble_item_list)
        for item_list in chunk_list:
            message = FlexSendMessage(
                alt_text='hello',
                contents=CarouselContainer(
                    contents=item_list
                )
            )
            messages.append(message)

        # if len(messages) > 5:
        #     chunk_list = get_chunk_list(messages, 5)
        #     for messages in chunk_list:
        #         line_bot_api.reply_message(
        #             event.reply_token,
        #             messages)
        #         break
        # else:
        line_bot_api.reply_message(
            event.reply_token,
            messages)
    else:
        message = TextSendMessage(text=text)

        line_bot_api.reply_message(
            event.reply_token,
            message)


def get_chunk_list(data=[], chunk_size=12):
    n = chunk_size
    return [data[i:i + n] for i in range(0, len(data), n)]


if __name__ == "__main__":
    app.run('127.0.0.1', 8000, True)
