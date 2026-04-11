# File Uploads Directory

This directory is the **default location** for test file uploads. Place your test files here for easy management and CI/CD pipeline integration.

## 📁 Directory Structure

Organize files by module/feature for better maintainability:

```
src/resources/uploads/
├── auth/
│   ├── profile_photo.jpg
│   └── id_document.pdf
├── documents/
│   ├── contract.pdf
│   ├── invoice.xlsx
│   └── report.docx
├── images/
│   ├── banner.png
│   └── logo.svg
└── general/
    └── sample.txt
```

## 🚀 Usage in Tests

When recording tests with file uploads, you can use:

### **Option 1: Filename Only (Recommended)**
Just specify the filename if the file is in `src/resources/uploads/`:
```
file.pdf
```

### **Option 2: Module Subdirectory**
Organize by module and use relative path:
```
documents/contract.pdf
auth/profile_photo.jpg
```

### **Option 3: Relative Path**
Use relative path from `src/resources/`:
```
uploads/documents/contract.pdf
```

### **Option 4: Absolute Path**
Use full system path (less portable):
```
C:\Users\YourName\Downloads\file.pdf
```

## 💡 Best Practices

1. **Use Module Subdirectories**: Organize files by feature/module (e.g., `auth/`, `documents/`)
2. **Keep Files Small**: Use sample/test files, not production data
3. **Version Control**: Commit test files to git for consistent CI/CD runs
4. **Naming Convention**: Use descriptive names (e.g., `valid_resume.pdf`, `invalid_image.txt`)
5. **Clean Up**: Remove unused test files periodically

## 🔧 CI/CD Integration

This directory structure ensures:
- ✅ Consistent file paths across environments
- ✅ No hardcoded absolute paths
- ✅ Easy setup in Docker containers
- ✅ Portable across team members' machines
- ✅ Works in CI/CD pipelines without modification

## 📝 Example

**Recording a test:**
1. Place `resume.pdf` in `src/resources/uploads/documents/`
2. When prompted for file path, enter: `documents/resume.pdf`
3. The system automatically resolves to: `[PROJECT_ROOT]/src/resources/uploads/documents/resume.pdf`

**Multiple files:**
```
documents/file1.pdf
documents/file2.pdf
images/photo.jpg
```

## 🛠️ Path Resolution Order

The system checks paths in this order:
1. `src/resources/uploads/[your-path]` ← **Default**
2. `src/resources/[your-path]`
3. `[project-root]/[your-path]`
4. Absolute path as-is

This smart resolution makes your tests portable and maintainable! 🎉
