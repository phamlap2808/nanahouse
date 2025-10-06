# Test Suite Documentation

Bộ test suite hoàn chỉnh cho ứng dụng FastAPI với RBAC (Role-Based Access Control).

## Cấu trúc Test

```
tests/
├── conftest.py              # Test configuration và fixtures
├── test_utils.py            # Test utilities và helper functions
├── test_health.py           # Test cho health endpoint
├── test_auth_api.py         # Test cho Auth API
├── test_users_api.py        # Test cho Users API
├── test_test_api.py         # Test cho Test API
├── test_rbac_api.py         # Test cho RBAC APIs (Groups, Roles, Permissions)
└── test_integration.py      # Integration và End-to-End tests
```

## Các loại Test

### 1. Unit Tests
- **test_auth_api.py**: Test các endpoint authentication
- **test_users_api.py**: Test các endpoint quản lý users
- **test_test_api.py**: Test các endpoint test/health
- **test_rbac_api.py**: Test các endpoint RBAC

### 2. Integration Tests
- **test_integration.py**: Test tích hợp giữa các components
- Test complete workflows
- Test data consistency
- Test error handling
- Test performance
- Test security

### 3. Test Utilities
- **conftest.py**: Pytest fixtures và configuration
- **test_utils.py**: Helper functions và test data factories

## Fixtures có sẵn

### Database Fixtures
- `test_db`: Database connection cho test session
- `clean_db`: Clean database trước mỗi test

### User Fixtures
- `test_user`: Regular user
- `test_admin_user`: Admin user
- `sample_user_data`: Sample user data

### RBAC Fixtures
- `test_group`: Test group
- `test_role`: Test role
- `test_permission`: Test permission
- `sample_group_data`: Sample group data
- `sample_role_data`: Sample role data
- `sample_permission_data`: Sample permission data

### Utility Fixtures
- `client`: FastAPI test client
- `auth_headers`: Function để tạo auth headers
- `test_utils`: TestUtils class
- `test_data_factory`: TestDataFactory class

## Cách chạy Tests

### Chạy tất cả tests
```bash
pytest
```

### Chạy tests theo category
```bash
# Chỉ unit tests
pytest -m unit

# Chỉ integration tests
pytest -m integration

# Chỉ auth tests
pytest -m auth

# Chỉ RBAC tests
pytest -m rbac
```

### Chạy tests theo file
```bash
# Test Auth API
pytest tests/test_auth_api.py

# Test Users API
pytest tests/test_users_api.py

# Test RBAC API
pytest tests/test_rbac_api.py

# Test Integration
pytest tests/test_integration.py
```

### Chạy tests với verbose output
```bash
pytest -v
```

### Chạy tests và hiển thị coverage
```bash
pytest --cov=src
```

## Test Cases Coverage

### Auth API Tests
- ✅ User registration (success, duplicate email, invalid data)
- ✅ User login (success, invalid credentials, inactive user)
- ✅ Get current user info (success, invalid token, no token)
- ✅ Update current user info (success, no changes, invalid token)

### Users API Tests
- ✅ List users (success, no auth)
- ✅ Create user (success, duplicate email, invalid data, no auth)
- ✅ Get user (success, not found, no auth)
- ✅ Delete user (success, not found, no auth)
- ✅ RBAC integration (group_id, is_admin)

### Test API Tests
- ✅ Health endpoint (success, no auth required)
- ✅ HTTP methods validation
- ✅ Response format validation
- ✅ Multiple calls
- ✅ Headers và query params

### RBAC API Tests
- ✅ Group management (CRUD operations)
- ✅ Role management (CRUD operations)
- ✅ Permission management (CRUD operations)
- ✅ User-Group assignments
- ✅ Group-Role assignments
- ✅ Role-Permission assignments
- ✅ Complete RBAC flow
- ✅ Admin vs non-admin permissions

### Integration Tests
- ✅ Complete user lifecycle
- ✅ Complete RBAC lifecycle
- ✅ Authentication flow
- ✅ Error handling
- ✅ Data consistency
- ✅ Performance testing
- ✅ Security testing

## Test Utilities

### TestUtils Class
- `create_auth_headers()`: Tạo auth headers
- `create_test_user()`: Tạo test user
- `create_test_group()`: Tạo test group
- `create_test_role()`: Tạo test role
- `create_test_permission()`: Tạo test permission
- `assign_user_to_group()`: Gán user vào group
- `assign_role_to_group()`: Gán role vào group
- `assign_permission_to_role()`: Gán permission vào role
- `setup_rbac_chain()`: Setup complete RBAC chain
- `assert_success_response()`: Assert success response
- `assert_error_response()`: Assert error response
- `assert_user_data()`: Assert user data structure
- `assert_group_data()`: Assert group data structure
- `assert_role_data()`: Assert role data structure
- `assert_permission_data()`: Assert permission data structure

### TestDataFactory Class
- `get_sample_user_data()`: Sample user data
- `get_sample_group_data()`: Sample group data
- `get_sample_role_data()`: Sample role data
- `get_sample_permission_data()`: Sample permission data
- `get_invalid_user_data()`: Invalid user data for testing
- `get_invalid_group_data()`: Invalid group data for testing
- `get_invalid_role_data()`: Invalid role data for testing
- `get_invalid_permission_data()`: Invalid permission data for testing

## Test Configuration

### pytest.ini
- Test discovery patterns
- Output formatting
- Markers definition
- Warning filters

### conftest.py
- Session-scoped fixtures
- Database setup/teardown
- RBAC initialization
- Test data creation

## Best Practices

### 1. Test Isolation
- Mỗi test độc lập
- Clean database trước mỗi test
- Không phụ thuộc vào thứ tự test

### 2. Test Data
- Sử dụng factories để tạo test data
- Sử dụng fixtures cho common data
- Clean up sau mỗi test

### 3. Assertions
- Assert cả status code và response data
- Sử dụng utility functions cho assertions
- Test cả success và error cases

### 4. Authentication
- Sử dụng fixtures cho auth headers
- Test cả authenticated và unauthenticated requests
- Test different user roles

### 5. Error Handling
- Test các error scenarios
- Assert error messages
- Test validation errors

## Debugging Tests

### Chạy test với debug output
```bash
pytest -v -s
```

### Chạy test cụ thể
```bash
pytest tests/test_auth_api.py::TestAuthAPI::test_register_success -v
```

### Chạy test với pdb
```bash
pytest --pdb
```

### Xem test coverage
```bash
pytest --cov=src --cov-report=html
```

## Continuous Integration

Tests được thiết kế để chạy trong CI/CD pipeline:

- Không cần external dependencies
- Sử dụng test database
- Parallel execution support
- Clear error messages
- Fast execution

## Maintenance

### Thêm test mới
1. Tạo test class trong file tương ứng
2. Sử dụng existing fixtures
3. Follow naming conventions
4. Add appropriate markers

### Cập nhật tests
1. Update khi API changes
2. Maintain test coverage
3. Update documentation
4. Review test performance

### Debugging failures
1. Check test isolation
2. Verify fixtures
3. Check database state
4. Review error messages
