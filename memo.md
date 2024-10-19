以下を実行する、puppeteer を使ったスクリプトを Python で作成してください。
URL やメールアドレス、パスワード、id, className などは環境変数に設定してください。

1. https://moneyforward.com　にアクセスする
2. className = header-nav-menu の部分をクリックする
3. href="/sign_in" の a タグをクリックする
4. type="email"の input タグにメールアドレスを入力する
5. id = "submitto" の部分をクリックする
6. type が password の部分にパスワードを入力する
7. id = "submitto" の部分をクリックする
8. 口座ページを開く(https://moneyforward.com/accounts/show_manual/UelgLvqc8MmyucztXVB_fl2hjtZPkY6uAP6o-l9kjhI)
9. 手入力で資産を追加というテキストを含む要素をクリックする
10. id=user_asset_det_asset_subclass_id の select タグの option タグの value が"66"のものをクリックする
11. id=user_asset_det_name の input タグに"USDT"を入力する
12. id=user_asset_det_value の input タグに"1000"を入力する
13. value がこの内容で登録するの input タグをクリックする
