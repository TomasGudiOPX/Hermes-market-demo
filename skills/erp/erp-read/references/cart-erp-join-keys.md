# Cart ↔ Odoo Join-Key Mapping

How the marketplace (`cart_workflow` MCP) and Odoo ERP (`odoo` MCP) entities match. Both MCPs are registered in the same Hermes session; the join is by **key**, not by shared ID.

## Products

- Marketplace key: `id` (UUID) + `name` + `category` + `priceCents` + `stock` + `isActive`. **No SKU/barcode field.**
- Odoo key: `product.product` → `default_code` (SKU), `barcode`, `name`, `list_price`, `qty_available`.
- **Recommended join key:** `default_code` (Odoo) ↔ a future `sku` field on the marketplace product. Until added, fall back to normalized `name`.
- **Current state (2026-08-24):** marketplace has 12 products; Odoo has 3 (`Botle`, `Chair Office`, `Picture`). **Zero name overlap** — matching returns no-match until a shared SKU exists.

## Customers

- Marketplace key: `id` (UUID) + `email` (**masked** → e.g. `c*******@example.com`) + `role`.
- Odoo key: `res.partner` → `email`, `name`, `is_company`, `country_id`.
- **Recommended join key:** `email`. **Blocker:** `get_user_profile` masks the email, so the bot cannot match a marketplace user to an Odoo partner by email today. Needs an unmasked stable identifier (external id) or an admin-only unmasked lookup.

## Orders ↔ Invoices

- Marketplace key: `id` (UUID), `userId`, `status`, `totalCents`, `items[].productId/unitPriceCents/quantity`, `createdAt`.
- Odoo key: **no `sale.order`** (Sales app not installed). Accounting path is `account.move` (`move_type='out_invoice'`) + `account.move.line`.
- **Recommended join key:** order reference ↔ invoice `ref`/`invoice_origin`, plus total + date + partner as fallback.
- **Current state:** reconcile is design-only until (a) the customer join works and (b) invoices are actually created in Odoo.

## Match normalization (when matching by name/email)

- Lowercase, trim, collapse whitespace, strip diacritics (é→e), drop punctuation.
- Exact normalized equality first; fall back to `ilike` substring only when unambiguous.

## Honest summary

Transport is connected; **entity keys are not.** The bridges work today as *detectors* (they report "no match found" cleanly) and become real the moment a shared SKU + unmasked email/stable-id are added.
