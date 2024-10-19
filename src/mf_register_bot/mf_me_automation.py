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

    # 4. type="email" の input タグにメールアドレスを入力
    await page.waitForSelector('input[type="email"]')
    await page.type('input[type="email"]', MONEYFORWARD_EMAIL)

    # 5. id="submitto" の部分をクリック
    await page.click("#submitto")

    # 6. type="password" の input タグにパスワードを入力
    await page.waitForSelector('input[type="password"]')
    await page.type('input[type="password"]', MONEYFORWARD_PASSWORD)

    # 7. id="submitto" の部分をクリック
    await page.waitForSelector("#submitto")
    await page.click("#submitto")

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
