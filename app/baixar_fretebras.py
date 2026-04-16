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

    usuario_ok = False
    for seletor in [
        'input[name="username"]',
        'input[name="email"]',
        'input[id="username"]',
        'input[id="email"]',
        'input[type="email"]',
    ]:
        try:
            page.locator(seletor).first.wait_for(state="visible", timeout=4000)
            page.locator(seletor).first.fill(usuario)
            log(f"✅ Campo usuário preenchido com seletor: {seletor}")
            usuario_ok = True
            break
        except Exception:
            continue

    senha_ok = False
    for seletor in [
        'input[name="password"]',
        'input[id="password"]',
        'input[type="password"]',
    ]:
        try:
            page.locator(seletor).first.wait_for(state="visible", timeout=4000)
            page.locator(seletor).first.fill(senha)
            log(f"✅ Campo senha preenchido com seletor: {seletor}")
            senha_ok = True
            break
        except Exception:
            continue

    if not usuario_ok or not senha_ok:
        screenshot_seguro(page, base_dir / "diag_login_campos.png")
        raise RuntimeError("Não foi possível preencher login/senha.")

    entrou = False
    for seletor in [
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("Entrar")',
        'button:has-text("Acessar")',
    ]:
        try:
            page.locator(seletor).first.wait_for(state="visible", timeout=4000)
            page.locator(seletor).first.click(force=True)
            log(f"✅ Clique em entrar com seletor: {seletor}")
            entrou = True
            break
        except Exception:
            continue

    if not entrou:
        screenshot_seguro(page, base_dir / "diag_login_botao.png")
        raise RuntimeError("Não foi possível clicar no botão de login.")

    page.wait_for_timeout(8000)
    screenshot_seguro(page, base_dir / "diag_pos_login.png")
    log("✅ Login concluído")
    log(f"URL após login: {page.url}")


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

    tentativas = [
        lambda: page.get_by_text("Desativados", exact=False).first.click(force=True),
        lambda: page.get_by_text("Desativados:", exact=False).first.click(force=True),
        lambda: page.locator("button").filter(has_text="Desativados").first.click(force=True),
        lambda: page.locator("span").filter(has_text="Desativados").first.click(force=True),
        lambda: page.locator("div").filter(has_text="Desativados").first.click(force=True),
        lambda: page.locator("text=Desativados").first.click(force=True),
    ]

    for i, tentativa in enumerate(tentativas, start=1):
        try:
            tentativa()
            page.wait_for_timeout(5000)
            screenshot_seguro(page, base_dir / "diag_desativados_aberta.png")
            log(f"✅ Clique em Desativados na tentativa {i}")
            log("✅ Aba Desativados aberta")
            return
        except Exception:
            continue

    try:
        page.mouse.click(245, 104)
        page.wait_for_timeout(5000)
        screenshot_seguro(page, base_dir / "diag_desativados_aberta_coord.png")
        log("✅ Clique em Desativados por coordenada")
        log("✅ Aba Desativados aberta")
        return
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "erro_aba_desativados.png")
    raise RuntimeError("Não foi possível abrir a aba Desativados.")


def diagnosticar_desativados_automaticos(page, base_dir: Path) -> int:
    log("🔎 Diagnosticando fretes com texto 'Frete desativado automaticamente'...")

    page.wait_for_timeout(3000)
    screenshot_seguro(page, base_dir / "diag_desativados_antes_contagem.png")

    try:
        itens = page.locator("text=/Frete desativado automaticamente/i")
        total = itens.count()
    except Exception:
        total = 0

    log(f"📦 Total de fretes desativados automaticamente encontrados: {total}")

    # coleta alguns textos próximos para debug
    try:
        blocos = page.locator("div, span, p, small, strong, li")
        total_blocos = blocos.count()
        encontrados = 0

        for i in range(min(total_blocos, 300)):
            try:
                txt = blocos.nth(i).inner_text().strip()
                if txt and "desativado" in txt.lower():
                    log(f"🧭 Texto relacionado [{i}]: {repr(txt[:200])}")
                    encontrados += 1
                    if encontrados >= 10:
                        break
            except Exception:
                continue
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "diag_desativados_depois_contagem.png")
    return total


def voltar_para_ativos(page, base_dir: Path):
    log("↩️ Voltando para Ativos...")

    tentativas = [
        lambda: page.get_by_text("Ativos", exact=False).first.click(force=True),
        lambda: page.get_by_text("Ativos:", exact=False).first.click(force=True),
        lambda: page.locator("button").filter(has_text="Ativos").first.click(force=True),
        lambda: page.locator("span").filter(has_text="Ativos").first.click(force=True),
        lambda: page.locator("div").filter(has_text="Ativos").first.click(force=True),
        lambda: page.locator("text=Ativos").first.click(force=True),
    ]

    for i, tentativa in enumerate(tentativas, start=1):
        try:
            tentativa()
            page.wait_for_timeout(4000)
            screenshot_seguro(page, base_dir / "diag_ativos_retorno.png")
            log(f"✅ Clique em Ativos na tentativa {i}")
            return
        except Exception:
            continue

    try:
        page.goto("https://novacentral.fretebras.com.br/meus-fretes", wait_until="load", timeout=60000)
        page.wait_for_timeout(5000)
        screenshot_seguro(page, base_dir / "diag_ativos_retorno_url.png")
        log("✅ Retorno para Meus Fretes por URL direta")
        return
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "erro_aba_ativos.png")
    raise RuntimeError("Não foi possível voltar para a aba Ativos.")


def selecionar_todos(page, base_dir: Path):
    log("☑️ Selecionando todos os ativos...")
    page.wait_for_timeout(3000)

    # 1) checkbox nativo
    try:
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
    except Exception:
        pass

    # 2) role checkbox
    try:
        checks = page.locator('[role="checkbox"]')
        total = checks.count()

        for i in range(total):
            try:
                el = checks.nth(i)
                if el.is_visible():
                    el.click(force=True)
                    log(f"✅ Checkbox selecionado via role=checkbox índice {i}")
                    screenshot_seguro(page, base_dir / "diag_checkbox_role_ok.png")
                    return
            except Exception:
                continue
    except Exception:
        pass

    # 3) fallback por coordenada
    try:
        page.mouse.click(50, 105)
        page.wait_for_timeout(1500)
        screenshot_seguro(page, base_dir / "diag_checkbox_coord_ok.png")
        log("✅ Checkbox selecionado por coordenada")
        return
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "erro_checkbox_fretebras.png")
    raise RuntimeError("❌ Nenhum checkbox encontrado")


def baixar_listagem_ativos(page, pasta_downloads: Path, timestamp: str, base_dir: Path) -> Path:
    log("⬇️ Iniciando download da listagem...")

    with page.expect_download(timeout=30000) as download_info:
        clicou = False

        for seletor in [
            'button:has-text("Download da listagem")',
            'a:has-text("Download da listagem")',
            'text="Download da listagem"',
        ]:
            try:
                page.locator(seletor).first.click(force=True)
                log(f"✅ Clique em download com seletor: {seletor}")
                clicou = True
                break
            except Exception:
                continue

        if not clicou:
            screenshot_seguro(page, base_dir / "erro_download_botao.png")
            raise RuntimeError("Não foi possível clicar em Download da listagem.")

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
            qtd_desativados_auto = diagnosticar_desativados_automaticos(page, base_dir)
            log(f"ℹ️ Diagnóstico desativados automáticos: {qtd_desativados_auto}")

            voltar_para_ativos(page, base_dir)
            selecionar_todos(page, base_dir)
            caminho = baixar_listagem_ativos(page, pasta_downloads, timestamp, base_dir)

            return {
                "arquivo": str(caminho),
                "status": "ok",
                "houve_reativacao": False,
                "desativados_automaticos_encontrados": qtd_desativados_auto,
            }

        except Exception as e:
            screenshot_seguro(page, base_dir / "erro_fluxo_fretebras.png")
            log(f"❌ Erro: {e}")
            raise

        finally:
            browser.close()