import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright


def log(msg):
    print(msg, flush=True)


def fazer_login(page, usuario, senha):
    log("🔐 Abrindo Fretebras...")
    page.goto("https://novacentral.fretebras.com.br/")

    page.fill('input[name="username"]', usuario)
    page.fill('input[name="password"]', senha)
    page.click('button[type="submit"]')

    page.wait_for_timeout(5000)
    log("✅ Login concluído")


def abrir_meus_fretes(page):
    log("📂 Abrindo Meus Fretes...")

    try:
        page.click('text="Meus Fretes"', timeout=5000)
    except:
        page.click('aside button', timeout=5000)
        page.click('text="Meus Fretes"', timeout=5000)

    page.wait_for_timeout(4000)
    log("✅ Tela Meus Fretes aberta")


def selecionar_todos(page):
    log("☑️ Selecionando todos...")

    checkboxes = page.locator("input[type='checkbox']")
    if checkboxes.count() > 0:
        checkboxes.nth(0).click()
        log("✅ Checkbox selecionado")
    else:
        raise RuntimeError("❌ Nenhum checkbox encontrado")


def baixar_listagem_ativos(page, pasta_downloads, timestamp):
    log("⬇️ Iniciando download...")

    with page.expect_download() as download_info:
        page.click('text="Download da listagem"')

    download = download_info.value
    nome = download.suggested_filename

    caminho = pasta_downloads / f"{timestamp}_{nome}"
    download.save_as(caminho)

    log(f"✅ Arquivo salvo em: {caminho}")
    return caminho


def baixar_listagem():
    usuario = os.getenv("FRETEBRAS_USER", "").strip()
    senha = os.getenv("FRETEBRAS_PASS", "").strip()

    if not usuario or not senha:
        raise ValueError("Defina FRETEBRAS_USER e FRETEBRAS_PASS")

    base_dir = Path(__file__).resolve().parent.parent
    pasta_downloads = base_dir / "downloads"
    pasta_downloads.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        try:
            fazer_login(page, usuario, senha)
            abrir_meus_fretes(page)

            selecionar_todos(page)

            caminho = baixar_listagem_ativos(page, pasta_downloads, timestamp)

            return {
                "arquivo": str(caminho),
                "status": "ok"
            }

        except Exception as e:
            log(f"❌ Erro: {e}")
            raise

        finally:
            browser.close()