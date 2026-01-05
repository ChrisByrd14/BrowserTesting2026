# Splinter Browser Testing Presentation Highlights

## Presentation Outline

### 1. Introduction to Web Application Testing
- **What**: Automated testing of web applications through a browser interface
- **Why**: Catch UI bugs, verify user flows, test client-side interactions
- **How**: Using Python, Pytest, and Splinter to automate browser interactions

### 2. Why Splinter?
- Browser automation made simple and Pythonic
- Abstracts away Selenium complexity with a clean API
- Multi-driver support (Firefox, Chrome, etc.)
- Great for integration/E2E testing

### 3. Getting Started with Splinter
- Installation and setup
- Creating a Browser instance
- Understanding fixtures with Pytest for reusable browser setup

### 4. Core Splinter API - Navigation
- **`browser.visit(url)`** - Navigate to a URL
- **`browser.url`** - Get the current URL property
- Understanding URLs and redirects in tests

### 5. Core Splinter API - Finding Elements
- **`browser.find_by_css(selector)`** - Find elements by CSS selector
- **`browser.find_by_tag(tag_name)`** - Find elements by HTML tag
- **`.first`** - Get the first element from a collection
- **`.text`** - Access element text content

### 6. Core Splinter API - Text Assertions
- **`browser.is_text_present(text)`** - Check if text is visible on page (most important!)
- **`browser.html`** - Get full HTML of the page (useful for complex assertions)
- Combining text assertions with `wait_time` parameter

### 7. Core Splinter API - User Interactions
- **`browser.fill(field_name, value)`** - Fill form fields by name
- **`element.click()`** - Click buttons and links
- **Form submission** workflow: fill → click → assertions

### 8. Core Splinter API - Working with Elements
- Understanding element objects and collections
- **`.text`** property - Extract element text
- **`.html`** property - Extract element HTML (chaining with page-level assertions)
- Chaining methods: `find_by_css()` → `first` → `.text`

### 9. Smart Waits and Timing
- **`wait_time` parameter** in `is_text_present(text, wait_time=2)`
- Why waits matter: asynchronous operations, dynamic content loading
- Avoiding flaky tests with proper wait strategies

### 10. Testing Workflows
- **Happy path testing**: Normal user flows
- **Error handling**: Testing validation and error messages
- **Redirect validation**: Checking URL changes after actions
- **Message verification**: Success/error alert messages

### 11. Test Organization with Pytest
- Fixtures for setup (browser lifecycle, test data)
- Scope management (session, package, function)
- Cleanup with fixtures
- Parameterization for multiple scenarios

### 12. Common Testing Patterns

#### Pattern 1: Navigate and Assert Text
```python
browser.visit(url)
assert browser.is_text_present("Expected text")
```

#### Pattern 2: Fill, Click, and Verify Redirect
```python
browser.fill("field_name", "value")
browser.find_by_css('button[type="submit"]').click()
assert browser.url.endswith("/expected-page")
```

#### Pattern 3: Find Elements and Check Content
```python
element = browser.find_by_css(".selector").first
assert "Expected content" in element.text
```

#### Pattern 4: Complex Assertions with HTML
```python
price_text = "$ 99.99"
assert browser.html.count(price_text) == 2  # Appears twice on page
```

### 13. Live Demo: Implementing Cart Tests
*(To be completed during presentation)*

**Test 1: `test_nonempty_cart`**
- Load cart items using fixture
- Visit cart page
- Verify both items are displayed
- Check quantity values
- Verify subtotals and total calculations

**Test 2: `test_deleting_from_cart`**
- Load cart with items
- Find and click delete button for an item
- Verify item is removed
- Verify success message appears
- Check that remaining items still display correctly

### 14. Best Practices & Tips
- Keep selectors stable and maintainable
- Use wait_time for dynamic content
- Test from user perspective (text, not implementation details)
- Isolate test data with fixtures
- Make tests readable—they document the application
- Use specific assertions—avoid generic checks
- Browser instances are expensive—reuse when possible

### 15. Troubleshooting Common Issues
- Elements not found → verify selector and wait time
- Flaky tests → likely need wait_time parameter
- Stale elements → re-find after navigation
- Browser state → ensure proper setup/teardown with fixtures

### 16. Next Steps
- Expand test coverage
- Add visual regression testing
- Integrate with CI/CD pipelines
- Consider headless browser mode for speed
- Explore accessibility testing with Splinter

---

## Key Splinter API Methods Reference

### Navigation
- `browser.visit(url)` - Navigate to a URL
- `browser.url` - Get current URL

### Finding Elements
- `browser.find_by_css(selector)` - Find by CSS selector
- `browser.find_by_tag(tag_name)` - Find by HTML tag
- `.first` - Get first element from collection
- Collection indexing: `[0]`, `[1]`, etc.

### Text & Content
- `browser.is_text_present(text, wait_time=None)` - Check if text exists
- `browser.html` - Get full page HTML
- `element.text` - Get element text
- `element.html` - Get element HTML

### Interactions
- `element.click()` - Click element
- `browser.fill(name, value)` - Fill form field by name
- Form submission via click on submit buttons

### Element Collections
- `browser.find_by_css()` returns a collection
- Can chain methods on collections
- `.first` gets single element, others return collection

---

## Testing Patterns Summary

| Pattern | Use Case | Example |
|---------|----------|---------|
| Text assertion | Verify visible content | `assert browser.is_text_present("Success")` |
| URL check | Verify navigation | `assert browser.url.endswith("/cart")` |
| Form fill & submit | User input workflow | `browser.fill("qty", "5"); click_button()` |
| Find & extract | Complex assertions | `cart_item.text; element.html.count()` |
| Error messages | Validation testing | `assert "Invalid" in browser.find_by_css(".alert").text` |

---

## Live Coding Session: What to Implement

The two unimplemented tests demonstrate different Splinter patterns:

1. **`test_nonempty_cart`** - Tests the happy path and data verification
   - Uses fixtures to load test data
   - Verifies multiple elements on a page
   - Checks calculated values (subtotals)

2. **`test_deleting_from_cart`** - Tests user interactions and state changes
   - Finds and clicks elements (delete button)
   - Verifies page updates after interaction
   - Checks for success/confirmation messages
