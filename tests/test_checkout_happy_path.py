"""
End-to-end happy path for https://www.saucedemo.com/

Flow: standard_user login -> add Sauce Labs Backpack -> verify cart ->
checkout -> verify order overview -> assert order confirmation.

Selectors use the site's data-test attributes (stable, intended for testing).
There are no fixed sleeps: every wait is a Playwright auto-wait or a retrying
expect() assertion.
"""
import os
import re

from playwright.sync_api import Page, expect

BASE_URL = os.environ.get("SAUCEDEMO_URL", "https://www.saucedemo.com/")
# Public demo credentials published on the login page (not real secrets).
USERNAME = os.environ.get("SAUCEDEMO_USER", "standard_user")
PASSWORD = os.environ.get("SAUCEDEMO_PASSWORD", "secret_sauce")

PRODUCT_NAME = "Sauce Labs Backpack"
ADD_BUTTON = "add-to-cart-sack-labs-backpack"
REMOVE_BUTTON = "remove-sack-labs-backpack"


def by_test(page: Page, name: str):
    return page.locator(f'[data-test="{name}"]')


def money(text: str) -> float:
    """'$29.99' / 'Item total: $29.99' -> 29.99"""
    match = re.search(r"\$([\d,]+\.\d{2})", text)
    assert match, f"No dollar amount found in {text!r}"
    return float(match.group(1).replace(",", ""))


def test_standard_user_can_buy_backpack(page: Page):
    # 1. Log in as standard_user
    page.goto(BASE_URL)
    by_test(page, "username").fill(USERNAME)
    by_test(page, "password").fill(PASSWORD)
    by_test(page, "login-button").click()
    expect(page).to_have_url(re.compile(r"/inventory\.html"))
    expect(by_test(page, "title")).to_have_text("Products")

    # 2. Remember the product's listed price, then add it to the cart
    product = by_test(page, "inventory-item").filter(has_text=PRODUCT_NAME)
    expect(product).to_have_count(1)
    listed_price = money(product.locator('[data-test="inventory-item-price"]').inner_text())

    by_test(page, ADD_BUTTON).click()
    expect(by_test(page, REMOVE_BUTTON)).to_be_visible()  # button toggled
    expect(by_test(page, "shopping-cart-badge")).to_have_text("1")

    # 3. Verify the cart contents
    by_test(page, "shopping-cart-link").click()
    expect(page).to_have_url(re.compile(r"/cart\.html"))
    expect(by_test(page, "title")).to_have_text("Your Cart")
    cart_items = by_test(page, "inventory-item")
    expect(cart_items).to_have_count(1)
    expect(by_test(page, "inventory-item-name")).to_have_text(PRODUCT_NAME)
    expect(by_test(page, "item-quantity")).to_have_text("1")
    assert money(by_test(page, "inventory-item-price").inner_text()) == listed_price

    # 4. Checkout: customer information
    by_test(page, "checkout").click()
    expect(page).to_have_url(re.compile(r"/checkout-step-one\.html"))
    by_test(page, "firstName").fill("Test")
    by_test(page, "lastName").fill("User")
    by_test(page, "postalCode").fill("12345")
    by_test(page, "continue").click()

    # 5. Verify the order overview, including the arithmetic
    expect(page).to_have_url(re.compile(r"/checkout-step-two\.html"))
    expect(by_test(page, "title")).to_have_text("Checkout: Overview")
    expect(by_test(page, "inventory-item-name")).to_have_text(PRODUCT_NAME)
    item_total = money(by_test(page, "subtotal-label").inner_text())
    tax = money(by_test(page, "tax-label").inner_text())
    total = money(by_test(page, "total-label").inner_text())
    assert item_total == listed_price, "Overview item total differs from listed price"
    assert round(item_total + tax, 2) == round(total, 2), (
        f"Total {total} != item total {item_total} + tax {tax}"
    )

    # 6. Finish and assert the business outcome: the order is confirmed
    by_test(page, "finish").click()
    expect(page).to_have_url(re.compile(r"/checkout-complete\.html"))
    expect(by_test(page, "complete-header")).to_have_text("Thank you for your order!")
    expect(by_test(page, "shopping-cart-badge")).to_have_count(0)  # cart emptied
