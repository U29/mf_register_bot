import asyncio
from pyppeteer import launch
import os
from dotenv import load_dotenv

# 環境変数をロード
load_dotenv()

# 環境変数から情報を取得
MONEYFORWARD_URL = os.getenv("MONEYFORWARD_URL")
MONEYFORWARD_ACCOUNTS_URL = os.getenv("MONEYFORWARD_ACCOUNTS_URL")
MONEYFORWARD_EMAIL = os.getenv("MONEYFORWARD_EMAIL")
MONEYFORWARD_PASSWORD = os.getenv("MONEYFORWARD_PASSWORD")


async def moneyforward_login():
    # ブラウザ起動
    browser = await launch(headless=False)
    page = await browser.newPage()

    # 1. https://moneyforward.com にアクセス
    await page.goto(MONEYFORWARD_ACCOUNTS_URL)

    # # 2. className="header-nav-menu" をクリック
    # await page.waitForSelector(".header-nav-menu")
    # await page.click(".header-nav-menu")

    # # 3. href="/sign_in" の a タグをクリック
    # await page.waitForSelector('a[href="/sign_in"]')
    # await page.click('a[href="/sign_in"]')

    # 4. type="email" の input タグにメールアドレスを入力
    await page.waitForSelector('input[type="email"]')
    await page.type('input[type="email"]', MONEYFORWARD_EMAIL)

    # 5. id="submitto" の部分をクリック
    await page.click("#submitto")

    # 6. type="password" の input タグにパスワードを入力
    await page.waitForSelector('input[type="password"]')
    await page.type('input[type="password"]', MONEYFORWARD_PASSWORD)

    # 7. id="submitto" の部分をクリック
    await page.click("#submitto")

    # # 8. value="yuluthi@gmail.com" の input タグをクリック
    # await page.waitForSelector('input[value="yuluthi@gmail.com"]')
    # await page.click('input[value="yuluthi@gmail.com"]')

    # # 9. 口座ページにアクセス
    # await page.goto(MONEYFORWARD_ACCOUNTS_URL)

    # # 5. id="submitto" の部分をクリック
    # await page.click("#submitto")

    # 10. 「手入力で資産を追加」というテキストを含む要素をクリック
    # "手入力で資産を追加"のボタンをクリックする
    await page.waitForSelector('a[href="#modal_asset_new"]')  # href属性で指定
    # モーダルを開くためのJavaScriptを実行
    await page.evaluate(
        "document.querySelector('a[href=\"#modal_asset_new\"]').click()"
    )

    # 11. id=user_asset_det_asset_subclass_id の select タグで option の value="66" を選択
    await page.waitForSelector("#user_asset_det_asset_subclass_id")
    await page.select("#user_asset_det_asset_subclass_id", "66")

    # 12. id=user_asset_det_name の input タグに "USDT" を入力
    await page.waitForSelector("#user_asset_det_name", {"visible": True})
    # await page.type("#user_asset_det_name", "USDT")
    # JavaScriptで直接値を設定
    await page.evaluate('document.querySelector("#user_asset_det_name").value = "USDT"')

    # 13. id=user_asset_det_value の input タグに "1000" を入力
    await page.waitForSelector("#user_asset_det_value", {"visible": True})
    # JavaScriptで直接値を設定
    await page.evaluate(
        'document.querySelector("#user_asset_det_value").value = "1000"'
    )

    # 14. 「この内容で登録する」ボタンをクリック
    # await page.click('input[value="この内容で登録する"]')
    # JavaScriptで直接クリック
    await page.evaluate(
        "document.querySelector('input[value=\"この内容で登録する\"]').click()"
    )

    # ブラウザを閉じる
    await browser.close()


# メインの実行
asyncio.get_event_loop().run_until_complete(moneyforward_login())
