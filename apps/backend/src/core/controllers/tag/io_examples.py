from core.controllers.tag.io import (
    TagCreateInput,
    TagUpdateInput,
    TagListInput,
    TagOutput,
    TagMergeInput,
    PostSummaryOutput
)

# Examples for API documentation
TAG_CREATE_EXAMPLES = {
    "basic_tag": {
        "summary": "Tag cơ bản",
        "description": "Tạo tag với thông tin cơ bản",
        "value": TagCreateInput(
            name="Python",
            slug="python",
            description="Ngôn ngữ lập trình Python",
            color="#3776ab"
        ).dict()
    },
    "tech_tag": {
        "summary": "Tag công nghệ",
        "description": "Tạo tag cho công nghệ",
        "value": TagCreateInput(
            name="JavaScript",
            slug="javascript",
            description="Ngôn ngữ lập trình JavaScript",
            color="#f7df1e"
        ).dict()
    },
    "design_tag": {
        "summary": "Tag thiết kế",
        "description": "Tạo tag cho thiết kế",
        "value": TagCreateInput(
            name="UI/UX",
            slug="ui-ux",
            description="Thiết kế giao diện người dùng",
            color="#ff6b6b"
        ).dict()
    }
}

TAG_UPDATE_EXAMPLES = {
    "update_color": {
        "summary": "Cập nhật màu",
        "description": "Thay đổi màu của tag",
        "value": TagUpdateInput(
            color="#ff6b6b"
        ).dict(exclude_unset=True)
    },
    "update_description": {
        "summary": "Cập nhật mô tả",
        "description": "Cập nhật mô tả tag",
        "value": TagUpdateInput(
            description="Ngôn ngữ lập trình Python - Dễ học, mạnh mẽ"
        ).dict(exclude_unset=True)
    },
    "update_name": {
        "summary": "Cập nhật tên",
        "description": "Thay đổi tên tag",
        "value": TagUpdateInput(
            name="Python Programming",
            slug="python-programming"
        ).dict(exclude_unset=True)
    }
}

TAG_LIST_EXAMPLES = {
    "all_tags": {
        "summary": "Tất cả tags",
        "description": "Lấy tất cả tags",
        "value": TagListInput().dict()
    },
    "search_tags": {
        "summary": "Tìm kiếm tags",
        "description": "Tìm kiếm tags theo tên hoặc mô tả",
        "value": TagListInput(
            search="python"
        ).dict()
    },
    "by_color": {
        "summary": "Theo màu",
        "description": "Lọc tags theo màu",
        "value": TagListInput(
            color="#3776ab"
        ).dict()
    },
    "pagination": {
        "summary": "Phân trang",
        "description": "Lấy tags với phân trang",
        "value": TagListInput(
            page=2,
            limit=10
        ).dict()
    }
}

TAG_OUTPUT_EXAMPLE = TagOutput(
    id=1,
    name="Python",
    slug="python",
    description="Ngôn ngữ lập trình Python",
    color="#3776ab",
    post_count=5,
    posts=[
        PostSummaryOutput(
            id=1,
            title="Hướng dẫn lập trình Python",
            slug="huong-dan-lap-trinh-python",
            excerpt="Hướng dẫn cơ bản về lập trình Python",
            featured_image="https://example.com/python-tutorial.jpg",
            status="published",
            published_at="2024-01-01T10:00:00Z",
            view_count=150,
            like_count=25,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        ),
        PostSummaryOutput(
            id=2,
            title="Python vs JavaScript",
            slug="python-vs-javascript",
            excerpt="So sánh Python và JavaScript",
            featured_image="https://example.com/python-vs-js.jpg",
            status="published",
            published_at="2024-01-02T10:00:00Z",
            view_count=200,
            like_count=30,
            created_at="2024-01-02T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z"
        )
    ],
    created_at="2024-01-01T00:00:00Z",
    updated_at="2024-01-01T00:00:00Z"
).dict()

TAG_MERGE_EXAMPLE = TagMergeInput(
    source_tag_id=1,
    target_tag_id=2
).dict()
