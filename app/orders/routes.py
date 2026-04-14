from app.orders import orders_bp

# Orders routes — built in Step 7
#
# GET/POST /orders/checkout
#   - Shows shipping form (first name, last name, country, street address,
#     apartment, city, state, phone, email)
#   - Right panel shows order summary with cart items, subtotal,
#     COD fee (fixed Rs 250), and total
#   - Payment method: Cash on Delivery only
#   - On confirm → creates Order + OrderItems, clears cart
#
# GET /orders/my-orders
#   - Login required
#   - Lists all orders for the logged-in user
#   - Shows order ID, date, status, total
#
# GET /orders/<order_id>
#   - Login required
#   - Full order detail view
#   - Printable invoice with: order ID, date, items, shipping info,
#     subtotal, COD fee, grand total, status