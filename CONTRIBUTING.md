# 贡献指南

感谢您对文档提取工具的关注！欢迎贡献代码、报告问题或提出建议。

## 贡献方式

### 1. 报告问题

如果您发现了 Bug，请通过以下方式报告：

1. 使用 GitHub Issues
2. 提供详细的问题描述
3. 包含复现步骤
4. 附上错误信息截图（如果有）
5. 提供您的环境信息（操作系统、Python 版本等）

### 2. 功能建议

欢迎提出新功能的建议：

1. 创建新的 Issue
2. 详细描述功能需求
3. 说明使用场景
4. 可以的话提供实现方案

### 3. 代码贡献

#### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/YukiAsuna19990413/Claude-Document-Extractor.git
cd Claude-Document-Extractor

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e .[dev]
```

#### 代码规范

- 使用 Black 进行代码格式化
- 遵循 PEP 8 规范
- 添加适当的类型注解
- 编写清晰的注释和文档字符串

```bash
# 格式化代码
black src/

# 检查代码质量
flake8 src/

# 类型检查
mypy src/
```

#### 测试

- 新功能必须包含测试
- 确保所有测试通过
- 保持测试覆盖率

```bash
# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=src tests/
```

#### 提交规范

使用 conventional commits 规范：

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式化
refactor: 重构
test: 测试相关
chore: 构建或工具变动
```

示例：
```bash
git commit -m "feat: 添加新的 OCR 提供商支持"
git commit -m "fix: 修复滚动检测的边界情况"
git commit -m "docs: 更新安装说明"
```

## 分支管理

### 主分支

- `main` - 主分支，稳定版本
- `develop` - 开发分支，最新开发版本

### 功能分支

创建功能分支进行开发：

```bash
# 从 develop 分支创建功能分支
git checkout develop
git checkout -b feature/feature-name

# 开发完成后提交
git add .
git commit -m "feat: 添加新功能"
git push origin feature/feature-name

# 创建 Pull Request
```

## 代码审查

所有代码变更需要经过审查：

1. 确保代码符合项目规范
2. 检查测试覆盖率
3. 验证功能正常工作
4. 更新相关文档

## 文档贡献

文档与代码同样重要：

- API 文档要及时更新
- 使用说明要清晰易懂
- 示例代码要正确可用

## 发布流程

1. 版本号遵循语义化版本（SemVer）
2. 更新 CHANGELOG.md
3. 创建标签
4. 发布到 PyPI

## 行为准则

- 保持尊重和友善
- 关注技术讨论
- 欢迎新手参与
- 分享知识经验

## 常见问题

### 如何开始贡献？

1. 从简单的问题开始（标签 good first issue）
2. 阅读现有代码和文档
3. 在 develop 分支上开发
4. 提交 Pull Request

### 提交后如何修改？

如果需要根据审查意见修改：

```bash
# 在原分支上继续修改
git add .
git commit -m "fix: 根据审查意见修改"

# 推送到同一个分支
git push origin feature/feature-name
```

### 如何获得帮助？

- 在 Issue 中提问
- 查看 Wiki 文档
- 加入讨论群组（如果有）

感谢您的贡献！🎉