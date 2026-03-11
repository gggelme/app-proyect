import flet as ft
from ui import AcademiaApp

def main(page: ft.Page):
    app = AcademiaApp(page)
    app.run()

if __name__ == "__main__":
    ft.app(target=main)