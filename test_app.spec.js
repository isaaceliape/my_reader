const { test, expect } = require('@playwright/test');

test.describe('my_reader TTS App', () => {
    test('app loads successfully', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000');
        
        // Check page title
        await expect(page).toHaveTitle(/Local TTS/);
        
        // Check main elements exist
        await expect(page.locator('h1')).toContainText('Local TTS');
        await expect(page.locator('#textInput')).toBeVisible();
        await expect(page.locator('#voiceSelect')).toBeVisible();
        await expect(page.locator('#playBtn')).toBeVisible();
        
        console.log('✓ App loads successfully');
    });

    test('status shows TTS ready', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000');
        
        // Wait for status to load
        await page.waitForSelector('#status');
        const status = await page.locator('#status').textContent();
        
        // Should show "TTS Ready" or similar ok status
        expect(status).toContain('Ready');
        console.log('✓ TTS status:', status);
    });

    test('voices endpoint returns voices', async ({ page }) => {
        const response = await page.goto('http://127.0.0.1:8000/voices');
        const json = await response.json();
        
        expect(json.voices).toBeDefined();
        expect(json.voices.length).toBeGreaterThan(0);
        console.log('✓ Voices endpoint:', json.voices.length, 'voices available');
        console.log('  Voices:', json.voices.map(v => v.name).join(', '));
    });

    test('health endpoint works', async ({ page }) => {
        const response = await page.goto('http://127.0.0.1:8000/api');
        const json = await response.json();
        
        expect(json.status).toBe('ok');
        expect(json.tts_loaded).toBe(true);
        console.log('✓ Health check passed, TTS loaded:', json.tts_loaded);
    });

    test('generate TTS audio', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000');
        
        // Enter test text
        await page.fill('#textInput', 'Hello, this is a test of the local TTS system.');
        
        // Click generate button
        await page.click('#playBtn');
        
        // Wait for audio player to appear (max 30 seconds for TTS generation)
        await page.waitForSelector('#audioPlayer.visible', { timeout: 30000 });
        
        // Check audio element has source
        const audioSrc = await page.locator('#audioElement').getAttribute('src');
        expect(audioSrc).toBeTruthy();
        expect(audioSrc).toContain('blob:');
        
        console.log('✓ TTS generation successful, audio blob created');
    });
});
