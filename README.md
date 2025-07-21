# GUIタスク管理アプリケーション 🎨

## 概要

これは、美しく直感的なグラフィカル・ユーザー・インターフェース（GUI）を持つデスクトップ・タスク管理アプリケーションです。日々のタスク管理を、より快適で視覚的に行うことを目的としています。

---

## ✨ スクリーンショット

*ここにアプリケーションのスクリーンショットを挿入してください。*

**(例)**
| タスク一覧画面 | タスク追加ダイアログ |
| :---: | :---: |
| ![タスク一覧画面のスクリーンショット](https://via.placeholder.com/400x300.png?text=Main+Window) | ![タスク追加画面のスクリーンショット](https://via.placeholder.com/400x300.png?text=Add+Task+Dialog) |

---

## 主な機能

-   ✅ **タスクの追加**: 分かりやすいフォームから新しいタスクを登録します。
-   📋 **タスクの一覧表示**: 見やすいリストでタスクをリアルタイムに確認できます。
-   ✏️ **タスクの更新**: 既存のタスクをダブルクリックなどで簡単に編集します。
-   🗑️ **タスクの削除**: 不要になったタスクを選択して削除します。
-   🏁 **タスクの完了**: チェックボックスをクリックするだけで、タスクのステータスを切り替えられます。

---

## 開発・実行環境

-   **言語**: Python 3.11
-   **環境管理**: Conda
-   **GUIフレームワーク**: **CustomTkinter** (または PySide6, Flet など、あなたが選んだフレームワーク名に書き換えてください)

---

## 🛠️ インストールとセットアップ

このアプリケーションを実行するには、以下の手順に従ってください。

1.  **リポジトリのクローン**
    ```bash
    git clone [https://github.com/](https://github.com/)[Kota-James]/[my-task-app].git
    cd [my-task-app]
    ```

2.  **Conda仮想環境の作成と有効化**
    プロジェクトルートに`environment.yml`を用意しました。これを使い、GUIフレームワークを含んだ環境を一度に構築します。

    **`environment.yml` ファイル例:**
    ```yaml
    name: my-task-app-env
    channels:
      - defaults
    dependencies:
      - python=3.11
      - pip
      - pip:
        - customtkinter==5.2.2
        # - pyside6
        # - flet
    ```

    **コマンド:**
    ```bash
    # Conda仮想環境を作成
    conda env create -f environment.yml

    # 作成した仮想環境を有効化
    conda activate my-task-app-env
    ```

---

## 🚀 使い方

セットアップが完了したら、以下のコマンドでアプリケーションのGUIウィンドウを起動します。

```bash
python src/main.py
```

---

## ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。