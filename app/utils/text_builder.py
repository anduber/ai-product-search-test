from app.db.models import Product


def build_product_text(product: Product) -> str:
    lines: list[str] = []

    name = (product.name or "").strip()
    if name:
        lines.append(f"Name: {name}.")

    description = (product.description or "").strip()
    if description:
        lines.append(f"Description: {description}.")

    category = (product.category or "").strip()
    if category:
        lines.append(f"Category: {category}.")

    return "\n".join(lines)
