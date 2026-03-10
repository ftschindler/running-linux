# GitHub Copilot Instructions

This repository contains Felix' personal notes on running Linux in various circumstances.
It is implemented as a Quartz-based static site generator with markdown content in the `content/` directory.

## Technical Guidelines

- Make use of pre-commit, see [.pre-commit-config.yaml](../.pre-commit-config.yaml) for details.
- Follow the markdownlint and PyMarkdown configurations defined in [.markdownlint-cli2.jsonc](../.markdownlint-cli2.jsonc) and [.pymarkdown.json](../.pymarkdown.json) respectively.
- The site is built using Quartz, refer to the [README.md](../README.md) for further instructions.

## Content Guidelines

### Language and Grammar

- Always use British English spelling and grammar conventions:
  - Use "ise" endings (e.g., "realise", "optimise", "organised")
  - Use "our" endings (e.g., "behaviour", "colour", "favour")
  - British punctuation (e.g., single quotes for emphasis, logical punctuation placement)
  - British terminology (e.g., "whilst" instead of "while", "amongst" instead of "among")
  - no Oxford Comma

### File Structure and Naming

- All content files must be in the `content/` directory
- Use lowercase filenames with underscore for spaces (e.g., `some_file.md`)
- Store assets like `image.jpg` required for an entry `foo.md` in a subdirectory `foo/image.jpg`.

### Frontmatter Requirements

Every markdown file must start with YAML frontmatter containing at least a title:

```yaml
---
title: Your Document Title
---
```

It should be followed by links for discussion and editing, for example:

```markdown
> Edit this document [on Github](https://github.com/arup-group/ana-roadmap/edit/main/content/<path_to_file>)
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
