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
        headless=True,
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
    await page.setViewport({"width": 1200, "height": 800})
    print("Viewport set")
    # 1. https://moneyforward.com にアクセス
    await page.goto(MONEYFORWARD_ACCOUNTS_URL)
    print("Accessed to MoneyForward")

    # 4. type="email" の input タグにメールアドレスを入力
    await page.waitForSelector('input[type="email"]')
    await page.type('input[type="email"]', MONEYFORWARD_EMAIL)
    print("Typed email")

    # 5. id="submitto" の部分をクリック
    await page.click("#submitto")
    print("Clicked submitto")

    # 6. type="password" の input タグにパスワードを入力
    await page.waitForSelector('input[type="password"]')
    await page.type('input[type="password"]', MONEYFORWARD_PASSWORD)
    print("Typed password")

    # 7. id="submitto" の部分をクリック
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

    # .accounts-formクラスのsectionタグ以下の最初のaタグをクリック
    await page.waitForSelector(".accounts-form")
    await page.evaluate('document.querySelector(".accounts-form a").click()')

    # 11. id=user_asset_det_asset_subclass_id の select タグ以下のlabelが預金・現金・暗号資産のoptgroupタグ内で optionタグ の value="66" を選択
    await page.waitForSelector("#user_asset_det_asset_subclass_id", {"visible": True})
    await page.select("#user_asset_det_asset_subclass_id", "66")
    # 12. id=user_asset_det_name の input タグに "USDT" を入力
    await page.waitForSelector("#user_asset_det_name", {"visible": True})
    # await page.type("#user_asset_det_name", "USDT")
    # JavaScriptで直接値を設定
    await page.evaluate('document.querySelector("#user_asset_det_name").value = "USDT"')

    # 13. id=user_asset_det_value の input タグに diff を入力
    await page.waitForSelector("#user_asset_det_value", {"visible": True})
    # JavaScriptで直接値を設定
    await page.evaluate(
        f'document.querySelector("#user_asset_det_value").value = "{diff}"'
    )
    # 14. 「この内容で登録する」ボタンをクリック
    # await page.click('input[value="この内容で登録する"]')
    # JavaScriptで直接クリック
    await page.evaluate(
        "document.querySelector('input[value=\"この内容で登録する\"]').click()"
    )

    await asyncio.sleep(5)

    # class="alert alert-success" のテキストが"資産を追加しました"であることを確認
    await page.waitForSelector(".alert.alert-success")
    success_message = await page.evaluate(
        'document.querySelector(".alert.alert-success").textContent'
    )
    print(success_message)
    assert "資産を追加しました" in success_message

    # ブラウザを閉じる
    await browser.close()


# メインの実行
asyncio.get_event_loop().run_until_complete(moneyforward_login())
