from core.controllers.category.io import (
    CategoryCreateInput,
    CategoryUpdateInput,
    CategoryListInput,
    CategoryOutput,
    CategoryTreeOutput
)

# Examples for API documentation
CATEGORY_CREATE_EXAMPLES = {
    "root_category": {
        "summary": "Tạo root category",
        "description": "Tạo category gốc không có parent",
        "value": CategoryCreateInput(
            name="Điện tử",
            slug="dien-tu",
            description="Các sản phẩm điện tử",
            image="https://example.com/electronics.jpg",
            order=1,
            is_active=True,
            parent_id=None
        ).dict()
    },
    "child_category": {
        "summary": "Tạo child category",
        "description": "Tạo category con",
        "value": CategoryCreateInput(
            name="Điện thoại",
            slug="dien-thoai",
            description="Các loại điện thoại",
            image="https://example.com/phones.jpg",
            order=1,
            is_active=True,
            parent_id=1
        ).dict()
    }
}

CATEGORY_UPDATE_EXAMPLES = {
    "update_name": {
        "summary": "Cập nhật tên",
        "description": "Chỉ cập nhật tên category",
        "value": CategoryUpdateInput(
            name="Điện tử - Cập nhật"
        ).dict(exclude_unset=True)
    },
    "update_parent": {
        "summary": "Thay đổi parent",
        "description": "Di chuyển category sang parent khác",
        "value": CategoryUpdateInput(
            parent_id=2
        ).dict(exclude_unset=True)
    },
    "deactivate": {
        "summary": "Vô hiệu hóa",
        "description": "Vô hiệu hóa category",
        "value": CategoryUpdateInput(
            is_active=False
        ).dict(exclude_unset=True)
    }
}

CATEGORY_LIST_EXAMPLES = {
    "all_categories": {
        "summary": "Tất cả categories",
        "description": "Lấy tất cả categories",
        "value": CategoryListInput().dict()
    },
    "root_only": {
        "summary": "Chỉ root categories",
        "description": "Lấy chỉ các root categories",
        "value": CategoryListInput(
            only_root=True
        ).dict()
    },
    "by_parent": {
        "summary": "Theo parent",
        "description": "Lấy categories theo parent ID",
        "value": CategoryListInput(
            parent_id=1
        ).dict()
    },
    "active_only": {
        "summary": "Chỉ active",
        "description": "Lấy chỉ các categories đang hoạt động",
        "value": CategoryListInput(
            is_active=True
        ).dict()
    }
}

CATEGORY_OUTPUT_EXAMPLE = CategoryOutput(
    id=1,
    name="Điện tử",
    slug="dien-tu",
    description="Các sản phẩm điện tử",
    image="https://example.com/electronics.jpg",
    order=1,
    is_active=True,
    parent_id=None,
    parent=None,
    children=[
        CategoryOutput(
            id=2,
            name="Điện thoại",
            slug="dien-thoai",
            description="Các loại điện thoại",
            image="https://example.com/phones.jpg",
            order=1,
            is_active=True,
            parent_id=1,
            parent=None,
            children=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
    ],
    created_at="2024-01-01T00:00:00Z",
    updated_at="2024-01-01T00:00:00Z"
).dict()

CATEGORY_TREE_EXAMPLE = [
    CategoryTreeOutput(
        id=1,
        name="Điện tử",
        slug="dien-tu",
        description="Các sản phẩm điện tử",
        image="https://example.com/electronics.jpg",
        order=1,
        is_active=True,
        parent_id=None,
        children=[
            CategoryTreeOutput(
                id=2,
                name="Điện thoại",
                slug="dien-thoai",
                description="Các loại điện thoại",
                image="https://example.com/phones.jpg",
                order=1,
                is_active=True,
                parent_id=1,
                children=[
                    CategoryTreeOutput(
                        id=3,
                        name="iPhone",
                        slug="iphone",
                        description="Điện thoại iPhone",
                        image="https://example.com/iphone.jpg",
                        order=1,
                        is_active=True,
                        parent_id=2,
                        children=[],
                        created_at="2024-01-01T00:00:00Z",
                        updated_at="2024-01-01T00:00:00Z"
                    )
                ],
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )
        ],
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )
]
