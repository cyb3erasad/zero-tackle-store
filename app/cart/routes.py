from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.cart import cart_bp
from app.models import Cart, CartItem, Product, ProductSize
from app.extensions import db


# ======================================================================
# HELPER — get or create cart for current user
# ======================================================================

def get_or_create_cart():
    """Returns the current user's cart. Creates one if it doesn't exist."""
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return cart


# ======================================================================
# VIEW CART
# ======================================================================

@cart_bp.route('/')
@login_required
def view_cart():
    """Shows all items in the user's cart with subtotal and COD fee."""
    cart = get_or_create_cart()
    cod_fee = 250
    total = float(cart.subtotal) + cod_fee if cart.items else 0
    return render_template(
        'cart/cart.html',
        cart=cart,
        cod_fee=cod_fee,
        total=total
    )


# ======================================================================
# ADD TO CART
# ======================================================================

@cart_bp.route('/add', methods=['POST'])
@login_required
def add_to_cart():
    """
    Adds a product to cart.
    - Validates product exists and is in stock
    - For sized products: validates size is selected and in stock
    - If same product+size already in cart: increments quantity
    - Otherwise: creates new CartItem
    """
    product_id = request.form.get('product_id', type=int)
    size_label  = request.form.get('size_label', None)
    quantity    = request.form.get('quantity', 1, type=int)

    product = Product.query.get_or_404(product_id)

    # ---- stock validation --------------------------------------------
    if product.is_sold_out or product.total_stock == 0:
        flash('Sorry, this product is sold out.', 'danger')
        return redirect(url_for('products.detail', product_id=product_id))

    if product.has_sizes:
        if not size_label:
            flash('Please select a size.', 'warning')
            return redirect(url_for('products.detail', product_id=product_id))

        size = ProductSize.query.filter_by(
            product_id=product_id,
            size_label=size_label
        ).first()

        if not size or size.quantity == 0:
            flash(f'Size {size_label} is out of stock.', 'danger')
            return redirect(url_for('products.detail', product_id=product_id))

    # ---- get or create cart ------------------------------------------
    cart = get_or_create_cart()

    # ---- check if same item already in cart --------------------------
    existing = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id,
        size_label=size_label
    ).first()

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            size_label=size_label,
            quantity=quantity
        )
        db.session.add(item)

    db.session.commit()
    flash(f'"{product.name}" added to your cart!', 'success')
    return redirect(url_for('cart.view_cart'))


# ======================================================================
# UPDATE QUANTITY
# ======================================================================

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_item(item_id):
    """Updates quantity of a cart item. Removes if quantity is 0."""
    cart = get_or_create_cart()
    item = CartItem.query.filter_by(
        id=item_id,
        cart_id=cart.id
    ).first_or_404()

    quantity = request.form.get('quantity', type=int)

    if quantity is None or quantity < 1:
        db.session.delete(item)
        flash('Item removed from cart.', 'info')
    else:
        item.quantity = quantity

    db.session.commit()
    return redirect(url_for('cart.view_cart'))


# ======================================================================
# REMOVE ITEM
# ======================================================================

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_item(item_id):
    """Removes a single item from the cart."""
    cart = get_or_create_cart()
    item = CartItem.query.filter_by(
        id=item_id,
        cart_id=cart.id
    ).first_or_404()

    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))


# ======================================================================
# CLEAR CART
# ======================================================================

@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear_cart():
    """Removes all items from the cart."""
    cart = get_or_create_cart()
    for item in cart.items:
        db.session.delete(item)
    db.session.commit()
    flash('Your cart has been cleared.', 'info')
    return redirect(url_for('cart.view_cart'))