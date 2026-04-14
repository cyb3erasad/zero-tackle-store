from app.admin import admin_bp
from app.admin.decorators import admin_required

# All admin routes are protected with @login_required + @admin_required
# Built fully in Step 9
#
# GET  /admin/dashboard
#   - Stats cards: total users, total orders, total revenue
#   - Inventory summary per category (jerseys, footballs, shorts, etc.)
#   - Recent orders table (last 10)
#
# GET/POST /admin/add-product
#   - Form: product name, price, description, category, stock quantity, image
#   - For size-based categories (jerseys, shorts):
#       size options: S, M, L, XL, XXL with individual stock quantities
#       size chart image upload
#   - For non-size categories (footballs, etc.):
#       simple stock quantity field only
#
# GET  /admin/manage-products
#   - Table: product name, category, price, total stock
#   - Actions per row:
#       [Delete]    → removes product from DB
#       [Sold Out]  → sets stock to 0, shows "Sold Out" badge on store
#
# GET  /admin/orders
#   - Table: order ID, customer name, date, total, current status
#   - Click any order → order detail view (same as user invoice view)
#   - Inline status dropdown per order:
#       Pending → Processing → Shipped → Delivered → Cancelled
#   - Status update via POST /admin/orders/<order_id>/update-status
#
# GET  /admin/view-store
#   - Simple redirect to /products/ (store landing page)
#   - Admin sees the store exactly as a normal user would