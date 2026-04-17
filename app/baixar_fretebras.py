import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()


def log(msg: str):
    print(msg, flush=True)


def screenshot_seguro(page, caminho: Path):
    try:
        page.screenshot(path=str(caminho), full_page=True)
    except Exception:
        pass


def fazer_login(page, usuario, senha):
    log("🔐 Fazendo login...")
    page.goto("https://novacentral.fretebras.com.br", timeout=60000)

    page.fill('input[name="username"]', usuario)
    page.fill('input[name="password"]', senha)
    page.click('button[type="submit"]')

    page.wait_for_timeout(8000)
    log("✅ Login concluído")


def abrir_meus_fretes(page):
    log("📂 Abrindo Meus Fretes...")
    page.goto("https://novacentral.fretebras.com.br/meus-fretes", timeout=60000)
    page.wait_for_timeout(5000)


def abrir_aba_desativados(page):
    log("♻️ Indo para Desativados...")
    page.get_by_text("Desativados", exact=False).first.click()
    page.wait_for_timeout(4000)


def selecionar_primeiro_desativado_automatico_com_hover(page):
    log("🎯 Buscando desativado automático...")

    textos = page.locator("text=/Frete desativado automaticamente/i")
    total = textos.count()

    log(f"Encontrados: {total}")

    if total == 0:
        return 0

    alvo = textos.first
    alvo.scroll_into_view_if_needed()

    box = alvo.bounding_box()
    if not box:
        return 0

    x = box["x"] - 200
    y = box["y"] + (box["height"] / 2)

    page.mouse.move(x, y)
    page.wait_for_timeout(500)
    page.mouse.click(x, y)

    log("✅ Clique no checkbox do automático")
    return 1


def clicar_ativar(page):
    log("🟢 Clicando em Ativar...")
    page.get_by_text("Ativar", exact=False).first.click()
    page.wait_for_timeout(3000)


def tratar_popup(page):
    log("🔵 Confirmando popup...")
    page.get_by_text("Ativar", exact=False).last.click()
    page.wait_for_timeout(3000)


def marcar_motivo(page):
    log("📝 Marcando motivo...")
    page.get_by_text("Motorista desistiu da negociação", exact=False).click()
    page.wait_for_timeout(1000)


def clicar_confirmar(page):
    log("✅ Confirmando...")
    page.get_by_text("Confirmar", exact=False).click()
    page.wait_for_timeout(3000)


def voltar_para_ativos(page):
    log("↩️ Voltando para ativos...")
    page.get_by_text("Ativos", exact=False).first.click()
    page.wait_for_timeout(4000)


def selecionar_todos(page):
    log("☑️ Selecionando todos...")
    page.locator('input[type="checkbox"]').first.click()
    page.wait_for_timeout(1000)


def baixar_arquivo(page, pasta, timestamp):
    log("⬇️ Baixando...")

    with page.expect_download(timeout=60000) as download_info:
        page.get_by_text("Download da listagem").click()

    download = download_info.value
    caminho = pasta / f"{timestamp}_{download.suggested_filename}"
    download.save_as(str(caminho))

    log(f"✅ Arquivo salvo em: {caminho}")
    return caminho


def baixar_listagem():
    usuario = os.getenv("FRETEBRAS_USER")
    senha = os.getenv("FRETEBRAS_PASS")

    if not usuario or not senha:
        raise ValueError("Defina FRETEBRAS_USER e FRETEBRAS_PASS")

    base_dir = Path(__file__).resolve().parent.parent
    pasta = base_dir / "downloads"
    pasta.mkdir(exist_ok=True)

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
            abrir_aba_desativados(page)

            qtd = selecionar_primeiro_desativado_automatico_com_hover(page)

            if qtd > 0:
                clicar_ativar(page)
                tratar_popup(page)
                marcar_motivo(page)
                clicar_confirmar(page)
                log("✅ Reativação concluída")
            else:
                log("ℹ️ Nenhum automático encontrado")

            voltar_para_ativos(page)
            selecionar_todos(page)

            caminho = baixar_arquivo(page, pasta, timestamp)

            return {
                "arquivo": str(caminho),
                "reativado": qtd > 0
            }

        except Exception as e:
            log(f"❌ ERRO: {e}")
            raise

        finally:
            browser.close()