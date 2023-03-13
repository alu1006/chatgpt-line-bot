import os
from dotenv import load_dotenv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
#update
app = Flask(__name__)
load_dotenv()
# 從環境變量中讀取 LINE Channel Access Token 與 Channel Secret
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
# 設置 OpenAI API 的 API key
openai.api_key = os.getenv("OPENAI_API_KEY")



@app.route("/callback", methods=["POST"])
def callback():
    # 獲取 X-Line-Signature 首部內容
    signature = request.headers["X-Line-Signature"]
    # 獲取請求內容主體
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        # 驗證 LINE 請求的簽名是否正確
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 當簽名不正確時，回應 400 HTTP 錯誤
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 當收到 TextMessage 時回應相同的內容
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))
    question = event.message.text

    # 使用 OpenAI API 生成智慧回答
    response = openai.Completion.create(
        engine="davinci",
        prompt=(f"Q: {question}\nA: "),
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    # 解析 OpenAI API 的回應，獲取生成的智慧回答
    smart_answer = response.choices[0].text.strip()
    reply_message = f"{smart_answer}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )


if __name__ == "__main__":
    app.run()
