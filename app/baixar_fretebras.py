import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

load_dotenv()


def log(msg: str):
    print(msg)


def screenshot_seguro(page, caminho: Path):
    try:
        page.screenshot(path=str(caminho), full_page=True)
        log(f"📸 Screenshot salva em {caminho.name}")
    except Exception as e:
        log(f"⚠️ Não foi possível salvar screenshot: {e}")


def fazer_login(page, usuario: str, senha: str):
    log("🔐 Abrindo Fretebras...")
    page.goto("https://novacentral.fretebras.com.br", wait_until="load", timeout=60000)

    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except PlaywrightTimeoutError:
        pass

    # usuário
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

    # senha
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
        raise RuntimeError("Não foi possível clicar no botão de login.")

    page.wait_for_timeout(8000)
    log("✅ Login concluído")
    log(f"URL após login: {page.url}")


def abrir_meus_fretes(page):
    page.goto("https://novacentral.fretebras.com.br/meus-fretes", wait_until="load", timeout=60000)
    page.wait_for_timeout(5000)
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
            log(f"✅ Clique em Desativados na tentativa {i}")
            page.wait_for_timeout(5000)
            log("✅ Aba Desativados aberta")
            return
        except Exception:
            continue

    try:
        page.mouse.click(245, 104)
        log("✅ Clique em Desativados por coordenada")
        page.wait_for_timeout(5000)
        log("✅ Aba Desativados aberta")
        return
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "erro_aba_desativados.png")
    raise RuntimeError("Não foi possível abrir a aba Desativados.")


def marcar_fretes_desativados_automaticamente(page):
    log("🔎 Procurando fretes com texto 'Frete desativado automaticamente'...")

    itens = page.locator("text=/Frete desativado automaticamente/i")
    total = itens.count()

    log(f"📦 Total de fretes desativados automaticamente encontrados: {total}")
    return total

def clicar_ativar_topo(page, base_dir: Path):
    log("🟢 Tentando clicar em Ativar do topo...")
    page.wait_for_timeout(2500)

    tentativas = [
        lambda: page.get_by_text("Ativar", exact=False).first.click(force=True),
        lambda: page.locator("button").filter(has_text="Ativar").first.click(force=True),
        lambda: page.locator("span").filter(has_text="Ativar").first.click(force=True),
        lambda: page.locator("div").filter(has_text="Ativar").first.click(force=True),
        lambda: page.locator("text=Ativar").first.click(force=True),
    ]

    for i, tentativa in enumerate(tentativas, start=1):
        try:
            tentativa()
            log(f"✅ Clique em Ativar na tentativa {i}")
            page.wait_for_timeout(2500)
            return
        except Exception:
            continue

    try:
        page.mouse.click(1180, 145)
        log("✅ Clique em Ativar por coordenada")
        page.wait_for_timeout(2500)
        return
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "erro_botao_ativar_topo.png")
    raise RuntimeError("Não foi possível clicar em Ativar do topo.")


def tratar_modal_intermediario_ativar(page, base_dir: Path):
    log("🔵 Tratando popup 'Ativar fretes?'...")
    page.wait_for_timeout(3000)

    # tenta localizar um dialog aberto
    modal = None
    try:
        dialogs = page.locator("div[role='dialog']")
        total_dialogs = dialogs.count()

        for i in range(total_dialogs):
            d = dialogs.nth(i)
            try:
                texto = d.inner_text().strip().lower()
                if "ativar frete" in texto or "ativar fretes" in texto:
                    modal = d
                    break
            except Exception:
                continue
    except Exception:
        pass

    # fallback: procurar qualquer bloco grande com o texto
    if modal is None:
        try:
            blocos = page.locator("div")
            total_blocos = blocos.count()
            for i in range(min(total_blocos, 300)):
                b = blocos.nth(i)
                try:
                    texto = b.inner_text().strip().lower()
                    if "ativar frete" in texto or "ativar fretes" in texto:
                        modal = b
                        break
                except Exception:
                    continue
        except Exception:
            pass

    if modal is None:
        log("ℹ️ Popup intermediário não apareceu.")
        return

    log("✅ Popup intermediário detectado")

    # clica no botão Ativar DENTRO do modal
    clicou = False

    # 1) botões dentro do modal
    try:
        botoes = modal.locator("button")
        total_botoes = botoes.count()

        for i in range(total_botoes):
            try:
                btn = botoes.nth(i)
                texto = btn.inner_text().strip().lower()
                if texto == "ativar" or "ativar" in texto:
                    btn.click(force=True)
                    log(f"✅ Clique no Ativar do popup via botão índice {i}")
                    clicou = True
                    break
            except Exception:
                continue
    except Exception:
        pass

    # 2) texto dentro do modal
    if not clicou:
        try:
            modal.get_by_text("Ativar", exact=False).last.click(force=True)
            log("✅ Clique no Ativar do popup via texto interno")
            clicou = True
        except Exception:
            pass

    # 3) JS dentro do modal
    if not clicou:
        try:
            botoes = modal.locator("button")
            total_botoes = botoes.count()

            for i in range(total_botoes):
                try:
                    btn = botoes.nth(i)
                    texto = btn.inner_text().strip().lower()
                    if "ativar" in texto:
                        page.evaluate("(el) => el.click()", btn)
                        log(f"✅ Clique no Ativar do popup via JS no botão {i}")
                        clicou = True
                        break
                except Exception:
                    continue
        except Exception:
            pass

    # 4) fallback coordenada do botão azul do popup
    if not clicou:
        try:
            page.mouse.click(647, 336)
            log("✅ Clique no Ativar do popup por coordenada")
            clicou = True
        except Exception:
            pass

    if not clicou:
        screenshot_seguro(page, base_dir / "erro_modal_ativar.png")
        raise RuntimeError("Não foi possível clicar no botão Ativar do popup intermediário.")

    page.wait_for_timeout(3000)


def marcar_motivo_motorista_desistiu(page, base_dir: Path):
    log("📝 Tentando marcar motivo: Motorista desistiu da negociação...")
    page.wait_for_timeout(2500)

    tentativas = [
        lambda: page.get_by_text("Motorista desistiu da negociação", exact=False).first.click(force=True),
        lambda: page.locator("label").filter(has_text="Motorista desistiu da negociação").first.click(force=True),
        lambda: page.locator("span").filter(has_text="Motorista desistiu da negociação").first.click(force=True),
        lambda: page.locator("div").filter(has_text="Motorista desistiu da negociação").first.click(force=True),
        lambda: page.locator("text=Motorista desistiu da negociação").first.click(force=True),
    ]

    for i, tentativa in enumerate(tentativas, start=1):
        try:
            tentativa()
            log(f"✅ Motivo marcado na tentativa {i}")
            page.wait_for_timeout(1500)
            return
        except Exception:
            continue

    try:
        candidatos = page.locator("label, div, span, input")
        total = candidatos.count()

        for i in range(min(total, 300)):
            try:
                el = candidatos.nth(i)
                texto = el.inner_text().strip().lower()
                if "motorista desistiu" in texto:
                    page.evaluate("(el) => el.click()", el)
                    log(f"✅ Motivo marcado via JS no elemento {i}")
                    page.wait_for_timeout(1500)
                    return
            except Exception:
                continue
    except Exception:
        pass

    try:
        page.mouse.click(385, 346)
        log("✅ Motivo marcado por coordenada")
        page.wait_for_timeout(1500)
        return
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "erro_motivo_reativacao.png")
    raise RuntimeError("Não foi possível marcar o motivo 'Motorista desistiu da negociação'.")


def clicar_confirmar_motivo(page, base_dir: Path):
    log("✅ Tentando clicar em Confirmar...")
    page.wait_for_timeout(1200)

    tentativas = [
        lambda: page.get_by_text("Confirmar", exact=False).first.click(force=True),
        lambda: page.locator("button").filter(has_text="Confirmar").first.click(force=True),
        lambda: page.locator("span").filter(has_text="Confirmar").first.click(force=True),
        lambda: page.locator("div").filter(has_text="Confirmar").first.click(force=True),
        lambda: page.locator("text=Confirmar").first.click(force=True),
    ]

    for i, tentativa in enumerate(tentativas, start=1):
        try:
            tentativa()
            log(f"✅ Clique em Confirmar na tentativa {i}")
            page.wait_for_timeout(4000)
            return
        except Exception:
            continue

    try:
        page.mouse.click(611, 396)
        log("✅ Clique em Confirmar por coordenada")
        page.wait_for_timeout(4000)
        return
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "erro_confirmar_reativacao.png")
    raise RuntimeError("Não foi possível clicar em Confirmar.")


def reativar_desativados_automaticos(page, base_dir: Path) -> bool:
    abrir_aba_desativados(page, base_dir)

    itens = page.locator("text=/Frete desativado automaticamente/i")
    total = itens.count()

    log(f"⚠️ Fretes desativados automaticamente encontrados: {total}")
    log("ℹ️ Reativação automática pausada por segurança.")

    return False


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
            log(f"✅ Clique em Ativos na tentativa {i}")
            page.wait_for_timeout(4000)
            return
        except Exception:
            continue

    try:
        page.goto("https://novacentral.fretebras.com.br/meus-fretes", wait_until="load", timeout=60000)
        page.wait_for_timeout(5000)
        log("✅ Retorno para Meus Fretes por URL direta")
        log(f"URL atual: {page.url}")
        return
    except Exception:
        pass

    screenshot_seguro(page, base_dir / "erro_aba_ativos.png")
    raise RuntimeError("Não foi possível voltar para a aba Ativos.")


def baixar_listagem_ativos(page, pasta_downloads: Path, timestamp: str, base_dir: Path) -> Path:
    log("⬇️ Baixando listagem dos ativos...")

    clicou_checkbox = False

    try:
        checks = page.locator('input[type="checkbox"]')
        total = checks.count()
        for i in range(total):
            try:
                el = checks.nth(i)
                if el.is_visible():
                    el.click(force=True)
                    log(f"✅ Clique em selecionar todos com seletor: input[type='checkbox'] | índice {i}")
                    clicou_checkbox = True
                    break
            except Exception:
                continue
    except Exception:
        pass

    if not clicou_checkbox:
        screenshot_seguro(page, base_dir / "erro_checkbox_ativos.png")
        raise RuntimeError("Não foi possível clicar no Selecionar todos dos ativos.")

    page.wait_for_timeout(1500)

    caminho_final = None

    for seletor in [
        'button:has-text("Download da listagem")',
        'a:has-text("Download da listagem")',
        'text="Download da listagem"',
    ]:
        try:
            with page.expect_download(timeout=20000) as download_info:
                page.locator(seletor).first.click(force=True)

            download = download_info.value
            nome_original = download.suggested_filename
            nome_final = f"{timestamp}_{nome_original}"
            caminho_final = pasta_downloads / nome_final
            download.save_as(str(caminho_final))

            log(f"✅ Download concluído com seletor: {seletor}")
            log(f"✅ Nome original: {nome_original}")
            log(f"✅ Arquivo salvo em: {caminho_final}")
            break
        except Exception:
            continue

    if caminho_final is None:
        screenshot_seguro(page, base_dir / "erro_download_fretebras.png")
        raise RuntimeError("Não foi possível baixar a listagem.")

    return caminho_final


def baixar_listagem():
    usuario = os.getenv("FRETEBRAS_USER", "").strip()
    senha = os.getenv("FRETEBRAS_PASS", "").strip()

    if not usuario or not senha:
        raise ValueError("Defina FRETEBRAS_USER e FRETEBRAS_PASS no .env")

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

            houve_reativacao = reativar_desativados_automaticos(page, base_dir)
            log(f"ℹ️ Houve reativação? {houve_reativacao}")

            voltar_para_ativos(page, base_dir)

            caminho = baixar_listagem_ativos(page, pasta_downloads, timestamp, base_dir)

            return {
                "arquivo": caminho,
                "houve_reativacao": houve_reativacao,
            }

        except Exception as e:
            screenshot_seguro(page, base_dir / "erro_fluxo_fretebras.png")
            log(f"❌ Erro no fluxo: {e}")
            raise

        finally:
            try:
                browser.close()
            except Exception:
                pass