# Feathered Friends King comforter checker

Run the **Feathered Friends comforters** workflow manually from GitHub Actions.
It requests three genuine `https://featheredfriends.com/products/<handle>.js`
endpoints, fails on HTTP or schema errors, and prints all 16 King variants:
Summer/Light/Medium × 700+/850+ for regular and seconds Bavarian, and
Light/Medium × 700+/850+ for Organic Bavarian seconds. Prices are Shopify's
integer USD cents; availability is the endpoint's boolean, not inferred from price.

The run summary displays the table. The `comforter-results` artifact contains
raw product responses, the timestamped snapshot, and the Markdown report.
No schedule, notification credentials, or alerts are configured in this manual probe.

Parser checks: `python3 -m unittest discover -s comforter-checker -v`.
