"""Minimal Toga UI — set token and note to run core on device via Termux/Python."""

def run():
    try:
        import toga
        from toga.style import Pack
        from toga.style.pack import COLUMN, ROW
    except ImportError:
        print("toga not installed — use Termux path: python main.py")
        return

    def on_save(widget):
        token = input_token.value.strip() if input_token.value else ""
        status.value = "saved locally — run core with python main.py in Termux for full selfbot"
        # Full gateway on Android requires the Python stack (Termux) or a companion service.

    def build(app):
        global input_token, status
        input_token = toga.PasswordInput(placeholder="Discord user token")
        status = toga.Label("OreoSB mobile shell")
        btn = toga.Button("Save token hint", on_press=on_save)
        box = toga.Box(
            children=[
                toga.Label("OreoSB"),
                input_token,
                btn,
                status,
                toga.Label("Full bot: Termux + pip install -r requirements.txt"),
            ],
            style=Pack(direction=COLUMN, margin=12, gap=8),
        )
        return toga.MainWindow(title="OreoSB", content=box)

    app = toga.App("OreoSB", "com.oreosb.app", startup=build)
    app.main_loop()
