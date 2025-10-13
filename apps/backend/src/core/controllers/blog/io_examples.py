from core.controllers.blog.io import (
    PostCreateInput,
    PostUpdateInput,
    PostListInput,
    PostOutput,
    TagCreateInput,
    TagUpdateInput,
    TagOutput,
    AuthorOutput,
    CategoryOutput
)

# Examples for API documentation
POST_CREATE_EXAMPLES = {
    "basic_post": {
        "summary": "Bài viết cơ bản",
        "description": "Tạo bài viết với thông tin cơ bản",
        "value": PostCreateInput(
            title="Hướng dẫn lập trình Python",
            slug="huong-dan-lap-trinh-python",
            content="<h1>Giới thiệu Python</h1><p>Python là một ngôn ngữ lập trình...</p>",
            excerpt="Hướng dẫn cơ bản về lập trình Python cho người mới bắt đầu",
            featured_image="https://example.com/python-tutorial.jpg",
            status="draft",
            category_id=1,
            tag_ids=[1, 2],
            seo_title="Hướng dẫn lập trình Python - Từ cơ bản đến nâng cao",
            seo_description="Học lập trình Python từ cơ bản với các bài tập thực hành",
            seo_keywords="python, lập trình, tutorial, học code"
        ).dict()
    },
    "published_post": {
        "summary": "Bài viết đã xuất bản",
        "description": "Tạo bài viết và xuất bản ngay",
        "value": PostCreateInput(
            title="Top 10 Framework JavaScript 2024",
            slug="top-10-framework-javascript-2024",
            content="<h1>Top 10 Framework JavaScript</h1><p>React, Vue, Angular...</p>",
            excerpt="Danh sách các framework JavaScript phổ biến nhất năm 2024",
            featured_image="https://example.com/js-frameworks.jpg",
            status="published",
            published_at="2024-01-01T10:00:00Z",
            category_id=2,
            tag_ids=[3, 4],
            seo_title="Top 10 Framework JavaScript 2024 - So sánh chi tiết",
            seo_description="Tổng hợp các framework JavaScript tốt nhất năm 2024",
            seo_keywords="javascript, framework, react, vue, angular"
        ).dict()
    }
}

POST_UPDATE_EXAMPLES = {
    "update_content": {
        "summary": "Cập nhật nội dung",
        "description": "Cập nhật nội dung bài viết",
        "value": PostUpdateInput(
            content="<h1>Giới thiệu Python</h1><p>Python là một ngôn ngữ lập trình mạnh mẽ...</p>"
        ).dict(exclude_unset=True)
    },
    "publish_post": {
        "summary": "Xuất bản bài viết",
        "description": "Chuyển bài viết từ draft sang published",
        "value": PostUpdateInput(
            status="published",
            published_at="2024-01-01T10:00:00Z"
        ).dict(exclude_unset=True)
    },
    "update_tags": {
        "summary": "Cập nhật tags",
        "description": "Thay đổi tags của bài viết",
        "value": PostUpdateInput(
            tag_ids=[1, 3, 5]
        ).dict(exclude_unset=True)
    }
}

POST_LIST_EXAMPLES = {
    "all_posts": {
        "summary": "Tất cả bài viết",
        "description": "Lấy tất cả bài viết",
        "value": PostListInput().dict()
    },
    "by_category": {
        "summary": "Theo category",
        "description": "Lấy bài viết theo category",
        "value": PostListInput(
            category_id=1
        ).dict()
    },
    "published_posts": {
        "summary": "Bài viết đã xuất bản",
        "description": "Lấy chỉ bài viết đã xuất bản",
        "value": PostListInput(
            status="published"
        ).dict()
    },
    "search": {
        "summary": "Tìm kiếm",
        "description": "Tìm kiếm bài viết",
        "value": PostListInput(
            search="Python"
        ).dict()
    }
}

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
    }
}

POST_OUTPUT_EXAMPLE = PostOutput(
    id=1,
    title="Hướng dẫn lập trình Python",
    slug="huong-dan-lap-trinh-python",
    content="<h1>Giới thiệu Python</h1><p>Python là một ngôn ngữ lập trình...</p>",
    excerpt="Hướng dẫn cơ bản về lập trình Python cho người mới bắt đầu",
    featured_image="https://example.com/python-tutorial.jpg",
    status="published",
    published_at="2024-01-01T10:00:00Z",
    author_id=1,
    author=AuthorOutput(
        id=1,
        name="Admin User",
        email="admin@example.com"
    ),
    category_id=1,
    category=CategoryOutput(
        id=1,
        name="Lập trình",
        slug="lap-trinh"
    ),
    tags=[
        TagOutput(
            id=1,
            name="Python",
            slug="python",
            description="Ngôn ngữ lập trình Python",
            color="#3776ab",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        ),
        TagOutput(
            id=2,
            name="Tutorial",
            slug="tutorial",
            description="Hướng dẫn học tập",
            color="#28a745",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
    ],
    seo_title="Hướng dẫn lập trình Python - Từ cơ bản đến nâng cao",
    seo_description="Học lập trình Python từ cơ bản với các bài tập thực hành",
    seo_keywords="python, lập trình, tutorial, học code",
    view_count=150,
    like_count=25,
    created_at="2024-01-01T00:00:00Z",
    updated_at="2024-01-01T00:00:00Z"
).dict()

TAG_OUTPUT_EXAMPLE = TagOutput(
    id=1,
    name="Python",
    slug="python",
    description="Ngôn ngữ lập trình Python",
    color="#3776ab",
    created_at="2024-01-01T00:00:00Z",
    updated_at="2024-01-01T00:00:00Z"
).dict()
