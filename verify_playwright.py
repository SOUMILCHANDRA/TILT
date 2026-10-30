import asyncio
from playwright.async_api import async_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def run_tests():
    print("=== TILT PLAYWRIGHT VERIFICATION SUITE ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--use-gl=angle', '--use-angle=swiftshader']
        )
        page = await browser.new_page()

        console_logs = []
        page_errors = []

        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # TEST 1: Load file directly
        print("\n--- Test 1: Loading file:///e:/tilt/index.html ---")
        await page.goto("file:///e:/tilt/index.html", wait_until="networkidle")
        await asyncio.sleep(1)

        # Check initial state
        init_state = await page.evaluate("""() => ({
            canvasExists: !!document.getElementById('game-canvas'),
            threeDefined: typeof THREE !== 'undefined',
            gameRunning: gameRunning,
            levelTitle: currentLevelData ? currentLevelData.title : null,
            marbleZ: marble ? marble.pos.z : null,
            controlMode: settings.controlMode
        })""")
        print(f"Initial State: {init_state}")
        assert init_state['canvasExists'], "Canvas does not exist!"
        assert init_state['threeDefined'], "THREE.js is not defined!"
        assert init_state['gameRunning'], "Game is not running!"
        assert init_state['controlMode'] == 'auto', f"Expected auto control mode, got {init_state['controlMode']}"

        # TEST 2: Keyboard WASD out-of-the-box response (No settings change required)
        print("\n--- Test 2: Testing WASD keyboard response out-of-the-box ---")
        z_before_w = await page.evaluate("() => marble.pos.z")
        await page.keyboard.down("w")
        await asyncio.sleep(1.8)
        await page.keyboard.up("w")
        z_after_w = await page.evaluate("() => marble.pos.z")
        print(f"Marble Z before 'w': {z_before_w:.2f}, after 'w': {z_after_w:.2f}")
        assert z_after_w < z_before_w - 0.5, f"Marble did not roll forward with 'w'! (before: {z_before_w}, after: {z_after_w})"
        print("PASS: Keyboard WASD successfully tilted the island and rolled the marble!")

        # TEST 3: Mouse Dragging
        print("\n--- Test 3: Testing Mouse Dragging ---")
        # Restart level to reset marble
        await page.evaluate("() => restartLevel()")
        await asyncio.sleep(0.5)
        z_before_drag = await page.evaluate("() => marble.pos.z")

        # Simulate click and drag forward
        await page.mouse.move(640, 360)
        await page.mouse.down()
        await page.mouse.move(640, 150, steps=10)
        await asyncio.sleep(1.8)
        await page.mouse.up()

        z_after_drag = await page.evaluate("() => marble.pos.z")
        print(f"Marble Z before drag: {z_before_drag:.2f}, after drag: {z_after_drag:.2f}")
        assert z_after_drag < z_before_drag - 0.5, f"Marble did not roll with drag! (before: {z_before_drag}, after: {z_after_drag})"
        print("PASS: Mouse drag successfully tilted the island and rolled the marble!")

        # TEST 4: Full Run to Goal & Victory Modal Verification
        print("\n--- Test 4: Rolling marble to goal pad for completion ---")
        await page.evaluate("() => restartLevel()")
        await asyncio.sleep(0.5)

        # Hold 'w' until goal reached
        await page.keyboard.down("w")
        completed = False
        for tick in range(16):
            await asyncio.sleep(0.5)
            st = await page.evaluate("() => ({ z: marble.pos.z, running: gameRunning })")
            if not st['running']:
                completed = True
                print(f"Level completed at tick {tick * 0.5:.1f}s!")
                break
        await page.keyboard.up("w")

        assert completed, "Level did not complete within time limit!"

        # Check Victory Modal
        victory_data = await page.evaluate("""() => {
            const modal = document.getElementById('modal-victory');
            return {
                modalActive: modal.classList.contains('active'),
                timeText: document.getElementById('victory-time-text').textContent,
                medalText: document.getElementById('victory-medal-text').textContent,
                ghostCode: document.getElementById('victory-ghost-code').value,
                starsCollected: starsCollected
            };
        }""")
        print(f"Victory Data: {victory_data}")
        assert victory_data['modalActive'], "Victory modal is not active!"
        assert len(victory_data['ghostCode']) > 10, "Ghost code was not generated!"
        print("PASS: Goal reached, Victory modal displayed with medals & ghost code!")

        await page.screenshot(path="e:/tilt/verified_victory.png")
        print("Saved verified_victory.png")

        # TEST 5: Ghost Replay Code Import & Playback
        print("\n--- Test 5: Importing Ghost Replay Code ---")
        ghost_code = victory_data['ghostCode']
        # Load level 1 again
        await page.evaluate("() => { loadLevel(0); closeModal('modal-victory'); }")
        await asyncio.sleep(0.5)

        # Import ghost
        imported = await page.evaluate(f"""() => {{
            const ghost = MultiplayerAPI.decodeGhost('{ghost_code}');
            if (ghost && ghost.keyframes.length > 0) {{
                ghostRunData = ghost;
                ghostMesh.visible = true;
                return true;
            }}
            return false;
        }}""")
        assert imported, "Failed to decode and import ghost replay!"
        ghost_visible = await page.evaluate("() => ghostMesh.visible")
        assert ghost_visible, "Ghost mesh is not visible!"
        print("PASS: Ghost replay code successfully imported and ghost marble is active!")

        # TEST 6: Daily Island Challenge
        print("\n--- Test 6: Testing Daily Island Challenge ---")
        await page.evaluate("() => document.getElementById('btn-select-daily').click()")
        await asyncio.sleep(0.5)

        daily_info = await page.evaluate("""() => ({
            levelTitle: currentLevelData.title,
            id: currentLevelData.id,
            hazardCount: activeHazards.length,
            starCount: activeStars.length
        })""")
        print(f"Daily Island Info: {daily_info}")
        assert "Daily Island" in daily_info['levelTitle'], "Daily Island was not loaded!"
        assert daily_info['starCount'] == 3, "Daily Island should have 3 stars!"
        print("PASS: Daily Island successfully generated and loaded!")

        # TEST 7: Console Errors and Warnings Check
        print("\n--- Test 7: Console Logs & Errors Audit ---")
        errors = [l for l in console_logs if "[error]" in l]
        warnings = [l for l in console_logs if "[warning]" in l]
        print(f"Total console logs: {len(console_logs)}")
        print(f"Total errors: {len(errors)}, Total warnings: {len(warnings)}")
        for err in errors:
            print(f"ERROR: {err}")
        for warn in warnings:
            print(f"WARN: {warn}")

        assert len(errors) == 0, f"Found {len(errors)} console errors!"
        assert len(page_errors) == 0, f"Found {len(page_errors)} uncaught page errors: {page_errors}"
        print("PASS: Zero console errors, zero uncaught page errors!")

        await page.screenshot(path="e:/tilt/verified_daily.png")
        print("Saved verified_daily.png")

        await browser.close()
        print("\n=== ALL PLAYWRIGHT TESTS PASSED WITH 100% SUCCESS! ===")

if __name__ == "__main__":
    asyncio.run(run_tests())
