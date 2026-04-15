import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()


def log(msg):
    print(msg, flush=True)


def fazer_login(page, usuario, senha):
    log("🔐 Abrindo Fretebras...")
    page.goto("https://novacentral.fretebras.com.br/", wait_until="load", timeout=60000)

    page.fill('input[name="username"]', usuario)
    page.fill('input[name="password"]', senha)
    page.click('button[type="submit"]')

    page.wait_for_timeout(8000)
    log("✅ Login concluído")


def abrir_meus_fretes(page):
    log("📂 Abrindo Meus Fretes...")

    # vai direto pela URL para evitar depender do menu lateral
    page.goto("https://novacentral.fretebras.com.br/meus-fretes", wait_until="load", timeout=60000)
    page.wait_for_timeout(6000)

    log("✅ Tela Meus Fretes aberta")
    log(f"URL atual: {page.url}")


def selecionar_todos(page):
    log("☑️ Selecionando todos...")

    page.wait_for_timeout(4000)

    # 1) tenta checkbox nativo
    try:
        checks = page.locator('input[type="checkbox"]')
        total = checks.count()

        for i in range(total):
            try:
                el = checks.nth(i)
                if el.is_visible():
                    el.click(force=True)
                    log(f"✅ Checkbox selecionado via input[type='checkbox'] índice {i}")
                    return
            except Exception:
                continue
    except Exception:
        pass

    # 2) tenta checkbox por role
    try:
        checks = page.locator('[role="checkbox"]')
        total = checks.count()

        for i in range(total):
            try:
                el = checks.nth(i)
                if el.is_visible():
                    el.click(force=True)
                    log(f"✅ Checkbox selecionado via role=checkbox índice {i}")
                    return
            except Exception:
                continue
    except Exception:
        pass

    # 3) tenta clicar perto do canto esquerdo da listagem
    # baseado no layout que você já mostrou antes
    try:
        page.mouse.click(50, 105)
        page.wait_for_timeout(1500)
        log("✅ Checkbox selecionado por coordenada")
        return
    except Exception:
        pass

    raise RuntimeError("❌ Nenhum checkbox encontrado")


def baixar_listagem_ativos(page, pasta_downloads, timestamp):
    log("⬇️ Iniciando download...")

    with page.expect_download(timeout=30000) as download_info:
        page.get_by_text("Download da listagem", exact=False).click()

    download = download_info.value
    nome = download.suggested_filename
    caminho = pasta_downloads / f"{timestamp}_{nome}"

    download.save_as(str(caminho))

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
                "status": "ok",
                "houve_reativacao": False,
            }

        except Exception as e:
            log(f"❌ Erro: {e}")
            raise

        finally:
            browser.close()