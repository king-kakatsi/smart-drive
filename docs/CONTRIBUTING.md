# Contributing Guide

Welcome to Smart-Drive! This guide explains how to contribute to the project, from setting up your development environment to submitting your first pull request.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style & Standards](#code-style--standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Documentation](#documentation)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- **Be respectful**: Treat all contributors with respect and kindness
- **Be inclusive**: Welcome contributors from all backgrounds and skill levels
- **Be collaborative**: Work together to improve the project
- **Be patient**: Understand that contributors have different schedules and expertise levels
- **Be constructive**: Provide helpful feedback and focus on solutions

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- Python 3.12 or higher
- Node.js 20.x or higher
- Git
- Docker & Docker Compose (recommended)
- Visual Studio Code with recommended extensions

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
   # Then clone your fork
   git clone https://github.com/your-username/smart-drive.git
   cd smart-drive

   # Add upstream remote
   git remote add upstream https://github.com/original-owner/smart-drive.git
   ```

2. **Install Dependencies**
   ```bash
   # Install all dependencies (backend, frontend, development tools)
   make setup-dev

   # Or manually:
   # Backend
   cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

   # Frontend
   cd frontend && npm install
   ```

3. **Configure Environment**
   ```bash
   # Copy environment templates
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env

   # Edit with your API keys (optional for basic development)
   # For full functionality, get API keys from:
   # - Groq: https://console.groq.com/
   # - Google Drive: https://console.cloud.google.com/
   ```

4. **Run Development Servers**
   ```bash
   # Start all services
   make dev

   # Or manually in separate terminals:
   # Terminal 1: Backend
   cd backend && source venv/bin/activate && python run.py

   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

5. **Verify Setup**
   ```bash
   # Check services are running
   curl http://localhost:8000/health  # Backend
   curl http://localhost:5173         # Frontend
   ```

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.isort",
    "Vue.volar",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-eslint",
    "ms-vscode.vscode-json",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-docker",
    "ms-vscode.vscode-yaml",
    "GitHub.copilot"
  ]
}
```

## Development Workflow

### Branching Strategy

We use a simplified Git Flow with the following branches:

```
main (production) ──┐
                    ├── feature/feature-name
                    ├── bugfix/bug-description
                    ├── hotfix/critical-fix
                    └── refactor/refactor-description
```

#### Branch Naming Convention

- **Features**: `feature/description-of-feature`
- **Bug Fixes**: `bugfix/description-of-bug`
- **Hotfixes**: `hotfix/critical-fix-description`
- **Refactors**: `refactor/description-of-refactor`

### Development Process

1. **Choose an Issue**
   - Check the [GitHub Issues](https://github.com/your-repo/smart-drive/issues) for open tasks
   - Comment on the issue to indicate you're working on it
   - If no suitable issue exists, create one describing the feature/bug

2. **Create Feature Branch**
   ```bash
   # Update main branch
   git checkout main
   git pull upstream main

   # Create and switch to feature branch
   git checkout -b feature/your-feature-name
   ```

3. **Develop Your Changes**
   - Write clean, well-documented code
   - Follow the code style guidelines (see below)
   - Write tests for new functionality
   - Test your changes thoroughly
   - Commit regularly with clear messages

4. **Test Your Changes**
   ```bash
   # Run all tests
   make test

   # Run backend tests only
   make test-backend

   # Run frontend tests only
   make test-frontend

   # Run integration tests
   make test-integration
   ```

5. **Update Documentation**
   - Update any relevant documentation
   - Add docstrings to new functions
   - Update API documentation if endpoints changed

6. **Commit Your Changes**
   ```bash
   # Stage your changes
   git add .

   # Commit with conventional format
   git commit -m "feat: add amazing new feature

   - Add feature X that does Y
   - Improve performance by Z%
   - Fix issue with edge case W

   Closes #123"
   ```

### Commit Message Convention

We follow the [Angular commit convention](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit):

```
type(scope): subject

body (optional)

footer (optional)
```

#### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples
```
feat(auth): add Google OAuth2 integration

- Implement OAuth2 flow for Google Drive
- Add token refresh mechanism
- Store tokens securely in database

Closes #45

feat(ui): improve file upload experience

- Add drag-and-drop functionality
- Show upload progress with progress bars
- Add file validation feedback

BREAKING CHANGE: File upload API now requires content-type header
```

## Code Style & Standards

### Backend (Python)

#### Code Formatting
We use Black for code formatting:

```bash
# Format code
black backend/app/

# Check formatting (CI)
black --check backend/app/
```

#### Import Sorting
We use isort for import organization:

```bash
# Sort imports
isort backend/app/

# Check imports (CI)
isort --check-only backend/app/
```

#### Linting
We use flake8 for code quality:

```bash
# Check code quality
flake8 backend/app/
```

#### Type Hints
All new code should include type hints:

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class FileService:
    async def upload_file(self, file: UploadFile, user_id: str) -> FileResponse:
        """Upload and process a file.

        Args:
            file: The uploaded file
            user_id: ID of the uploading user

        Returns:
            FileResponse: Details of the uploaded file
        """
        pass
```

### Frontend (JavaScript/Vue)

#### Code Formatting
We use Prettier for consistent formatting:

```bash
# Format code
cd frontend && npm run format

# Check formatting (CI)
npm run format:check
```

#### Linting
We use ESLint for code quality:

```bash
# Check code quality
npm run lint

# Fix auto-fixable issues
npm run lint:fix
```

#### Vue.js Best Practices

```vue
<!-- Good: Clear component structure -->
<template>
  <div class="file-card">
    <div class="file-header">
      <h3>{{ file.name }}</h3>
      <span class="file-size">{{ formatSize(file.size) }}</span>
    </div>
    <div class="file-actions">
      <button @click="downloadFile" class="btn-primary">
        Download
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Good: Clear composition function naming
const props = defineProps({
  file: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['download'])

// Good: Descriptive computed properties
const fileExtension = computed(() => {
  return props.file.name.split('.').pop().toLowerCase()
})

// Good: Clear function names and single responsibility
const formatSize = (bytes) => {
  // Implementation
}

const downloadFile = () => {
  emit('download', props.file.id)
}
</script>

<style scoped>
/* Good: Scoped styles, consistent naming */
.file-card {
  /* Styles */
}
</style>
```

### General Code Standards

#### Documentation
All public functions, classes, and modules must have docstrings/documentation:

```python
# Good: Comprehensive docstring
def process_document(file_path: str, user_id: str) -> Dict[str, Any]:
    """Process a document file and extract text content.

    This function handles PDF, DOCX, and TXT files, extracting
    text content and preparing it for vector embedding.

    Args:
        file_path: Path to the file to process
        user_id: ID of the user who uploaded the file

    Returns:
        Dict containing:
        - content: Extracted text content
        - metadata: File metadata (pages, word count, etc.)
        - chunks: Text chunks for embedding

    Raises:
        FileProcessingError: If file cannot be processed
        UnsupportedFileTypeError: If file type is not supported

    Example:
        >>> result = process_document("document.pdf", "user123")
        >>> print(result["content"][:100])
        'This is the beginning of the document...'
    """
    pass
```

#### Error Handling
Implement proper error handling with custom exceptions:

```python
# backend/app/core/exceptions.py
class SmartDriveError(Exception):
    """Base exception for Smart-Drive."""
    pass

class FileProcessingError(SmartDriveError):
    """Raised when file processing fails."""
    pass

class AuthenticationError(SmartDriveError):
    """Raised when authentication fails."""
    pass

# Usage
def process_file(file_path: str):
    try:
        # Processing logic
        if not file_exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        result = extract_text(file_path)
        return result

    except FileNotFoundError as e:
        logger.error(f"File processing failed: {e}")
        raise FileProcessingError("Could not access file") from e
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise FileProcessingError("File processing failed") from e
```

#### Logging
Use structured logging with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

def upload_file(file: UploadFile, user_id: str):
    logger.info("Starting file upload", extra={
        "user_id": user_id,
        "filename": file.filename,
        "file_size": file.size
    })

    try:
        # Upload logic
        result = save_file(file, user_id)

        logger.info("File upload successful", extra={
            "user_id": user_id,
            "file_id": result.id,
            "processing_time": time.time() - start_time
        })

        return result

    except Exception as e:
        logger.error("File upload failed", extra={
            "user_id": user_id,
            "filename": file.filename,
            "error": str(e)
        })
        raise
```

## Testing

### Testing Strategy

We follow a comprehensive testing strategy:

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user workflows
4. **Performance Tests**: Test system performance under load

### Backend Testing

```python
# backend/tests/test_file_service.py
import pytest
from unittest.mock import Mock, patch
from app.services.file_service import FileService
from app.core.exceptions import FileProcessingError

class TestFileService:
    @pytest.fixture
    def file_service(self):
        return FileService()

    @pytest.fixture
    def mock_file(self):
        mock = Mock()
        mock.filename = "test.pdf"
        mock.content_type = "application/pdf"
        return mock

    def test_upload_valid_file(self, file_service, mock_file):
        """Test successful file upload."""
        with patch('app.services.file_service.save_file') as mock_save:
            mock_save.return_value = "/uploads/test.pdf"

            result = file_service.upload_file(mock_file, "user123")

            assert result.filename == "test.pdf"
            assert result.user_id == "user123"
            mock_save.assert_called_once()

    def test_upload_unsupported_file_type(self, file_service):
        """Test upload rejection for unsupported file types."""
        mock_file = Mock()
        mock_file.filename = "test.exe"
        mock_file.content_type = "application/x-msdownload"

        with pytest.raises(FileProcessingError, match="Unsupported file type"):
            file_service.upload_file(mock_file, "user123")

    @pytest.mark.asyncio
    async def test_process_file_with_ai(self, file_service):
        """Test file processing with AI integration."""
        # Test implementation
        pass
```

### Frontend Testing

```javascript
// frontend/src/components/__tests__/FileCard.test.js
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FileCard from '../FileCard.vue'

describe('FileCard', () => {
  const mockFile = {
    id: '123',
    name: 'document.pdf',
    size: 1024000,
    uploadDate: '2024-01-15T10:00:00Z'
  }

  it('renders file information correctly', () => {
    const wrapper = mount(FileCard, {
      props: { file: mockFile }
    })

    expect(wrapper.text()).toContain('document.pdf')
    expect(wrapper.text()).toContain('976 KB') // Formatted size
  })

  it('emits download event when download button is clicked', async () => {
    const wrapper = mount(FileCard, {
      props: { file: mockFile }
    })

    await wrapper.find('.download-btn').trigger('click')

    expect(wrapper.emitted()).toHaveProperty('download')
    expect(wrapper.emitted('download')[0]).toEqual(['123'])
  })

  it('shows processing indicator for new files', () => {
    const processingFile = { ...mockFile, status: 'processing' }
    const wrapper = mount(FileCard, {
      props: { file: processingFile }
    })

    expect(wrapper.find('.processing-indicator').exists()).toBe(true)
  })
})
```

### Running Tests

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Run with coverage
make test-coverage

# Run specific test file
pytest backend/tests/test_file_service.py -v

# Run frontend tests in watch mode
cd frontend && npm run test:watch
```

### Test Coverage

We aim for high test coverage:

```bash
# Backend coverage
coverage run -m pytest
coverage report --fail-under=85
coverage html  # Generate HTML report

# Frontend coverage
npm run test:coverage
```

## Submitting Changes

### Pull Request Process

1. **Ensure your branch is up to date**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run the full test suite**
   ```bash
   make test
   make lint
   ```

3. **Update documentation if needed**
   ```bash
   # Update any relevant docs
   # Add API documentation for new endpoints
   ```

4. **Create the pull request**
   - Go to GitHub and create a new Pull Request
   - Use a clear, descriptive title
   - Fill out the PR template completely
   - Reference any related issues

5. **PR Template**
   ```markdown
   ## Description
   Brief description of the changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing completed
   - [ ] All tests pass

   ## Screenshots (if applicable)
   Add screenshots of UI changes

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] Tests added for new functionality
   - [ ] All CI checks pass
   - [ ] Reviewed by at least one maintainer
   ```

### Code Review Process

1. **Automated Checks**
   - CI/CD pipeline runs automatically
   - Code formatting, linting, and tests are checked
   - Security scans are performed

2. **Peer Review**
   - At least one maintainer reviews the code
   - Review focuses on:
     - Code quality and style
     - Test coverage
     - Documentation
     - Security implications
     - Performance impact

3. **Review Feedback**
   - Address all review comments
   - Make requested changes or provide justification for not making them
   - Keep discussions civil and constructive

4. **Approval and Merge**
   - PR is approved by reviewer(s)
   - CI checks must pass
   - Squash and merge using the PR title as commit message
   - Delete the feature branch

## Reporting Issues

### Bug Reports

When reporting bugs, please provide:

1. **Clear title** describing the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **Environment information**:
   - OS and version
   - Browser and version (for frontend issues)
   - Python/Node.js versions
   - Docker version (if applicable)
5. **Error messages** and stack traces
6. **Screenshots** if applicable
7. **Additional context** (when the issue occurs, frequency, etc.)

### Feature Requests

For new features, please provide:

1. **Clear description** of the proposed feature
2. **Use case** and problem it solves
3. **Proposed solution** or implementation approach
4. **Alternatives considered** (if any)
5. **Additional context** or mockups

### Security Issues

For security vulnerabilities:

- **DO NOT** create a public GitHub issue
- Email security@smart-drive.com directly
- Provide detailed information about the vulnerability
- Allow time for the issue to be investigated and fixed before public disclosure

## Documentation

### Documentation Standards

All documentation should be:

- **Clear and concise**: Use simple language, avoid jargon
- **Comprehensive**: Cover all aspects of the feature
- **Up-to-date**: Update when code changes
- **Well-structured**: Use consistent formatting and organization

### API Documentation

API endpoints must be documented using OpenAPI/Swagger:

```python
# backend/app/routers/files.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter()

@router.post(
    "/upload",
    response_model=FileResponse,
    summary="Upload a file",
    description="Upload a file for processing and AI analysis. Supports PDF, DOCX, TXT, MP4, and other formats.",
    response_description="Details of the uploaded file including processing status"
)
async def upload_file(
    file: UploadFile = File(..., description="The file to upload"),
    user_id: str = Query(..., description="ID of the user uploading the file")
) -> FileResponse:
    """
    Upload and process a file.

    This endpoint:
    - Validates file type and size
    - Saves the file securely
    - Starts background processing for AI analysis
    - Returns file metadata and processing status

    **Supported file types:**
    - Documents: PDF, DOCX, TXT
    - Videos: MP4, AVI, WEBM
    - Images: JPG, PNG, GIF

    **File size limit:** 10MB
    """
    # Implementation
    pass
```

### Updating Documentation

When making changes that affect documentation:

1. Update relevant `.md` files in the `docs/` directory
2. Update docstrings in code
3. Update API documentation
4. Test that documentation builds correctly
5. Ensure all links work

## Getting Help

### Communication Channels

- **GitHub Issues**: For bugs, features, and general discussion
- **GitHub Discussions**: For questions and community discussion
- **Documentation**: Check docs first for common questions

### Asking Good Questions

When asking for help:

1. **Search first**: Check if the question has been asked before
2. **Be specific**: Provide detailed information about your problem
3. **Include context**: Mention what you're trying to accomplish
4. **Show your work**: Include code snippets, error messages, etc.
5. **Be patient**: Allow time for community members to respond

### Example Good Question

```
Subject: File upload failing with "Unsupported file type" error

I'm trying to upload a PDF file but getting an "Unsupported file type" error.
I've confirmed the file is a valid PDF (created with Adobe Acrobat).

Environment:
- Smart-Drive version: v1.0.0
- Browser: Chrome 120.0.6099.109
- OS: macOS Sonoma 14.1

Steps to reproduce:
1. Go to Files page
2. Click "Upload"
3. Select a PDF file
4. Click "Upload"
5. Error appears: "Unsupported file type"

Expected behavior: File should upload successfully

Additional context: This worked last week. No recent changes to my setup.
```

## Recognition

Contributors are recognized in several ways:

- **GitHub Contributors**: Listed in repository contributors
- **Changelog**: Mentioned in release changelogs
- **Credits**: Special recognition for major contributions
- **Community**: Access to contributor-only channels

## License

By contributing to Smart-Drive, you agree that your contributions will be licensed under the same MIT License that covers the project.

Thank you for contributing to Smart-Drive! Your help makes the project better for everyone.
