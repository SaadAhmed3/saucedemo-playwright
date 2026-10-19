# SauceDemo Playwright Test (Python + Pytest)

Automated end-to-end test for <https://www.saucedemo.com/> (Task C of the SQA
Engineer practical assessment).

**Flow covered:** `standard_user` login -> add *Sauce Labs Backpack* -> verify
cart -> checkout -> verify order overview -> assert order confirmation.

## Prerequisites
- Python 3.9+
- Internet access to saucedemo.com

## Setup and run (Windows PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
pytest -q
```
macOS/Linux: activate with `source venv/bin/activate`.

Useful options: `pytest --headed` (watch the browser), `pytest --slowmo 500`.

On failure, a screenshot and a Playwright trace are saved in `test-results/`.

## What the test asserts
- Login lands on `/inventory.html` with the *Products* page.
- The backpack's add button changes to *Remove* and the cart badge shows `1`.
- The cart shows exactly one item, the right name, quantity 1 and the same price
  as the product list.
- The overview shows the same item and price, and `total = item total + tax`.
- The final page shows **"Thank you for your order!"** and the cart badge is gone.

## Design decisions
- `data-test` selectors rather than CSS classes or XPath, for stability.
- No fixed sleeps; Playwright auto-waits and retrying `expect()` assertions only.
- The final assertion checks the business outcome (order confirmed), not just a URL.
- The demo credentials are public (shown on the login page).

## AI assistance
AI was used for test design and code drafting. The first run failed because an
AI-drafted locator contained a typo (`sack-labs` instead of `sauce-labs`); I
found it by running the test and corrected it.

## Limitations
- One happy path; no negative, accessibility, mobile, load or backend checks.
- Depends on demo-site availability and its current `data-test` attributes.
- A passing UI test does not prove backend or production correctness.

## Test result
Run on 2026-10-19, Windows, Playwright 1.64.0, pytest 9.1.1: `1 passed in 5.46s`.
