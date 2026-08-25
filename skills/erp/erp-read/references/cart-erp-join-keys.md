# Cart ↔ Odoo Join-Key Mapping

How the marketplace (`cart_workflow` MCP) and Odoo ERP (`odoo` MCP) entities match. Both MCPs are registered in the same Hermes session; the join is by **key**, not by shared ID.

## Products

- Marketplace key: `id` (UUID), `name`, `sku` (**live**), `category`, `priceCents`, `stock`, `isActive`.
- Odoo key: `product.product` → `default_code` (SKU), `barcode`, `name`, `list_price`, `qty_available`.
- **Join key (live):** marketplace `sku` ↔ Odoo `default_code`. The 12 marketplace products carry `MP-<CAT>-<NN>` SKUs that match Odoo's `default_code` (the seed is the source of truth for both).
- **Current state (2026-08-25):** 12 products on both sides with matching SKUs — `cart-erp-stock` now produces real matches.

## Customers

- Marketplace key: `id` (UUID), `email` (masked), `role`, `externalId` (**live, unmasked**).
- Odoo key: `res.partner` → `email`, `ref` (Internal Reference), `name`, `is_company`, `country_id`.
- **Join key (live):** marketplace `externalId` (returned unmasked by `get_user_profile`) ↔ Odoo `res.partner.ref` (or `email`, since the seed sets `externalId = email` as a placeholder). Email stays masked in `get_user_profile` — PII invariant preserved.
- **Current state:** `cart-erp-customer` can now match by `externalId` without leaking the email.

## Orders ↔ Invoices

- Marketplace key: `id` (UUID), `userId`, `status`, `totalCents`, `items[].productId/unitPriceCents/quantity`, `createdAt`.
- Odoo key: `sale.order` (**now installed**) + `account.move` (`move_type='out_invoice'`) + `account.move.line`.
- **Join key:** order reference ↔ `sale.order.name` / invoice `ref`/`invoice_origin`, plus total + date + partner as fallback.
- **Current state:** `sale.order` is queryable (0 orders at check time). Reconcile remains design-only until invoices are actually created in Odoo and the customer join (`externalId`) is wired end-to-end.

## Match normalization (when matching by name/email)

- Lowercase, trim, collapse whitespace, strip diacritics (é→e), drop punctuation.
- Exact normalized equality first; fall back to `ilike` substring only when unambiguous.

## Honest summary

Transport is connected and the **product + customer entity keys are live** (SKU + externalId): the stock and customer bridges now produce real joins. Order/invoice reconciliation still awaits real invoices in Odoo.
