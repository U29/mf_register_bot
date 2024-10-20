import asyncio
from pyppeteer import launch
import os
from dotenv import load_dotenv
from pybit.unified_trading import HTTP
import requests

# 環境変数をロード
load_dotenv()

# 環境変数から情報を取得
MONEYFORWARD_URL = os.getenv("MONEYFORWARD_URL")
MONEYFORWARD_ACCOUNTS_URL = os.getenv("MONEYFORWARD_ACCOUNTS_URL")
MONEYFORWARD_EMAIL = os.getenv("MONEYFORWARD_EMAIL")
MONEYFORWARD_PASSWORD = os.getenv("MONEYFORWARD_PASSWORD")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
HEADLESS_MODE = os.getenv("HEADLESS_MODE") == "TRUE"


async def moneyforward_login():
    # Bybit APIセッションを初期化
    session = HTTP(
        testnet=False,
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
        recv_window=10000,
    )

    # 総資産を取得
    total_balance = session.get_wallet_balance(
        accountType="UNIFIED",
        coin="USDT",
    )
    total_balance = float(total_balance["result"]["list"][0]["totalEquity"])
    print(total_balance)

    # APIで為替レートを取得
    url = "https://api.excelapi.org/currency/rate?pair=usd-jpy"
    response = requests.get(url)
    assert response.status_code == 200
    usd_rate = float(response.json())

    # 総資産を円換算
    total_balance_jpy = total_balance * usd_rate

    # ブラウザ起動
    browser = await launch(
        headless=HEADLESS_MODE,
        args=[
            "--no-sandbox",
            "--disable-gpu",
        ],
    )
    print("Browser launched")
    page = await browser.newPage()
    print("Page created")

    await page.setUserAgent(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36"
    )
    print("User agent set")
    await page.setViewport({"width": 1200, "height": 1080})
    print("Viewport set")
    # https://moneyforward.com にアクセス
    await page.goto(MONEYFORWARD_ACCOUNTS_URL)
    print("Accessed to MoneyForward")

    # type="email" の input タグにメールアドレスを入力
    await page.waitForSelector('input[type="email"]')
    await page.type('input[type="email"]', MONEYFORWARD_EMAIL)
    print("Typed email")

    # id="submitto" の部分をクリック
    await page.click("#submitto")
    print("Clicked submitto")

    # type="password" の input タグにパスワードを入力
    await page.waitForSelector('input[type="password"]')
    await page.type('input[type="password"]', MONEYFORWARD_PASSWORD)
    print("Typed password")

    # id="submitto" の部分をクリック
    await page.waitForSelector("#submitto")
    await page.click("#submitto")
    print("Clicked submitto")

    await asyncio.sleep(5)

    # 暗号資産総額の取得
    # heading-smallクラスの最初の要素のテキストを取得
    total_assets = await page.evaluate(
        'document.querySelector(".heading-small").textContent'
    )
    print(total_assets)
    total_assets = total_assets.split("：")[1]
    total_assets = total_assets.replace("円", "").replace(",", "")
    print(total_assets)

    # 総資産の差分を計算
    diff = int(total_balance_jpy - float(total_assets))
    print(diff)

    if diff == 0:
        print("資産に変動はありません")
        return

    # class="cf-new-btn btn modal-switch btn-warning" のbuttonタグをクリック
    await page.waitForSelector(".cf-new-btn.btn.modal-switch.btn-warning")
    await page.evaluate(
        'document.querySelector(".cf-new-btn.btn.modal-switch.btn-warning").click()'
    )
    await asyncio.sleep(1)

    if diff < 0:
        # 支出ボタンをクリック
        # class=minus-payment かつ id=user_asset_act_payment_2 のinputタグをクリック
        await page.waitForSelector(".minus-payment")
        await page.evaluate('document.querySelector(".minus-payment").click()')

    else:
        # 収入ボタンをクリック
        # class=plus-payment かつ id=user_asset_act_payment_2 のinputタグをクリック

        await page.waitForSelector(".plus-payment")
        await page.evaluate('document.querySelector(".plus-payment").click()')
        await asyncio.sleep(1)

    # id=appendedPrependedInput のinputタグに diff を入力
    await page.waitForSelector("#appendedPrependedInput")
    await page.evaluate(
        f'document.querySelector("#appendedPrependedInput").value = "{abs(diff)}"'
    )
    await asyncio.sleep(1)

    # id=js-large-category-selected のaタグをクリック
    await page.waitForSelector("#js-large-category-selected")
    await page.evaluate('document.querySelector("#js-large-category-selected").click()')

    await asyncio.sleep(1)

    if diff < 0:
        # id=19517320のaタグをクリック(その他)
        await page.waitForSelector('[id="19517320"]')
        await page.evaluate("document.querySelector('[id=\"19517320\"]').click()")
        print("19517320 click end")

        # id=js-middle-category-selected のaタグをクリック
        await page.waitForSelector("#js-middle-category-selected")
        await page.evaluate(
            'document.querySelector("#js-middle-category-selected").click()'
        )

        # id=19517320 のaタグをクリック(暗号資産取引)
        await page.waitForSelector('[id="19517320"]')
        await page.evaluate("document.querySelector('[id=\"19517320\"]').click()")

    else:
        # id=1のaタグをクリック(収入)
        await page.waitForSelector('[id="1"]')
        await page.evaluate("document.querySelector('[id=\"1\"]').click()")

        await asyncio.sleep(1)

        # id=js-middle-category-selected のaタグをクリック
        await page.waitForSelector("#js-middle-category-selected")
        await page.evaluate(
            'document.querySelector("#js-middle-category-selected").click()'
        )

        # id=19517314 のaタグをクリック(暗号資産取引)
        await page.waitForSelector('[id="19517314"]')
        await page.evaluate("document.querySelector('[id=\"19517314\"]').click()")

        await asyncio.sleep(1)

    # id=submit-button のinputタグをクリック
    await page.waitForSelector("#submit-button")
    await page.evaluate('document.querySelector("#submit-button").click()')

    print("資産を追加しました")

    # ブラウザを閉じる
    await browser.close()


# メインの実行
asyncio.get_event_loop().run_until_complete(moneyforward_login())
