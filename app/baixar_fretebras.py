import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

load_dotenv()


def log(msg: str):
    print(msg, flush=True)


def screenshot_seguro(page, caminho: Path):
    try:
        page.screenshot(path=str(caminho), full_page=True)
        log(f"📸 Screenshot salva em {caminho}")
    except Exception as e:
        log(f"⚠️ Não foi possível salvar screenshot: {e}")


def fazer_login(page, usuario: str, senha: str, base_dir: Path):
    log("🔐 Abrindo Fretebras...")
    page.goto("https://novacentral.fretebras.com.br", wait_until="load", timeout=60000)

    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PlaywrightTimeoutError:
        pass

    page.fill('input[name="username"]', usuario)
    page.fill('input[name="password"]', senha)
    page.click('button[type="submit"]')

    page.wait_for_timeout(8000)
    screenshot_seguro(page, base_dir / "diag_pos_login.png")
    log("✅ Login concluído")
    log(f"URL atual: {page.url}")


def abrir_meus_fretes(page, base_dir: Path):
    log("📂 Abrindo Meus Fretes...")
    page.goto("https://novacentral.fretebras.com.br/meus-fretes", wait_until="load", timeout=60000)
    page.wait_for_timeout(6000)
    screenshot_seguro(page, base_dir / "diag_meus_fretes.png")
    log("✅ Tela Meus Fretes aberta")
    log(f"URL atual: {page.url}")


def abrir_aba_desativados(page, base_dir: Path):
    log("♻️ Indo para aba Desativados...")
    page.wait_for_timeout(3000)

    for i, tentativa in enumerate([
        lambda: page.get_by_text("Desativados", exact=False).first.click(force=True),
        lambda: page.locator("text=Desativados").first.click(force=True),
    ], start=1):
        try:
            tentativa()
            page.wait_for_timeout(5000)
            screenshot_seguro(page, base_dir / "diag_desativados_aberta.png")
            log(f"✅ Clique em Desativados na tentativa {i}")
            log("✅ Aba Desativados aberta")
            return
        except Exception:
            continue

    raise RuntimeError("Não foi possível abrir a aba Desativados.")


def selecionar_primeiro_desativado_automatico_com_hover(page, base_dir: Path) -> int:
    log("🎯 Procurando 1 frete desativado automaticamente para hover + seleção...")
    page.wait_for_timeout(3000)

    textos = page.locator("text=/Frete desativado automaticamente/i")
    total = textos.count()
    log(f"📦 Total de fretes desativados automaticamente encontrados: {total}")

    if total == 0:
        screenshot_seguro(page, base_dir / "diag_sem_desativado_auto.png")
        return 0

    for i in range(total):
        try:
            alvo = textos.nth(i)

            # sobe para um bloco maior da linha/card
            container = alvo.locator("xpath=ancestor::div[1]")
            try:
                container.hover(force=True)
            except Exception:
                alvo.hover(force=True)

            page.wait_for_timeout(1500)
            screenshot_seguro(page, base_dir / f"diag_hover_desativado_{i}.png")

            # tenta achar checkbox após hover
            checks = page.locator('input[type="checkbox"]')
            total_checks = checks.count()

            for j in range(total_checks):
                try:
                    chk = checks.nth(j)
                    if chk.is_visible():
                        chk.click(force=True)
                        log(f"✅ Checkbox do desativado automático clicado após hover (texto {i}, checkbox {j})")
                        screenshot_seguro(page, base_dir / "diag_checkbox_desativado_marcado.png")
                        return 1
                except Exception:
                    continue

            # fallback role checkbox
            checks_role = page.locator('[role="checkbox"]')
            total_role = checks_role.count()

            for j in range(total_role):
                try:
                    chk = checks_role.nth(j)
                    if chk.is_visible():
                        chk.click(force=True)
                        log(f"✅ Role checkbox do desativado clicado após hover (texto {i}, checkbox {j})")
                        screenshot_seguro(page, base_dir / "diag_role_checkbox_desativado_marcado.png")
                        return 1
                except Exception:
                    continue

        except Exception:
            continue

    screenshot_seguro(page, base_dir / "diag_hover_sem_checkbox.png")
    return 0


def clicar_ativar_topo(page, base_dir: Path):
    log("🟢 Tentando clicar em Ativar...")

    for i, tentativa in enumerate([
        lambda: page.get_by_text("Ativar", exact=False).first.click(force=True),
        lambda: page.locator("button").filter(has_text="Ativar").first.click(force=True),
        lambda: page.locator("text=Ativar").first.click(force=True),
    ], start=1):
        try:
            tentativa()
            page.wait_for_timeout(2500)
            screenshot_seguro(page, base_dir / "diag_botao_ativar_topo.png")
            log(f"✅ Clique em Ativar na tentativa {i}")
            return
        except Exception:
            continue

    raise RuntimeError("Não foi possível clicar em Ativar.")


def tratar_popup_ativar(page, base_dir: Path):
    log("🔵 Tratando popup 'Ativar fretes?'...")
    page.wait_for_timeout(2500)
    screenshot_seguro(page, base_dir / "diag_popup_ativar.png")

    for i, tentativa in enumerate([
        lambda: page.locator("div[role='dialog'] button").filter(has_text="Ativar").last.click(force=True),
        lambda: page.get_by_text("Ativar", exact=False).last.click(force=True),
    ], start=1):
        try:
            tentativa()
            page.wait_for_timeout(3000)
            screenshot_seguro(page, base_dir / "diag_popup_ativar_confirmado.png")
            log(f"✅ Clique no Ativar do popup na tentativa {i}")
            return
        except Exception:
            continue

    raise RuntimeError("Não foi possível clicar no Ativar do popup.")


def marcar_motivo_motorista_desistiu(page, base_dir: Path):
    log("📝 Marcando motivo 'Motorista desistiu da negociação'...")
    page.wait_for_timeout(2500)
    screenshot_seguro(page, base_dir / "diag_tela_motivo.png")

    for i, tentativa in enumerate([
        lambda: page.get_by_text("Motorista desistiu da negociação", exact=False).first.click(force=True),
        lambda: page.locator("text=Motorista desistiu da negociação").first.click(force=True),
    ], start=1):
        try:
            tentativa()
            page.wait_for_timeout(1500)
            screenshot_seguro(page, base_dir / "diag_motivo_marcado.png")
            log(f"✅ Motivo marcado na tentativa {i}")
            return
        except Exception:
            continue

    raise RuntimeError("Não foi possível marcar o motivo.")


def clicar_confirmar(page, base_dir: Path):
    log("✅ Clicando em Confirmar...")
    page.wait_for_timeout(1200)

    for i, tentativa in enumerate([
        lambda: page.get_by_text("Confirmar", exact=False).first.click(force=True),
        lambda: page.locator("button").filter(has_text="Confirmar").first.click(force=True),
        lambda: page.locator("text=Confirmar").first.click(force=True),
    ], start=1):
        try:
            tentativa()
            page.wait_for_timeout(4000)
            screenshot_seguro(page, base_dir / "diag_confirmado.png")
            log(f"✅ Clique em Confirmar na tentativa {i}")
            return
        except Exception:
            continue

    raise RuntimeError("Não foi possível clicar em Confirmar.")


def voltar_para_ativos(page, base_dir: Path):
    log("↩️ Voltando para Ativos...")

    for i, tentativa in enumerate([
        lambda: page.get_by_text("Ativos", exact=False).first.click(force=True),
        lambda: page.locator("text=Ativos").first.click(force=True),
    ], start=1):
        try:
            tentativa()
            page.wait_for_timeout(4000)
            screenshot_seguro(page, base_dir / "diag_ativos_retorno.png")
            log(f"✅ Clique em Ativos na tentativa {i}")
            return
        except Exception:
            continue

    page.goto("https://novacentral.fretebras.com.br/meus-fretes", wait_until="load", timeout=60000)
    page.wait_for_timeout(5000)
    screenshot_seguro(page, base_dir / "diag_ativos_retorno_url.png")
    log("✅ Retorno para Meus Fretes por URL direta")


def selecionar_todos(page, base_dir: Path):
    log("☑️ Selecionando todos os ativos...")
    page.wait_for_timeout(3000)

    checks = page.locator('input[type="checkbox"]')
    total = checks.count()

    for i in range(total):
        try:
            el = checks.nth(i)
            if el.is_visible():
                el.click(force=True)
                log(f"✅ Checkbox selecionado via input[type='checkbox'] índice {i}")
                screenshot_seguro(page, base_dir / "diag_checkbox_ativo_ok.png")
                return
        except Exception:
            continue

    raise RuntimeError("❌ Nenhum checkbox encontrado")


def baixar_listagem_ativos(page, pasta_downloads: Path, timestamp: str, base_dir: Path) -> Path:
    log("⬇️ Iniciando download da listagem...")

    with page.expect_download(timeout=30000) as download_info:
        page.get_by_text("Download da listagem", exact=False).click()

    download = download_info.value
    nome = download.suggested_filename
    caminho = pasta_downloads / f"{timestamp}_{nome}"
    download.save_as(str(caminho))

    log(f"✅ Arquivo salvo em: {caminho}")
    screenshot_seguro(page, base_dir / "diag_download_concluido.png")
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
            fazer_login(page, usuario, senha, base_dir)
            abrir_meus_fretes(page, base_dir)

            abrir_aba_desativados(page, base_dir)
            qtd_selecionados = selecionar_primeiro_desativado_automatico_com_hover(page, base_dir)
            log(f"ℹ️ Desativados automáticos selecionados: {qtd_selecionados}")

            if qtd_selecionados > 0:
                clicar_ativar_topo(page, base_dir)
                tratar_popup_ativar(page, base_dir)
                marcar_motivo_motorista_desistiu(page, base_dir)
                clicar_confirmar(page, base_dir)
                log("✅ Reativação concluída")

            voltar_para_ativos(page, base_dir)
            selecionar_todos(page, base_dir)
            caminho = baixar_listagem_ativos(page, pasta_downloads, timestamp, base_dir)

            return {
                "arquivo": str(caminho),
                "status": "ok",
                "houve_reativacao": qtd_selecionados > 0,
                "desativados_automaticos_encontrados": qtd_selecionados,
            }

        except Exception as e:
            screenshot_seguro(page, base_dir / "erro_fluxo_fretebras.png")
            log(f"❌ Erro: {e}")
            raise

        finally:
            browser.close()