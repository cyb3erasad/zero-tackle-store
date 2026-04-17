from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.orders import orders_bp
from app.models import Order, OrderItem, Cart, CartItem
from app.extensions import db


COD_FEE = 250


# ======================================================================
# CHECKOUT
# ======================================================================

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    GET  — show shipping form + order summary from cart
    POST — validate form, create Order + OrderItems, clear cart
    """
    cart = Cart.query.filter_by(user_id=current_user.id).first()

    # Redirect if cart is empty
    if not cart or not cart.items:
        flash('Your cart is empty. Add some products first.', 'warning')
        return redirect(url_for('cart.view_cart'))

    subtotal = float(cart.subtotal)
    total    = subtotal + COD_FEE

    if request.method == 'POST':
        # ---- collect form fields ------------------------------------
        first_name = request.form.get('first_name', '').strip()
        last_name  = request.form.get('last_name',  '').strip()
        email      = request.form.get('email',      '').strip()
        phone      = request.form.get('phone',      '').strip()
        country    = request.form.get('country',    '').strip()
        street     = request.form.get('street',     '').strip()
        apartment  = request.form.get('apartment',  '').strip()
        city       = request.form.get('city',       '').strip()
        state      = request.form.get('state',      '').strip()

        # ---- basic validation ---------------------------------------
        errors = []
        if not first_name: errors.append('First name is required.')
        if not last_name:  errors.append('Last name is required.')
        if not email:      errors.append('Email is required.')
        if not phone:      errors.append('Phone number is required.')
        if not country:    errors.append('Country is required.')
        if not street:     errors.append('Street address is required.')
        if not city:       errors.append('City is required.')
        if not state:      errors.append('State / Province is required.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'orders/checkout.html',
                cart=cart,
                subtotal=subtotal,
                cod_fee=COD_FEE,
                total=total
            )

        # ---- create order ------------------------------------------
        order = Order(
            user_id    = current_user.id,
            status     = Order.STATUS_PENDING,
            subtotal   = subtotal,
            cod_fee    = COD_FEE,
            total      = total,
            first_name = first_name,
            last_name  = last_name,
            email      = email,
            phone      = phone,
            country    = country,
            street     = street,
            apartment  = apartment,
            city       = city,
            state      = state,
        )
        db.session.add(order)
        db.session.flush()   # get order.id before committing

        # ---- snapshot each cart item into OrderItem ----------------
        for item in cart.items:
            order_item = OrderItem(
                order_id          = order.id,
                product_id        = item.product_id,
                size_label        = item.size_label,
                quantity          = item.quantity,
                price_at_purchase = item.product.price,
            )
            db.session.add(order_item)

        # ---- clear the cart ----------------------------------------
        for item in cart.items:
            db.session.delete(item)

        db.session.commit()

        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('orders.my_orders'))

    return render_template(
        'orders/checkout.html',
        cart=cart,
        subtotal=subtotal,
        cod_fee=COD_FEE,
        total=total
    )


# ======================================================================
# MY ORDERS
# ======================================================================

@orders_bp.route('/my-orders')
@login_required
def my_orders():
    """Lists all orders placed by the current user, newest first."""
    orders = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(Order.created_at.desc()).all()

    return render_template('orders/my_orders.html', orders=orders)


# ======================================================================
# ORDER DETAIL + INVOICE
# ======================================================================

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """
    Shows full order detail with printable invoice.
    Users can only view their own orders.
    """
    order = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template('orders/order_detail.html', order=order)