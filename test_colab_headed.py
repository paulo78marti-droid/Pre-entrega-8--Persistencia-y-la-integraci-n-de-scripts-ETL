"""
Test Headed con Playwright para Google Colab
Curso: Data Science II - Coderhouse
Proyecto: Pre-entrega 8 — Persistencia y la integración de scripts ETL

Este script abre Google Chrome en modo visible (headed: True) y carga
el cuaderno Pre-entrega_8_ETL.ipynb directamente en Google Colab
desde el repositorio público de GitHub.
"""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

COLAB_GITHUB_URL = (
    "https://colab.research.google.com/github/paulo78marti-droid/"
    "Pre-entrega-8--Persistencia-y-la-integraci-n-de-scripts-ETL/blob/master/Pre-entrega_8_ETL.ipynb"
)


def run_colab_headed_test():
    print("=" * 65)
    print(" INICIANDO TEST HEADED EN GOOGLE COLAB CON PLAYWRIGHT")
    print("=" * 65)
    print(f"URL a cargar: {COLAB_GITHUB_URL}\n")

    with sync_playwright() as p:
        print("[1/4] Abriendo navegador Chrome en modo visible (headed)...")
        # headless=False para que la ventana sea visible en pantalla
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            slow_mo=300
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        print("[2/4] Navegando al notebook del proyecto en Google Colab...")
        page.goto(COLAB_GITHUB_URL, wait_until="networkidle", timeout=60000)

        # Esperar unos segundos para que Colab termine de renderizar las celdas
        time.sleep(5)

        title = page.title()
        print(f"[3/4] Título de la página cargada: '{title}'")

        # Tomar captura de pantalla como evidencia del test
        screenshot_path = Path("colab_notebook_render.png")
        page.screenshot(path=str(screenshot_path))
        print(f"[4/4] Captura de pantalla guardada en: {screenshot_path.resolve()}")

        print("\n" + "-" * 65)
        print(" NOTA TÉCNICA SOBRE GOOGLE COLAB:")
        print("  • El notebook se visualiza con todas sus celdas y código ETL.")
        print("  • Para ejecutar las celdas ('Conectar / Run'), Google solicita")
        print("    iniciar sesión con una cuenta de Google activa.")
        print("-" * 65)

        # Mantener visible por 6 segundos antes de cerrar
        print("Manteniendo ventana abierta por 6 segundos...")
        time.sleep(6)

        browser.close()
        print("\n ¡Test headed completado exitosamente!\n")


if __name__ == "__main__":
    run_colab_headed_test()
