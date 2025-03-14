const { test, expect } = require('@playwright/test');

test.describe('Chat functionality', () => {
  let authToken;

  test.beforeAll(async ({ request }) => {
    // Get auth token via API to use for subsequent tests
    const response = await request.post('/api/auth/login', {
      data: {
        email: 'admin@example.com',
        password: 'password'
      }
    });
    
    const body = await response.json();
    authToken = body.access_token;
    
    // Store the auth token in localStorage to be used in tests
    test.use({
      storageState: {
        cookies: [],
        origins: [
          {
            origin: 'http://localhost:3000',
            localStorage: [
              {
                name: 'authToken',
                value: authToken
              },
              {
                name: 'user',
                value: JSON.stringify({
                  id: 1,
                  name: 'Admin',
                  email: 'admin@example.com'
                })
              }
            ]
          }
        ]
      }
    });
  });

  test.beforeEach(async ({ page }) => {
    // Go to the chat page
    await page.goto('/chat');
  });

  test('should display the chat interface', async ({ page }) => {
    // Check chat interface elements
    await expect(page.getByText(/como posso ajudar você hoje/i)).toBeVisible();
    await expect(page.getByRole('textbox', { name: /digite sua mensagem/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /enviar/i })).toBeVisible();
  });

  test('should allow sending and receiving messages', async ({ page }) => {
    // Type a message
    await page.getByRole('textbox', { name: /digite sua mensagem/i }).fill('Olá, tudo bem?');
    
    // Send the message
    await page.getByRole('button', { name: /enviar/i }).click();
    
    // Verify message was sent
    await expect(page.getByText('Olá, tudo bem?')).toBeVisible();
    
    // Wait for response (may take some time)
    await page.waitForResponse(response => 
      response.url().includes('/api/chat/message') && 
      response.status() === 200
    );
    
    // Verify we got a response (any response)
    await expect(page.locator('div').filter({ hasText: /enviado por: (openai|google|anthropic|mistral)/i })).toBeVisible({ timeout: 30000 });
  });

  test('should allow creating a new conversation', async ({ page }) => {
    // Click on "Nova Conversa" button
    await page.getByRole('button', { name: /nova conversa/i }).click();
    
    // Type a conversation title
    await page.getByLabel(/título da conversa/i).fill('Teste de conversa');
    
    // Confirm
    await page.getByRole('button', { name: /criar/i }).click();
    
    // Send a message in the new conversation
    await page.getByRole('textbox', { name: /digite sua mensagem/i }).fill('Esta é uma nova conversa');
    await page.getByRole('button', { name: /enviar/i }).click();
    
    // Verify message was sent in the new conversation
    await expect(page.getByText('Esta é uma nova conversa')).toBeVisible();
    
    // Verify conversation appears in the list
    await expect(page.getByText('Teste de conversa')).toBeVisible();
  });

  test('should allow switching between conversations', async ({ page }) => {
    // Create first conversation
    await page.getByRole('button', { name: /nova conversa/i }).click();
    await page.getByLabel(/título da conversa/i).fill('Conversa 1');
    await page.getByRole('button', { name: /criar/i }).click();
    
    // Send a message in the first conversation
    await page.getByRole('textbox', { name: /digite sua mensagem/i }).fill('Mensagem na conversa 1');
    await page.getByRole('button', { name: /enviar/i }).click();
    
    // Create second conversation
    await page.getByRole('button', { name: /nova conversa/i }).click();
    await page.getByLabel(/título da conversa/i).fill('Conversa 2');
    await page.getByRole('button', { name: /criar/i }).click();
    
    // Send a message in the second conversation
    await page.getByRole('textbox', { name: /digite sua mensagem/i }).fill('Mensagem na conversa 2');
    await page.getByRole('button', { name: /enviar/i }).click();
    
    // Switch back to first conversation
    await page.getByText('Conversa 1').click();
    
    // Verify we see the message from the first conversation
    await expect(page.getByText('Mensagem na conversa 1')).toBeVisible();
    
    // Switch to second conversation
    await page.getByText('Conversa 2').click();
    
    // Verify we see the message from the second conversation
    await expect(page.getByText('Mensagem na conversa 2')).toBeVisible();
  });

  test('should allow regenerating a response', async ({ page }) => {
    // Send a message
    await page.getByRole('textbox', { name: /digite sua mensagem/i }).fill('Me dê um conselho bíblico');
    await page.getByRole('button', { name: /enviar/i }).click();
    
    // Wait for response
    await page.waitForResponse(response => 
      response.url().includes('/api/chat/message') && 
      response.status() === 200
    );
    
    // Store the first response text
    const firstResponseLocator = page.locator('div.MuiCardContent-root').filter({ hasText: /enviado por/i }).last();
    const firstResponseText = await firstResponseLocator.textContent();
    
    // Click regenerate button
    await page.getByRole('button', { name: /regenerar/i }).click();
    
    // Wait for new response
    await page.waitForResponse(response => 
      response.url().includes('/api/chat/message') && 
      response.status() === 200
    );
    
    // Get the new response text
    const secondResponseLocator = page.locator('div.MuiCardContent-root').filter({ hasText: /enviado por/i }).last();
    const secondResponseText = await secondResponseLocator.textContent();
    
    // Verify the responses are different (this is probabilistic, but likely different)
    expect(secondResponseText).not.toEqual(firstResponseText);
  });

  test('should allow changing the LLM provider', async ({ page }) => {
    // Open provider selector
    await page.getByRole('button', { name: /provedor/i }).click();
    
    // Select a different provider than the default (assume OpenAI is default)
    await page.getByRole('option', { name: /google/i }).click();
    
    // Send a message
    await page.getByRole('textbox', { name: /digite sua mensagem/i }).fill('Olá usando Google');
    await page.getByRole('button', { name: /enviar/i }).click();
    
    // Wait for response
    await page.waitForResponse(response => 
      response.url().includes('/api/chat/message') && 
      response.status() === 200
    );
    
    // Verify response shows the Google provider
    await expect(page.getByText(/google /i)).toBeVisible({ timeout: 30000 });
  });
}); 