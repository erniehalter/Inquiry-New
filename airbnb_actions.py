# airbnb_actions.py

import logging
import asyncio
from playwright.async_api import Page, TimeoutError, Error as PlaywrightError
import settings 

async def login_to_airbnb(page: Page, check_url: str): 
    """
    Checks login status by navigating to the target check_url first.
    If redirected to login, performs login steps.
    """
    logging.info(f"Checking login status by navigating to target URL: {check_url}")
    try:
        await page.goto(check_url, timeout=settings.PLAYWRIGHT_TIMEOUT, wait_until='domcontentloaded')
        logging.info(f"Initial navigation attempt to {check_url} complete.")
        await page.wait_for_timeout(2000)
    except PlaywrightError as pe_goto:
         logging.error(f"Playwright error navigating to check_url {check_url}: {pe_goto}", exc_info=True)
         raise 

    current_url = page.url
    is_login_page = False
    if "login" in current_url or "signin" in current_url:
        is_login_page = True
        logging.info(f"Redirected to login page: {current_url}")
    else:
        login_page_indicator_selector = 'button[data-testid*="login"], button[data-testid*="signup"], input[type="email"], h3:has-text("Log in or sign up")'
        try:
            if await page.locator(login_page_indicator_selector).first.is_visible(timeout=settings.PLAYWRIGHT_TIMEOUT / 10):
                 is_login_page = True
                 logging.info("Detected login/signup elements on the page.")
        except TimeoutError:
             logging.info("Login page elements not found quickly. Assuming logged in.")

    if is_login_page:
        logging.info("Login required. Proceeding with login steps.")
        try:
            if not ("/login" in current_url and "airbnb.com" in current_url):
                 await page.goto("https://www.airbnb.com/login", timeout=settings.PLAYWRIGHT_TIMEOUT)

            email_input_selector = 'input[type="email"]'
            await page.wait_for_selector(email_input_selector, timeout=settings.PLAYWRIGHT_TIMEOUT)
            await page.fill(email_input_selector, settings.AIRBNB_EMAIL)
            logging.info("Email filled.")

            continue_button_selector = 'button:has-text("Continue")'
            await page.wait_for_selector(continue_button_selector, state='visible', timeout=settings.PLAYWRIGHT_TIMEOUT)
            await page.click(continue_button_selector)

            password_input_selector = 'input[type="password"]'
            await page.wait_for_selector(password_input_selector, timeout=settings.PLAYWRIGHT_TIMEOUT)
            await page.fill(password_input_selector, settings.AIRBNB_PASSWORD)
            logging.info("Password filled.")

            login_button_selector = 'button:has-text("Log in")'
            await page.wait_for_selector(login_button_selector, state='visible', timeout=settings.PLAYWRIGHT_TIMEOUT)
            await page.click(login_button_selector)
            
            await page.wait_for_url(lambda url: "login" not in url and "signin" not in url, timeout=settings.PLAYWRIGHT_TIMEOUT)
            logging.info("Login successful.")
            await page.goto(check_url, timeout=settings.PLAYWRIGHT_TIMEOUT, wait_until='domcontentloaded')
        except Exception as e:
            logging.error(f"Login failed: {e}")
            raise
    else:
        logging.info("Login not required.")

async def perform_inquiry_actions(page: Page, target_url: str):
    """
    Navigates to the inquiry, clicks pre-approve, and confirms 'Invite sent'.
    Returns: 'already_answered', 'success', or 'fail'.
    """
    logging.info(f"Navigating to target inquiry page: {target_url}")
    try:
        await page.goto(target_url, timeout=settings.PLAYWRIGHT_TIMEOUT, wait_until='domcontentloaded')
        
        already_answered_phrase = "Invite sent"
        expired_phrase = "Your invitation expired"
        preapprove_button_selector = 'a:has-text("Pre-approve")'
        
        sent_locator = page.locator(f"*:has-text('{already_answered_phrase}')")
        expired_locator = page.locator(f"*:has-text('{expired_phrase}')")
        button_locator = page.locator(preapprove_button_selector)

        combined_locator = sent_locator.or_(button_locator).or_(expired_locator)
        await combined_locator.first.wait_for(state='visible', timeout=settings.PLAYWRIGHT_TIMEOUT)

        if await sent_locator.first.is_visible() or await expired_locator.first.is_visible():
            logging.info("Inquiry already handled.")
            return 'already_answered'

        if await button_locator.first.is_visible():
            logging.info("Clicking Pre-approve...")
            await button_locator.click(timeout=5000)

            final_btn_selector = 'button[data-testid="hrd-pre-approve-inquiry-confirm"]'
            await page.wait_for_selector(final_btn_selector, state='visible', timeout=settings.PLAYWRIGHT_TIMEOUT)
            await page.click(final_btn_selector)
            
            # Final Confirmation Check
            try:
                await sent_locator.first.wait_for(state='visible', timeout=10000)
                logging.info("Confirmed: 'Invite sent' visible.")
                return 'success'
            except TimeoutError:
                logging.error("Confirmation FAILED: 'Invite sent' did not appear.")
                return 'fail'
        
        return 'fail'
    except Exception as e:
        logging.error(f"Action error: {e}")
        return 'fail'