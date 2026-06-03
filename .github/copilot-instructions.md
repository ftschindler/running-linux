# GitHub Copilot Instructions

This repository contains Felix' personal notes on running Linux in various circumstances.
It is implemented as a MkDocs-based static site generator with Material for MkDocs theme and markdown content in the `docs/` directory.

## General Guidelines

This site relies on an interplay of many tools, and we can only make use of the subset of Markdown features that are supported by mkdocs, obsidian, markdownlint-cli2 and pymarkdown.
When creating new content, ensure to check if Markdown features work across all tools.
If not, add a corresponding pre-commit hook to prohibit addition and document the exception.

- Follow the [Local Dev Environment](../docs/meta/local_dev_environment.md) guidance.
- Ensure to run `prek` and respect linting and formatting as defined in [.pre-commit-config.yaml](../.pre-commit-config.yaml).

## Content Guidelines

- Follow the [Editing Conventions](../docs/meta/editing_conventions.md).
- When creating or editing content, prioritise creating a coherent, well-connected knowledge base whilst maintaining high standards of British English and technical accuracy.

### Language and Grammar

- Always use British English spelling and grammar conventions:
  - Use "ise" endings (e.g., "realise", "optimise", "organised")
  - Use "our" endings (e.g., "behaviour", "colour", "favour")
  - British punctuation (e.g., single quotes for emphasis, logical punctuation placement)
  - British terminology (e.g., "whilst" instead of "while", "amongst" instead of "among")
  - no Oxford Comma

### File Structure and Naming

- All content files must be in the `docs/` directory
- Use lowercase filenames with underscore for spaces (e.g., `some_file.md`)
- Store assets like `image.jpg` required for an entry `foo.md` in a subdirectory `foo/image.jpg`.

### Frontmatter Requirements

Every markdown file must start with YAML frontmatter containing at least a title:

```yaml
---
title: Your Document Title
---
```

### Internal Linking

- Always create meaningful cross-references to related content within the repository
- Use relative paths for internal links (e.g., `[some topic](../some_topic.md)`)
- Link to relevant concepts, related proposals, supporting rationales and background information
- Ensure links work correctly by checking the relative path structure
- When referencing concepts that have dedicated pages, always link to them

### Content Structure

- Use clear, descriptive headings (the `title` from the metadata will be rendered as heading, so use ## for main sections, ### for subsections)
- Include a brief summary or introduction for substantial documents
- Use bullet points for lists and structured information

### Formatting Guidelines

- Use _italics_ for emphasis of technical terms and concepts
- Use **bold** for strong emphasis and important action items
- Use `inline code` for file names and commands
- Use proper markdown syntax for lists, headings and links

### Technical Content

- Maintain consistency with existing technical terminology
- Reference specific technologies, tools and frameworks mentioned in other documents
- Ensure technical accuracy and alignment with team practices
- Include practical examples and implementation details where relevant

### Quality Standards

- All content should provide value
- Ensure information is current and actionable
- Write with the target audience in mind (technical professionals)
- Review content for clarity, completeness and usefulness
- Maintain consistency with existing content style and structure
