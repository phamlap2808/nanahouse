from core.controllers.product.io import (
    ProductCreateInput,
    ProductUpdateInput,
    ProductListInput,
    ProductOutput,
    CategoryOutput
)

# Examples for API documentation
PRODUCT_CREATE_EXAMPLES = {
    "basic_product": {
        "summary": "Sản phẩm cơ bản",
        "description": "Tạo sản phẩm với thông tin cơ bản",
        "value": ProductCreateInput(
            name="iPhone 15 Pro",
            slug="iphone-15-pro",
            description="iPhone 15 Pro với chip A17 Pro mạnh mẽ",
            short_description="iPhone 15 Pro - Hiệu năng vượt trội",
            sku="IPH15P-256",
            price=29990000,
            compare_price=32990000,
            cost=25000000,
            weight=0.187,
            dimensions="14.67 x 7.15 x 0.83 cm",
            stock=50,
            track_stock=True,
            allow_backorder=False,
            status="active",
            featured=True,
            tags='["smartphone", "apple", "premium"]',
            seo_title="iPhone 15 Pro - Mua ngay tại cửa hàng",
            seo_description="iPhone 15 Pro với chip A17 Pro, camera 48MP, pin lâu. Giao hàng miễn phí.",
            category_id=1
        ).dict()
    },
    "draft_product": {
        "summary": "Sản phẩm nháp",
        "description": "Tạo sản phẩm ở trạng thái nháp",
        "value": ProductCreateInput(
            name="Samsung Galaxy S24",
            slug="samsung-galaxy-s24",
            description="Samsung Galaxy S24 với AI tích hợp",
            short_description="Galaxy S24 - AI thông minh",
            sku="SGS24-128",
            price=22990000,
            stock=0,
            status="draft",
            featured=False,
            category_id=1
        ).dict()
    }
}

PRODUCT_UPDATE_EXAMPLES = {
    "update_price": {
        "summary": "Cập nhật giá",
        "description": "Cập nhật giá sản phẩm",
        "value": ProductUpdateInput(
            price=27990000,
            compare_price=30990000
        ).dict(exclude_unset=True)
    },
    "update_stock": {
        "summary": "Cập nhật tồn kho",
        "description": "Cập nhật số lượng tồn kho",
        "value": ProductUpdateInput(
            stock=100
        ).dict(exclude_unset=True)
    },
    "activate_product": {
        "summary": "Kích hoạt sản phẩm",
        "description": "Chuyển sản phẩm từ draft sang active",
        "value": ProductUpdateInput(
            status="active"
        ).dict(exclude_unset=True)
    }
}

PRODUCT_LIST_EXAMPLES = {
    "all_products": {
        "summary": "Tất cả sản phẩm",
        "description": "Lấy tất cả sản phẩm",
        "value": ProductListInput().dict()
    },
    "by_category": {
        "summary": "Theo category",
        "description": "Lấy sản phẩm theo category",
        "value": ProductListInput(
            category_id=1
        ).dict()
    },
    "featured_products": {
        "summary": "Sản phẩm nổi bật",
        "description": "Lấy sản phẩm nổi bật",
        "value": ProductListInput(
            featured=True
        ).dict()
    },
    "price_range": {
        "summary": "Theo khoảng giá",
        "description": "Lấy sản phẩm trong khoảng giá",
        "value": ProductListInput(
            min_price=1000000,
            max_price=5000000
        ).dict()
    },
    "search": {
        "summary": "Tìm kiếm",
        "description": "Tìm kiếm sản phẩm",
        "value": ProductListInput(
            search="iPhone"
        ).dict()
    }
}

PRODUCT_OUTPUT_EXAMPLE = ProductOutput(
    id=1,
    name="iPhone 15 Pro",
    slug="iphone-15-pro",
    description="iPhone 15 Pro với chip A17 Pro mạnh mẽ",
    short_description="iPhone 15 Pro - Hiệu năng vượt trội",
    sku="IPH15P-256",
    price=29990000,
    compare_price=32990000,
    cost=25000000,
    weight=0.187,
    dimensions="14.67 x 7.15 x 0.83 cm",
    stock=50,
    track_stock=True,
    allow_backorder=False,
    status="active",
    featured=True,
    tags='["smartphone", "apple", "premium"]',
    seo_title="iPhone 15 Pro - Mua ngay tại cửa hàng",
    seo_description="iPhone 15 Pro với chip A17 Pro, camera 48MP, pin lâu. Giao hàng miễn phí.",
    category_id=1,
    category=CategoryOutput(
        id=1,
        name="Điện thoại",
        slug="dien-thoai"
    ),
    created_at="2024-01-01T00:00:00Z",
    updated_at="2024-01-01T00:00:00Z"
).dict()
