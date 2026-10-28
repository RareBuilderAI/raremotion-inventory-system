
import sqlite3

import pandas as pd
import streamlit as st

from database import init_db, get_connection

# ==========================================
# RAREMOTION LABS — INVENTORY SYSTEM
# ==========================================

st.set_page_config(
    page_title="Raremotion Inventory System",
    page_icon="📦",
    layout="wide"
)

init_db()


# ==========================================
# DATABASE HELPERS
# ==========================================

def load_products():
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT id, name, category, quantity, price
            FROM products
            ORDER BY id DESC
            """,
            conn
        )


def load_sales():
    with get_connection() as conn:
        return pd.read_sql_query(
            """
            SELECT
                s.id,
                p.name AS product,
                s.quantity,
                s.total,
                s.created_at
            FROM sales AS s
            JOIN products AS p
                ON s.product_id = p.id
            ORDER BY s.id DESC
            """,
            conn
        )


def product_label(products, product_id):
    product = products.loc[
        products["id"] == product_id
    ].iloc[0]

    return f"{product['name']} (ID: {product_id})"


def add_product(name, category, quantity, price):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO products
                (name, category, quantity, price)
            VALUES (?, ?, ?, ?)
            """,
            (
                name.strip(),
                category.strip(),
                int(quantity),
                float(price)
            )
        )
        conn.commit()


def update_product(product_id, name, category, price):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE products
            SET name = ?, category = ?, price = ?
            WHERE id = ?
            """,
            (
                name.strip(),
                category.strip(),
                float(price),
                int(product_id)
            )
        )
        conn.commit()
        return cursor.rowcount == 1


def delete_product(product_id):
    with get_connection() as conn:
        sales_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM sales
            WHERE product_id = ?
            """,
            (int(product_id),)
        ).fetchone()[0]

        if sales_count > 0:
            return False, "Product has sales history."

        cursor = conn.execute(
            "DELETE FROM products WHERE id = ?",
            (int(product_id),)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return False, "Product not found."

        return True, "Product deleted successfully."


def update_stock(product_id, action, amount):
    with get_connection() as conn:
        if action == "Stock In":
            cursor = conn.execute(
                """
                UPDATE products
                SET quantity = quantity + ?
                WHERE id = ?
                """,
                (int(amount), int(product_id))
            )
        else:
            cursor = conn.execute(
                """
                UPDATE products
                SET quantity = quantity - ?
                WHERE id = ?
                  AND quantity >= ?
                """,
                (
                    int(amount),
                    int(product_id),
                    int(amount)
                )
            )

        if cursor.rowcount != 1:
            return False

        conn.commit()
        return True


def record_sale(product_id, quantity):
    with get_connection() as conn:
        try:
            conn.execute("BEGIN IMMEDIATE")

            product = conn.execute(
                """
                SELECT quantity, price
                FROM products
                WHERE id = ?
                """,
                (int(product_id),)
            ).fetchone()

            if product is None:
                conn.rollback()
                return False, "Product not found."

            available, price = product

            if int(quantity) > int(available):
                conn.rollback()
                return False, "Insufficient stock."

            total = int(quantity) * float(price)

            cursor = conn.execute(
                """
                UPDATE products
                SET quantity = quantity - ?
                WHERE id = ?
                  AND quantity >= ?
                """,
                (
                    int(quantity),
                    int(product_id),
                    int(quantity)
                )
            )

            if cursor.rowcount != 1:
                conn.rollback()
                return False, "Stock update failed."

            conn.execute(
                """
                INSERT INTO sales
                    (product_id, quantity, total)
                VALUES (?, ?, ?)
                """,
                (
                    int(product_id),
                    int(quantity),
                    total
                )
            )

            conn.commit()
            return True, f"Sale recorded: ₦{total:,.2f}"

        except sqlite3.Error:
            conn.rollback()
            raise


# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("💛 Raremotion Labs")
st.sidebar.caption("Inventory Management System")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Products",
        "Stock Management",
        "Sales",
        "Reports"
    ]
)

st.title("📦 Raremotion Inventory System")
st.caption(
    "Business Inventory Management | Powered by Raremotion Labs"
)

st.divider()


# ==========================================
# DASHBOARD
# ==========================================

if menu == "Dashboard":

    st.header("Dashboard Overview")

    products = load_products()
    sales = load_sales()

    total_products = len(products)
    total_units = int(products["quantity"].sum())

    low_stock = int(
        (products["quantity"] <= 5).sum()
    )

    inventory_value = float(
        (
            products["quantity"] *
            products["price"]
        ).sum()
    )

    total_revenue = float(sales["total"].sum())

    a, b, c, d = st.columns(4)

    a.metric("Total Products", total_products)
    b.metric("Stock Units", total_units)
    c.metric(
        "Inventory Value",
        f"₦{inventory_value:,.2f}"
    )
    d.metric(
        "Total Revenue",
        f"₦{total_revenue:,.2f}"
    )

    st.divider()

    if low_stock > 0:
        st.warning(
            f"⚠️ {low_stock} product(s) have low stock."
        )
    else:
        st.success("No low-stock products.")

    st.subheader("Inventory Overview")

    if products.empty:
        st.info(
            "No products yet. Open Products to add an item."
        )
    else:
        st.dataframe(
            products,
            width="stretch",
            hide_index=True
        )

    if not sales.empty:
        st.subheader("Recent Sales")
        st.dataframe(
            sales.head(10),
            width="stretch",
            hide_index=True
        )


# ==========================================
# PRODUCT MANAGEMENT
# ==========================================

elif menu == "Products":

    st.header("Product Management")

    st.subheader("Add New Product")

    with st.form("add_product", clear_on_submit=True):

        name = st.text_input("Product Name")
        category = st.text_input("Category")

        quantity = st.number_input(
            "Initial Stock Quantity",
            min_value=0,
            step=1
        )

        price = st.number_input(
            "Unit Selling Price (₦)",
            min_value=0.0,
            step=100.0
        )

        submitted = st.form_submit_button(
            "Add Product"
        )

    if submitted:
        if not name.strip():
            st.error("Product name is required.")
        else:
            add_product(
                name,
                category,
                quantity,
                price
            )
            st.success("Product added successfully!")
            st.rerun()

    st.divider()

    products = load_products()

    st.subheader("All Products")

    if products.empty:
        st.info("No products available.")

    else:
        st.dataframe(
            products,
            width="stretch",
            hide_index=True
        )

        st.divider()
        st.subheader("Edit Product")

        selected_id = st.selectbox(
            "Select Product",
            products["id"].tolist(),
            format_func=lambda x: product_label(
                products, x
            )
        )

        selected = products.loc[
            products["id"] == selected_id
        ].iloc[0]

        with st.form("edit_product"):

            new_name = st.text_input(
                "Product Name",
                value=str(selected["name"])
            )

            new_category = st.text_input(
                "Category",
                value=str(
                    selected["category"] or ""
                )
            )

            new_price = st.number_input(
                "Selling Price (₦)",
                min_value=0.0,
                value=float(selected["price"]),
                step=100.0
            )

            update = st.form_submit_button(
                "Save Changes"
            )

        if update:
            if not new_name.strip():
                st.error(
                    "Product name cannot be empty."
                )
            else:
                success = update_product(
                    selected_id,
                    new_name,
                    new_category,
                    new_price
                )

                if success:
                    st.success("Product updated!")
                    st.rerun()
                else:
                    st.error("Product not found.")

        st.divider()
        st.subheader("Delete Product")

        st.warning(
            "Products with recorded sales cannot "
            "be deleted."
        )

        confirm_delete = st.checkbox(
            "I confirm deletion of this product."
        )

        if st.button(
            "Delete Selected Product",
            disabled=not confirm_delete
        ):
            success, message = delete_product(
                selected_id
            )

            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


# ==========================================
# STOCK MANAGEMENT
# ==========================================

elif menu == "Stock Management":

    st.header("Stock Management")

    products = load_products()

    if products.empty:
        st.info("Add products first.")

    else:
        selected_id = st.selectbox(
            "Select Product",
            products["id"].tolist(),
            format_func=lambda x: product_label(
                products, x
            )
        )

        selected = products.loc[
            products["id"] == selected_id
        ].iloc[0]

        st.metric(
            "Current Stock",
            int(selected["quantity"])
        )

        action = st.radio(
            "Stock Action",
            ["Stock In", "Stock Out"],
            horizontal=True
        )

        amount = st.number_input(
            "Quantity",
            min_value=1,
            step=1
        )

        if st.button("Update Stock"):

            success = update_stock(
                selected_id,
                action,
                amount
            )

            if success:
                st.success(
                    "Stock updated successfully!"
                )
                st.rerun()
            else:
                st.error(
                    "Insufficient stock or product not found."
                )

        st.divider()

        st.subheader("Low Stock Alerts")

        low_stock = products[
            products["quantity"] <= 5
        ]

        if low_stock.empty:
            st.success(
                "All products have sufficient stock."
            )
        else:
            st.warning(
                f"{len(low_stock)} product(s) "
                "need restocking."
            )

            st.dataframe(
                low_stock,
                width="stretch",
                hide_index=True
            )


# ==========================================
# SALES MANAGEMENT
# ==========================================

elif menu == "Sales":

    st.header("Sales Management")

    products = load_products()

    if products.empty:
        st.info("Add products before recording sales.")

    else:
        selected_id = st.selectbox(
            "Select Product",
            products["id"].tolist(),
            format_func=lambda x: product_label(
                products, x
            )
        )

        selected = products.loc[
            products["id"] == selected_id
        ].iloc[0]

        st.metric(
            "Available Stock",
            int(selected["quantity"])
        )

        quantity = st.number_input(
            "Quantity Sold",
            min_value=1,
            step=1
        )

        estimated_total = (
            int(quantity) *
            float(selected["price"])
        )

        st.info(
            f"Estimated Sale Total: "
            f"₦{estimated_total:,.2f}"
        )

        if st.button("Record Sale"):

            success, message = record_sale(
                selected_id,
                quantity
            )

            if success:
                st.session_state["sale_message"] = message
                st.rerun()
            else:
                st.error(message)

    if "sale_message" in st.session_state:
        st.success(
            st.session_state.pop("sale_message")
        )

    st.divider()

    st.subheader("Sales History")

    sales = load_sales()

    if sales.empty:
        st.info("No sales recorded yet.")
    else:
        st.dataframe(
            sales,
            width="stretch",
            hide_index=True
        )


# ==========================================
# BUSINESS REPORTS
# ==========================================

elif menu == "Reports":

    st.header("Business Reports")

    products = load_products()
    sales = load_sales()

    total_revenue = float(
        sales["total"].sum()
    )

    inventory_value = float(
        (
            products["quantity"] *
            products["price"]
        ).sum()
    )

    a, b, c = st.columns(3)

    a.metric(
        "Total Products",
        len(products)
    )

    b.metric(
        "Total Revenue",
        f"₦{total_revenue:,.2f}"
    )

    c.metric(
        "Inventory Selling Value",
        f"₦{inventory_value:,.2f}"
    )

    st.divider()

    st.subheader("Sales Analytics")

    if sales.empty:
        st.info(
            "Record sales to display analytics."
        )
    else:
        chart_data = (
            sales.groupby("product")["total"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(chart_data)

        st.subheader("Sales Transactions")

        st.dataframe(
            sales,
            width="stretch",
            hide_index=True
        )

    st.divider()

    st.subheader("Export Reports")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📥 Download Inventory CSV",
            data=products.to_csv(index=False),
            file_name="raremotion_inventory.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            label="📥 Download Sales CSV",
            data=sales.to_csv(index=False),
            file_name="raremotion_sales.csv",
            mime="text/csv"
        )

    st.caption(
        "Revenue is not profit. Inventory value "
        "uses selling prices."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "© 2026 Raremotion Labs | "
    "Inventory Management System"
)
