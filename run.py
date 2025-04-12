import tkinter as tk
import subprocess
import sys
import os
import shlex
from tkinter import filedialog
import getpass  # ユーザー名を取得するため
import threading # スレッド処理のため
import json  # 言語ファイルの読み込み用

# 言語ファイルの読み込み関数
def load_language(lang_code):
    lang_file = f"lang/{lang_code}.json"
    if not os.path.exists(lang_file):
        print(f"言語ファイルが見つかりません: {lang_file}")
        sys.exit(1)

    with open(lang_file, "r", encoding="utf-8") as file:
        return json.load(file)

def create_launcher_window(lang):
    """
    LinuxでWin+Rみたいな起動画面を作る関数。
    """
    try:
        root = tk.Tk()
        root.title(lang["window_title"])
        root.geometry("350x130")
        root.resizable(False, False)

        # メッセージラベル
        message_label = tk.Label(
            root,
            text=lang["message_label"],
            font=("Arial", 10),
            wraplength=300,
            justify=tk.LEFT,
        )
        message_label.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 0))

        # 入力フレーム
        input_frame = tk.Frame(root)
        input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(0, 5))

        # ラベル
        label = tk.Label(input_frame, text=lang["name_label"], font=("Arial", 10))
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
                    print(lang["stdout_message"])
                    print(result.stdout)
                if result.stderr:
                    print(lang["stderr_message"])
                    print(result.stderr)

                root.destroy()
            except subprocess.CalledProcessError as e:
                tk.messagebox.showerror(lang["error_title"], lang["command_error_message"].format(command=command, error=e))
                print(f"{lang['command_error_label']}: {e}")
                print(f"{lang['stderr_label']}:\n{e.stderr}")
            except FileNotFoundError:
                tk.messagebox.showerror(lang["error_title"], lang["file_not_found_message"].format(command=command))
            except Exception as e:
                tk.messagebox.showerror(lang["error_title"], lang["unexpected_error_message"].format(error=e))

        def on_ok_button_click(event=None): # event引数を追加
            """
            OKボタンがクリックされたときの処理。
            """
            if event and event.num == 3:  # 右クリックの場合
                # 管理者として実行するか確認
                answer = tk.messagebox.askyesno(lang["admin_prompt_title"], lang["admin_prompt_message"])
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
            file_path = filedialog.askopenfilename(title=lang["file_dialog_title"], initialdir=".")
            if file_path:
                entry.delete(0, tk.END)
                entry.insert(0, file_path)

        # ボタン用のフレームを作成
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

        # OKボタン
        ok_button = tk.Button(button_frame, text=lang["ok_button"], command=on_ok_button_click, width=8)
        ok_button.pack(side=tk.LEFT, padx=(0, 5))
        ok_button.bind("<Button-3>", on_ok_button_click)  # 右クリックもバインド

        # キャンセルボタン
        cancel_button = tk.Button(
            button_frame, text=lang["cancel_button"], command=on_cancel_button_click, width=8
        )
        cancel_button.pack(side=tk.LEFT, padx=(0, 5))

        # 参照ボタン
        browse_button = tk.Button(
            button_frame, text=lang["browse_button"], command=on_browse_button_click, width=8
        )
        browse_button.pack(side=tk.LEFT, padx=(0, 0))

        # EnterキーでOKボタンを押せるようにする
        root.bind("<Return>", on_ok_button_click)
        # Escキーでキャンセルボタンを押せるようにする
        root.bind("<Escape>", on_cancel_button_click)

        return root

    except Exception as e:
        print(lang["create_window_error_message"].format(error=e))
        sys.exit(1)
        return None


def run_app():
    """
    アプリケーションを実行する関数。
    """
    # 言語を選択
    lang_code = "ja"  # 必要に応じて "en" に変更可能
    lang = load_language(lang_code)

    root = create_launcher_window(lang)
    if root is None:
        print(lang["create_window_fail_message"])
        sys.exit(1)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print(lang["user_interrupt_message"])
    except Exception as e:
        print(lang["unexpected_error_message"].format(error=e))
        sys.exit(1)
    finally:
        print(lang["app_exit_message"])


if __name__ == "__main__":
    run_app()
