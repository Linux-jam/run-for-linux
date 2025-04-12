import tkinter as tk
import subprocess
import sys
import os
import shlex
from tkinter import filedialog
import getpass  # ユーザー名を取得するため
import threading # スレッド処理のため

def create_launcher_window():
    """
    LinuxでWin+Rみたいな起動画面を作る関数。
    """
    try:
        root = tk.Tk()
        root.title("ファイル名を指定して実行")
        root.geometry("350x130")
        root.resizable(False, False)

        # メッセージラベル
        message_label = tk.Label(
            root,
            text="実行するプログラム名、または開くフォルダーやドキュメント名、インターネット リソース名を入力してください。",
            font=("Arial", 10),
            wraplength=300,
            justify=tk.LEFT,
        )
        message_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))

        # 入力フレーム
        input_frame = tk.Frame(root)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 5))

        # ラベル
        label = tk.Label(input_frame, text="名前(O):", font=("Arial", 10))
        label.pack(side=tk.LEFT, padx=(0, 5), pady=(0, 0))

        # エントリー
        entry = tk.Entry(input_frame, font=("Arial", 12))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=(0, 0))
        entry.focus_set()

        def run_command(admin=False):
            """
            エントリーに入力されたコマンドを実行する関数。
            """
            command = entry.get()
            if not command:
                root.destroy()
                return
            try:
                args = shlex.split(command)
                if admin:
                    # pkexecで管理者権限で実行
                    cmd = ["pkexec"] + args
                    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                else:
                    result = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if result.stdout:
                    print("標準出力:")
                    print(result.stdout)
                if result.stderr:
                    print("標準エラー出力:")
                    print(result.stderr)

                root.destroy()
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror("エラー", f"'{command}' の実行に失敗しました。\nエラー: {e}")
                print(f"コマンド実行エラー: {e}")
                print(f"エラー出力:\n{e.stderr}")
            except FileNotFoundError:
                tk.messagebox.showerror("エラー", f"ファイルまたはコマンドが見つかりません: {command}")
            except Exception as e:
                tk.messagebox.showerror("エラー", f"予期せぬエラーが発生しました:\n{e}")

        def on_ok_button_click(event=None): # event引数を追加
            """
            OKボタンがクリックされたときの処理。
            """
            if event and event.num == 3:  # 右クリックの場合
                # 管理者として実行するか確認
                answer = tk.messagebox.askyesno("管理者権限で実行", "管理者権限で実行しますか？(β)")
                if answer:
                    run_command(admin=True)  # 管理者権限で実行
            else:
                run_command(admin=False) # 通常実行

        def on_cancel_button_click():
            root.destroy()

        def on_browse_button_click():
            """
            「参照」ボタンがクリックされたときにファイル選択ダイアログを開く関数
            """
            file_path = filedialog.askopenfilename(title="ファイルを選択", initialdir=".")
            if file_path:
                entry.delete(0, tk.END)
                entry.insert(0, file_path)

        # ボタン用のフレームを作成
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

        # OKボタン
        ok_button = tk.Button(button_frame, text="OK", command=on_ok_button_click, width=8)
        ok_button.pack(side=tk.LEFT, padx=(0, 5))
        ok_button.bind("<Button-3>", on_ok_button_click)  # 右クリックもバインド

        # キャンセルボタン
        cancel_button = tk.Button(
            button_frame, text="キャンセル", command=on_cancel_button_click, width=8
        )
        cancel_button.pack(side=tk.LEFT, padx=(0, 5))

        # 参照ボタン
        browse_button = tk.Button(
            button_frame, text="参照(B)...", command=on_browse_button_click, width=8
        )
        browse_button.pack(side=tk.LEFT, padx=(0, 0))

        # EnterキーでOKボタンを押せるようにする
        root.bind("<Return>", on_ok_button_click)
        # Escキーでキャンセルボタンを押せるようにする
        root.bind("<Escape>", on_cancel_button_click)

        return root

    except Exception as e:
        print(f"起動画面作成中にエラーが発生しました: {e}")
        sys.exit(1)
        return None


def run_app():
    """
    アプリケーションを実行する関数。
    """
    root = create_launcher_window()
    if root is None:
        print("起動画面の作成に失敗しました。終了します。")
        sys.exit(1)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("ユーザーによって中断されました。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        sys.exit(1)
    finally:
        print("アプリケーションを終了します。")


if __name__ == "__main__":
    run_app()
